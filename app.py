import json
import os
import statistics
from datetime import datetime, timezone
import streamlit as st
from dotenv import load_dotenv
from core import ROOT, METHODS, DEFAULT_MODEL, answer_question, policies, fingerprint, load_index

load_dotenv(ROOT / ".env")
st.set_page_config(page_title="Policy Lab | Anna Geckeler", page_icon="📚", layout="wide")


def setting(name, fallback=""):
    try:
        return st.secrets.get(name, os.getenv(name, fallback))
    except FileNotFoundError:
        return os.getenv(name, fallback)


def read_json(name, default):
    path = ROOT / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def metric(value):
    return "Not reported" if value is None else str(value)


def show_answer(result):
    if "error" in result:
        st.error(result["error"])
        return
    st.write(result["answer"])
    st.markdown("**Relevant policy:** " + ("; ".join(result["policy_titles"]) or "None identified"))
    st.caption(f"Response time: {result['response_seconds']:.4f} s")
    st.caption(f"LLM tokens — input: {metric(result['input_tokens'])} · output: {metric(result['output_tokens'])} · total: {metric(result['total_tokens'])}")
    st.caption(f"Query embedding tokens: {metric(result['embedding_tokens'])}")
    if result.get("unknown_citations"):
        st.warning("Citation not found in CSV: " + "; ".join(result["unknown_citations"]))
    if result.get("retrieved_policies"):
        with st.expander("Policies retrieved"):
            for title in result["retrieved_policies"]:
                st.write(title)


def run_one(method, question):
    try:
        return answer_question(method, question, setting("GEMINI_API_KEY"), setting("GEMINI_MODEL", DEFAULT_MODEL))
    except (RuntimeError, ValueError, KeyError) as exc:
        return {"method": method, "question": question, "error": str(exc)}


def summary_rows(results):
    table = []
    for method, label in METHODS.items():
        group = [r for r in results if r["method"] == method and "error" not in r]
        reviewed = [r for r in group if r.get("review_support") in ("Supported", "Unsupported")]
        correctness = [r for r in group if r.get("review_correct") in ("Correct", "Incorrect")]
        seconds = [r["response_seconds"] for r in group]
        tokens = [r["total_tokens"] for r in group if r.get("total_tokens") is not None]
        bad = sum(r["review_support"] == "Unsupported" for r in reviewed)
        correct = sum(r["review_correct"] == "Correct" for r in correctness)
        table.append({"Method": label, "Completed answers": len(group),
            "Mean seconds": round(statistics.mean(seconds), 4) if seconds else None,
            "Mean LLM tokens": round(statistics.mean(tokens), 1) if tokens else None,
            "Unsupported / reviewed": f"{bad}/{len(reviewed)}" if reviewed else "Not reviewed",
            "Correct / assessed": f"{correct}/{len(correctness)}" if correctness else "Not reviewed"})
    return table


st.caption("ANNA GECKELER · AI IN ACCOUNTING AND BUSINESS")
st.title("Company Policy Lab")
st.write("One policy database. Three ways to answer. Compare the evidence, speed and token use.")
tabs = st.tabs(["Ask a question", "Comparison & findings", "Run & review tests"])
questions = read_json("test_questions.json", [])

with tabs[0]:
    st.subheader("Ask about a company policy")
    with st.form("question"):
        question = st.text_input("Your question", "How many days per week may I work remotely?", max_chars=1500)
        submitted = st.form_submit_button("Compare all three methods", type="primary")
    if submitted and question.strip():
        st.session_state["answers"] = []
        with st.spinner("Finding policies and comparing answers…"):
            for method in METHODS:
                st.session_state["answers"].append(run_one(method, question))
    for col, method in zip(st.columns(3), METHODS):
        with col:
            st.subheader(METHODS[method])
            st.caption({"rules": "Keyword matching; returns the original policy text.", "full": "Gemini receives every policy.", "vector": "Gemini receives the three closest policy matches."}[method])
            for result in st.session_state.get("answers", []):
                if result["method"] == method:
                    show_answer(result)
    st.info("Unsupported-answer tendency is measured on the reviewed test set in Comparison & findings. A citation alone does not prove that an answer is supported.")

with tabs[1]:
    st.subheader("Measured comparison")
    saved = read_json("evaluation_results.json", {"results": []})
    results = saved.get("results", [])
    if results:
        if saved.get("policy_hash") != fingerprint(policies()):
            st.warning("These results refer to a different policy dataset. Rerun the tests before submitting.")
        st.caption("Saved evaluation: " + saved.get("exported_at", "unknown date"))
        st.dataframe(summary_rows(results), hide_index=True, width="stretch")
        complete = len(results) == 3 * len(questions) and all("error" not in r and r.get("review_support") in ("Supported", "Unsupported") and r.get("review_correct") in ("Correct", "Incorrect") for r in results)
        if not complete:
            st.warning("Evaluation is incomplete. Finish all methods and both review decisions for every question.")
        st.download_button("Download saved evaluation", json.dumps(saved, indent=2), "evaluation_results.json", "application/json")
        with st.expander("Inspect individual test answers"):
            for result in results:
                st.markdown(f"**{result.get('question_id', '')} · {METHODS[result['method']]}**")
                st.write(result["question"])
                show_answer(result)
                st.caption(f"Support: {result.get('review_support', 'Not reviewed')} · Correctness: {result.get('review_correct', 'Not reviewed')}")
                st.write(result.get("review_notes", ""))
    else:
        st.info("No measured results yet. Run the tests, review them, then upload the downloaded evaluation_results.json to the repository.")
    st.subheader("Two-paragraph comparison")
    comparison = (ROOT / "comparison.md").read_text(encoding="utf-8").strip()
    if "[" in comparison or len(comparison.split("\n\n")) != 2:
        st.warning("The comparison is a template. Replace the bracketed fields with your findings and keep exactly two paragraphs.")
    st.markdown(comparison)
    with st.expander("How the comparison works"):
        st.write("Both LLM approaches use the same generation model, instructions and temperature (0). The full-context method receives every row; the vector method retrieves the top three using cosine similarity over normalized Gemini embeddings. The rules method matches keywords, weights title matches three times, and returns one original policy statement.")
        st.write("Response time includes search/query embedding and generation, but excludes CSV/index loading and the one-time index build. LLM input, output and total counts come from Gemini; total may also include thinking tokens. Embedding token counts are shown separately when reported. Not reported means unavailable, not zero, and is excluded from LLM totals. A single run of ten questions is a small descriptive comparison, not a general performance guarantee.")
        st.caption("Generation model: " + setting("GEMINI_MODEL", DEFAULT_MODEL) + " · Embedding model: gemini-embedding-001 · Policy rows: " + str(len(policies())))
        try:
            index = load_index(policies())
            st.caption(f"One-time index setup: {index['setup_seconds']} s. Document embedding tokens: not reported by the endpoint.")
        except (RuntimeError, ValueError) as exc:
            st.caption(str(exc))

with tabs[2]:
    st.subheader("Run ten questions, then check the answers")
    st.write("Run one question at a time to keep free-tier use manageable. Each complete test uses two generation calls and one query-embedding call. Download your progress before closing the browser.")
    st.session_state.setdefault("evaluation", {})
    uploaded = st.file_uploader("Resume from a downloaded results file (optional)", type=["json"])
    if st.button("Load uploaded progress", disabled=uploaded is None):
        try:
            data = json.load(uploaded)
            if data["policy_hash"] != fingerprint(policies()):
                raise ValueError("Different policy dataset.")
            loaded = {}
            for r in data["results"]:
                if r["method"] not in METHODS or r["question_id"] not in {q["id"] for q in questions}:
                    raise ValueError("Unknown method or question.")
                loaded[r["question_id"] + r["method"]] = r
            st.session_state["evaluation"] = loaded
            for k in list(st.session_state):
                if k.startswith("review_"):
                    del st.session_state[k]
            st.success("Progress loaded.")
        except (ValueError, KeyError, TypeError):
            st.error("Invalid results file or different dataset. Use this app's downloaded JSON.")
    selected = st.selectbox("Test question", questions, format_func=lambda q: f"{q['id']} — {q['question']}")
    st.caption("Expected policy: " + (selected["expected_policy"] or "None"))
    st.write("Expected answer: " + selected["expected_answer"])
    if st.button("Run missing methods for this question", type="primary"):
        with st.spinner("Running test…"):
            for method in METHODS:
                result_key = selected["id"] + method
                previous = st.session_state["evaluation"].get(result_key)
                if not previous or "error" in previous:
                    result = run_one(method, selected["question"])
                    result.update(question_id=selected["id"], expected_policy=selected["expected_policy"], expected_answer=selected["expected_answer"], run_at=datetime.now(timezone.utc).isoformat())
                    st.session_state["evaluation"][result_key] = result
    st.caption("Supported = no invented policy claims. Correct = answers the question appropriately AND identifies the relevant policy. A copied but irrelevant policy can be supported yet incorrect. A suitable 'not specified' answer can be correct.")
    for method in METHODS:
        result_key = selected["id"] + method
        result = st.session_state["evaluation"].get(result_key)
        if result:
            st.markdown("**" + METHODS[method] + "**")
            show_answer(result)
            if "error" not in result:
                support = ["Not reviewed", "Supported", "Unsupported"]
                correct = ["Not reviewed", "Correct", "Incorrect"]
                result["review_support"] = st.selectbox("Are all policy claims supported by the CSV?", support, index=support.index(result.get("review_support", "Not reviewed")), key="review_support_" + result_key)
                result["review_correct"] = st.selectbox("Does it answer correctly and identify the right policy?", correct, index=correct.index(result.get("review_correct", "Not reviewed")), key="review_correct_" + result_key)
                result["review_notes"] = st.text_input("Brief reason for your assessment", result.get("review_notes", ""), key="review_notes_" + result_key)
    evaluation = list(st.session_state["evaluation"].values())
    if evaluation:
        st.dataframe(summary_rows(evaluation), hide_index=True, width="stretch")
        export = {"exported_at": datetime.now(timezone.utc).isoformat(), "policy_hash": fingerprint(policies()), "results": evaluation}
        st.download_button("Download results and review decisions", json.dumps(export, indent=2), "evaluation_results.json", "application/json", type="primary")
    with st.expander("Policy reference for manual review"):
        for row in policies():
            st.markdown("**" + row["title"] + "**")
            st.write(row["policy_text"])
