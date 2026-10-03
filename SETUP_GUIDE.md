# Policy assignment: step-by-step setup

This folder contains the website, three answering methods, a Slack bot, ten test questions and a two-paragraph comparison template. Your original files are unchanged. **No live AI results have been invented.** You still need your accounts and credentials, actual test runs, deployment, and the Slack screenshot.

## 1. Prepare your accounts

1. Create or sign in to [GitHub](https://github.com/).
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) and connect GitHub.
3. Open [Google AI Studio's API keys page](https://aistudio.google.com/api-keys), sign in with Google, and create a Gemini API key. Keep it private.
4. Create a separate [Slack workspace](https://slack.com/create), named **Anna Geckeler – Policies Assignment**, and a channel named **anna-policy-testing**.

The project uses `gemini-embedding-001` for embeddings and `gemini-2.5-flash-lite` for writing answers. Google introduced the embedding model with [free access](https://developers.googleblog.com/en/gemini-embedding-available-gemini-api/), and Flash-Lite has a free tier. Availability and quotas depend on your account; verify both in AI Studio and check [current pricing](https://ai.google.dev/gemini-api/docs/pricing) before running. Do not enable paid billing just to follow this guide. A paid Gemini chat subscription is not needed. If your lecturer requires another embedding model, the embedding code needs adapting before you build the index; do not merely rename it.

## 2. Put the project in an easy-to-find folder

Extract `policy-assistant.zip` somewhere convenient, for example your Documents folder. Open the extracted **policy-assistant** folder. You should see `app.py`, `core.py`, `requirements.txt` and the CSV directly inside it.

Install [Python](https://www.python.org/downloads/) if needed; Python 3.12 or newer is recommended. On Windows, enable the installer's PATH option if offered.

In File Explorer, open the project folder, right-click an empty area and choose **Open in Terminal**. Run these lines one at a time:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

If `py` is not recognized but `python` works, replace `py` with `python` in the first command. No environment activation or PowerShell policy changes are needed.

In Notepad, replace `replace_with_your_key` on the `GEMINI_API_KEY` line with your actual key. Leave the Slack placeholders for now. Save and close Notepad. The filename must be **.env**, not `.env.txt`; enable **View → Show → File name extensions** in File Explorer to check.

Never upload `.env`, `.streamlit/secrets.toml` or your `.venv` folder to GitHub. The supplied `.gitignore` excludes them when using Git, but browser uploads still require you to choose files carefully.

## 3. Build the vector index once

In the same terminal, run:

```powershell
.\.venv\Scripts\python.exe prepare_index.py
```

This sends the policy records to Gemini's embedding model and saves `policy_index.json`. It is a small local vector index, so no vector-database account is needed. Keep this generated file and upload it with the code later. The app reuses it instead of embedding all policies for every question. Rebuild only if the CSV or embedding implementation changes.

If you see a quota/rate-limit message, wait and try again. Free-tier daily limits may require waiting until the quota resets. Existing completed indexes are only replaced after a successful build.

## 4. Open your website locally

Run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Your browser should open. Otherwise open [localhost:8501](http://localhost:8501). Keep the terminal running; press Ctrl+C when you want to stop it.

In **Ask a question**, try **How many days per week may I work remotely?** Click **Compare all three methods**. You should see three answers, policy titles, response times and token counts.

Rules-based search needs no Gemini key. Both LLM methods need it; the vector method also needs `policy_index.json`. Missing setup produces an explanatory message instead of fabricated output.

## 5. Run and review the assignment comparison

1. Open **Run & review tests**.
2. Select Q01 and click **Run missing methods for this question**.
3. Read each answer against the expected answer and original policy reference.
4. For each method, select **Supported** or **Unsupported**, then **Correct** or **Incorrect**. Add a short reason.
5. Repeat for Q02–Q10. Pause between questions if your API rate limit requires it. The test set needs 20 successful generation calls plus 10 query-embedding calls in total; this may span more than one day on your free tier.
6. Click **Download results and review decisions** regularly. The browser session is temporary. To resume later, upload that JSON file, click **Load uploaded progress**, and continue. The run button skips successful answers, so it retries only missing or failed methods.
7. After all **30 answers** have both review decisions, put the downloaded file in the project folder with the exact name **evaluation_results.json**. Replace any older copy deliberately. Refresh the website: **Comparison & findings** now displays the saved results.

**How to judge:** An unsupported answer invents a claim not found in the CSV, such as a home-office allowance of $500. An answer can quote a real policy and still be incorrect because it does not answer the question or cites the wrong policy. For missing information, explicitly saying the amount is not specified can be correct. Score against these assignment records, not real-world policy or legal knowledge. Check every answer yourself; model citations are not evidence that all claims are supported.

The summary separates unsupported answers from overall correctness and displays the number actually reviewed. Incomplete or failed runs must not be reported as 0 hallucinations. Token fields marked **Not reported** are unavailable, not zero. The embedding endpoint normally does not supply token counts, so embedding usage is disclosed separately instead of being guessed or included in LLM totals. The saved results retain individual input, output, total and thinking token counts, model names, timestamps and retrieved policy titles.

The same generation model and instructions are used for both LLM methods. Timing includes the query search/embedding and answer generation, but excludes loading the CSV/index and the one-time index build. Questions are run in a fixed order and only once per successful method; discuss this small test's limits rather than making broad statistical claims. Use one generation model throughout the final test set; if you change it, start a fresh complete evaluation.

## 6. Finish the two-paragraph comparison

Open **comparison.md** in a text editor. Replace every bracketed placeholder with actual values and your conclusions. The mean times and LLM token totals appear in the evaluation summary. The index setup time appears under **How the comparison works**.

Keep **exactly two paragraphs**, separated by one blank line. The supplied template already has two. Choose the preferred method based on your results. Do not claim the vector method was best unless the results support that conclusion. The website includes two summary tables across its tabs; do not add more comparison tables. Refresh the site and confirm the template warning disappears.

## 7. Upload the project to GitHub

For the simplest browser workflow:

1. On GitHub, select **New repository** and name it **policy-assistant**. A public repository is easiest for the lecturer to access; it should contain only this assignment's non-secret files.
2. Create it, then choose **uploading an existing file** (or **Add file → Upload files**).
3. Upload these files directly into the repository's top level:
   - `app.py`, `core.py`, `prepare_index.py`, `slack_bot.py`
   - `requirements.txt`, `.gitignore`, `.env.example`
   - `company_policies.csv`, `ASSIGNMENT.md`, `test_questions.json`
   - `policy_index.json`, `evaluation_results.json`, `comparison.md`
   - `slack_manifest.json`, `README.md`, `SETUP_GUIDE.md`, `VERIFICATION.md`, `test_core.py`, `test_app.py`
4. Optionally upload the `.streamlit` folder containing **only** `config.toml` and `secrets.toml.example`. This gives the website its green theme. It contains no real keys in the supplied project.
5. Click **Commit changes**. Save the repository link for your hand-in.

Do not upload the entire working folder after setup: it now contains your private `.env` and a large `.venv`. Select only the files above. If you accidentally expose a real API key or Slack token, revoke and replace it; simply deleting the visible file is not enough.

## 8. Deploy on Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/) and choose **Create app**.
2. Select your GitHub repository and its branch (usually `main`).
3. Set the main file to **app.py**. In advanced settings, use Python **3.12** if a version choice is available.
4. In the app's **Secrets** settings, enter:

```toml
GEMINI_API_KEY = "your_actual_key"
GEMINI_MODEL = "gemini-2.5-flash-lite"
```

5. Deploy the app. Do not add Slack tokens to Streamlit; the Slack bot runs locally.
6. Open the resulting website link, try a question, and check that **Comparison & findings** includes your saved evaluation and finished two-paragraph comparison.
7. Confirm the lecturer can access the app and repository. Save the deployed website link for submission.

If you publish before finishing your evaluation, upload the final `evaluation_results.json` and `comparison.md` to the repository afterward and wait for the updated deployment. Results downloaded from the website do not automatically write to GitHub.

Official instructions: [Streamlit deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) and [secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).

## 9. Create the Slack app

1. Visit [Slack app management](https://api.slack.com/apps), sign in, and choose **Create New App → From a manifest**.
2. Select your separate assignment workspace.
3. Select the **JSON** format if offered, then paste the contents of **slack_manifest.json**. Review and create the app.
4. Open **Basic Information → App-Level Tokens → Generate Token and Scopes**. Name the token `local-connection`, add **connections:write**, and generate it. Copy the token beginning **xapp-** into `SLACK_APP_TOKEN` in your local `.env` file.
5. Open **OAuth & Permissions → Install to Workspace** and authorize it. Copy the **Bot User OAuth Token**, beginning **xoxb-**, into `SLACK_BOT_TOKEN` in `.env`.
6. Check that **Socket Mode** is enabled, and **Event Subscriptions** includes **app_mention**. The manifest configures these plus the **app_mentions:read** and **chat:write** bot permissions. If you change permissions afterward, reinstall the app to the workspace.
7. In your Slack testing channel, add PolicyBot using the channel's **Integrations → Add apps** option or `/invite @PolicyBot`.

No separate Slack developer account is needed; use your Slack login. Socket Mode connects from your computer, so you do not need a public bot server or a request URL. [Slack's setup guide](https://docs.slack.dev/tools/bolt-python/creating-an-app/)

## 10. Run the bot, invite your lecturer, and capture the screenshot

In `.env`, set `SLACK_METHOD` to your preferred approach: `rules`, `full`, or `vector`. The supplied default is `vector`; this is a starting configuration, not a claim that it wins your evaluation.

Open a **second terminal in the project folder** and run:

```powershell
.\.venv\Scripts\python.exe slack_bot.py
```

Keep it running. In the testing channel, type:

```text
@PolicyBot How many days per week may I work remotely?
```

Select the actual PolicyBot mention from Slack's suggestions. Open the reply thread and verify that it gives the answer and policy title. Capture a screenshot showing your channel name, the bot mention/question and the full reply. Use Windows **Win+Shift+S** and save the screenshot.

Invite **raz@sdu.dk** to the workspace and ensure the invitation includes **anna-policy-testing** (or add the lecturer to that channel once they join). This invitation is a required assignment outcome. The app files do not send it for you.

The bot stops responding when its terminal closes or your computer sleeps. Permanent hosting is not required by the assignment; run it again when demonstrating it.

## 11. Final hand-in checklist

- [ ] Deployed website link works and compares all three methods.
- [ ] Each method shows its answer, relevant policy, response time and token use.
- [ ] All 30 test answers have been checked; unsupported-answer tendency is visible.
- [ ] Exactly two completed comparison paragraphs explain the findings and preferred method; no more than two tables.
- [ ] Source-code repository link is accessible to the lecturer.
- [ ] Separate Slack workspace and testing channel identify you.
- [ ] Lecturer invited at **raz@sdu.dk**, including access to the testing channel.
- [ ] Screenshot shows the bot being called and answering with a policy reference.
- [ ] Submit the website link, two-paragraph comparison, repository link and screenshot.

## Quick troubleshooting

- **429/quota error:** Wait and retry. Save your test progress. Check daily limits in AI Studio; using the free tier does not mean unlimited calls.
- **Missing/invalid key:** Check `.env` locally or Streamlit Secrets online. Restart the local process after changing `.env`.
- **Missing/stale index:** Rerun `prepare_index.py` and upload the new `policy_index.json`.
- **Model unavailable:** Check available models in AI Studio; change `GEMINI_MODEL` in both `.env` and Streamlit Secrets. Rerun your evaluation consistently if the model changes.
- **Bot silent:** Check its terminal, both tokens, app installation, channel membership and the actual @mention. Verify Socket Mode and the `app_mention` subscription.
- **Website still shows placeholders:** Edit `comparison.md`, upload it, and wait for redeployment.

## Short glossary

- **LLM:** AI model that writes answers.
- **Embedding:** A list of numbers representing text meaning.
- **Vector index:** Saved embeddings that can be searched for similar meanings.
- **RAG:** Retrieval-augmented generation: find relevant policies, then let the LLM answer using them.
- **API key / token:** A private credential allowing code to use a service. Slack access tokens are different from the text tokens counted for AI usage.
- **LLM tokens:** Pieces of text processed/generated by the model.
- **Repository:** The project files stored on GitHub.
- **Deployment:** Publishing the website so others can open its link.
- **Socket Mode:** A connection allowing your locally running bot to receive Slack events.

Prepared 29 September 2026. Service interfaces and model availability can change; follow the linked official documentation if labels differ.
