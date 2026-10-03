import json
import unittest
from unittest.mock import patch
import core


class PolicyTests(unittest.TestCase):
    def test_csv_and_rules(self):
        rows = core.policies()
        self.assertGreater(len(rows), 90)
        result = core.answer_question("rules", "How many vacation days do employees receive?")
        self.assertEqual(result["policy_titles"], ["Vacation Policy"])
        self.assertIn("15", result["answer"])
        self.assertEqual(result["total_tokens"], 0)
        self.assertEqual(core.answer_question("rules", "zzzzzz")["policy_titles"], [])

    def test_validation(self):
        for question in ("", "x" * 1501):
            with self.assertRaises(ValueError):
                core.answer_question("rules", question)
        with self.assertRaises(ValueError):
            core.answer_question("other", "vacation")

    def test_generation_usage_and_unknown_citation_preserved(self):
        response = {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": json.dumps({"answer": "Unsupported", "policy_titles": ["Invented Policy"]})}]}}], "usageMetadata": {"promptTokenCount": 50, "candidatesTokenCount": 12, "totalTokenCount": 65, "thoughtsTokenCount": 3}}
        with patch.object(core, "api", return_value=response) as api:
            result = core.answer_question("full", "vacation", "dummy")
        self.assertEqual(result["unknown_citations"], ["Invented Policy"])
        self.assertEqual(result["total_tokens"], 65)
        self.assertEqual(result["thinking_tokens"], 3)
        payload = api.call_args.args[3]
        sent = json.loads(payload["contents"][0]["parts"][0]["text"])
        self.assertEqual(len(sent["policies"]), len(core.policies()))

    def test_vector_retrieves_three_and_separates_missing_embedding_usage(self):
        rows = core.policies()
        vectors = [[0.0] * 768 for _ in rows]
        for i, v in enumerate(vectors):
            v[0], v[1] = (1, 0) if rows[i]["title"] == "Vacation Policy" else (0, 1)
        fake_index = {"vectors": vectors}
        query_result = {"embedding": {"values": [1] + [0] * 767}}
        generated = {"answer": "15 days", "policy_titles": ["Vacation Policy"], "input_tokens": 30, "output_tokens": 5, "total_tokens": 35, "thinking_tokens": 0}
        with patch.object(core, "load_index", return_value=fake_index), patch.object(core, "api", return_value=query_result), patch.object(core, "generate", return_value=generated) as generate:
            result = core.answer_question("vector", "vacation", "dummy")
        self.assertEqual(result["retrieved_policies"][0], "Vacation Policy")
        self.assertEqual(len(generate.call_args.args[3]), 3)
        self.assertIsNone(result["embedding_tokens"])
        self.assertEqual(result["total_tokens"], 35)

    def test_truncated_generation_is_failure(self):
        with patch.object(core, "api", return_value={"candidates": [{"finishReason": "MAX_TOKENS"}]}):
            with self.assertRaises(RuntimeError):
                core.generate("dummy", core.DEFAULT_MODEL, "vacation", core.policies())

    def test_two_paragraph_template_and_expected_policies(self):
        comparison = (core.ROOT / "comparison.md").read_text(encoding="utf-8").strip()
        self.assertEqual(len(comparison.split("\n\n")), 2)
        titles = {r["title"] for r in core.policies()}
        questions = json.loads((core.ROOT / "test_questions.json").read_text())
        self.assertEqual(len(questions), 10)
        self.assertTrue(all(not q["expected_policy"] or q["expected_policy"] in titles for q in questions))


if __name__ == "__main__":
    unittest.main()
