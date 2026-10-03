import os
import re
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from core import ROOT, METHODS, DEFAULT_MODEL, answer_question

load_dotenv(ROOT / ".env")


def main():
    required = ("GEMINI_API_KEY", "SLACK_BOT_TOKEN", "SLACK_APP_TOKEN")
    if any(not os.getenv(k) or "replace" in os.getenv(k, "") for k in required):
        raise SystemExit("Fill in the Gemini key and both Slack tokens in .env. See SETUP_GUIDE.md.")
    method = os.getenv("SLACK_METHOD", "vector")
    if method not in METHODS:
        raise SystemExit("SLACK_METHOD must be rules, full, or vector.")
    app = App(token=os.environ["SLACK_BOT_TOKEN"])

    @app.event("app_mention")
    def respond(event, say):
        question = re.sub(r"<@[A-Z0-9]+>", "", event.get("text", "")).strip()
        if not question:
            say(text="Mention me with a policy question, such as: How many vacation days do I receive?", thread_ts=event["ts"])
            return
        try:
            result = answer_question(method, question, os.environ["GEMINI_API_KEY"], os.getenv("GEMINI_MODEL", DEFAULT_MODEL))
            titles = "; ".join(result["policy_titles"]) or "No relevant policy identified"
            text = f"{result['answer']}\n\nPolicy: {titles}\nMethod: {METHODS[method]}"
        except (RuntimeError, ValueError) as exc:
            text = str(exc)
        # Plain text prevents model-generated Slack markup or mentions from being activated.
        say(text="PolicyBot response", blocks=[{"type": "section", "text": {"type": "plain_text", "text": text[:2900]}}], thread_ts=event["ts"])

    print("PolicyBot is running. Mention it in your testing channel. Press Ctrl+C to stop.")
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()


if __name__ == "__main__":
    main()
