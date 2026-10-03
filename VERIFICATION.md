# Verification and remaining setup

Prepared on 29 September 2026.

## Offline checks

- Python compilation passed for the website, policy engine, index builder, Slack bot and core tests.
- Six core tests passed: CSV reading and keyword matching; input validation; generation usage and unknown citations; vector retrieval with a simulated query embedding; truncated-response handling; and the two-paragraph template/test-question references.
- Two Streamlit AppTest checks passed: initial page and three-method question flow; and review decisions persisting when switching between test questions. These checks use simulated answers, not real Gemini measurements.
- Tested with Python 3.14.7, Streamlit 1.64.0, Slack Bolt 1.30.0 and python-dotenv 1.2.3. The three direct dependencies are pinned to the tested versions.

## Not yet verified with live services

- No Gemini key was supplied, so live generation, embedding creation, current account quotas and model access have not been tested.
- No Slack tokens were supplied, so Slack installation and live bot replies have not been tested.
- The website has not been deployed, no GitHub repository has been created, and no invitation has been sent.
- There are no measured evaluation results or completed comparison conclusions yet. The provided comparison is explicitly a template.

Complete the setup guide, review actual results and capture the real Slack screenshot before submitting. The software tests do not substitute for the assignment's policy-answer evaluation.
