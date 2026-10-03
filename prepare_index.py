from dotenv import load_dotenv
import os
from core import ROOT, build_index

if __name__ == "__main__":
    load_dotenv(ROOT / ".env")
    print("Creating policy embeddings using Gemini. Existing index is replaced only after success.")
    try:
        index = build_index(os.getenv("GEMINI_API_KEY", ""), lambda done, total: print(f"{done}/{total} policies embedded"))
        print(f"Saved policy_index.json. Setup took {index['setup_seconds']} seconds.")
    except (RuntimeError, ValueError) as exc:
        raise SystemExit(str(exc))
