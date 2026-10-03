# Company Policy Lab

A Streamlit comparison of keyword search, full-context Gemini and Gemini with vector retrieval, plus a local Slack bot. Prepared for Anna Geckeler's company-policy assignment.

**Start with [SETUP_GUIDE.md](SETUP_GUIDE.md).** It covers accounts, Windows setup, Gemini credentials, test review, GitHub, Streamlit deployment, Slack installation and the hand-ins.

## Files

- `app.py`: comparison website and manual evaluation workflow.
- `core.py`: shared policy engine and Gemini API calls.
- `prepare_index.py`: creates `policy_index.json` using Gemini embeddings.
- `slack_bot.py` and `slack_manifest.json`: local Slack integration.
- `test_questions.json`: ten questions with expected answers.
- `comparison.md`: exactly two paragraphs; replace all placeholders after testing.
- `company_policies.csv`, `ASSIGNMENT.md`: copies of the supplied reference files.
- `test_core.py`: offline checks using simulated API responses.
- `VERIFICATION.md`: what was and was not verified before delivery.

Generated later: `policy_index.json` and `evaluation_results.json`. Neither contains credentials. The website clearly labels missing results and unfinished writing; it never substitutes demo measurements.

Uses Python's standard library for Gemini REST calls and exact cosine search over a small saved vector index. No model training, paid vector database or permanent Slack hosting required. Dependencies are in `requirements.txt`.

Run offline checks with `python -m unittest -v test_core.py`. Run the site with `python -m streamlit run app.py` after following the setup guide.
