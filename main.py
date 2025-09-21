# updated_main.py
import os
from dotenv import load_dotenv

# ✅ Load environment variables first!
load_dotenv()

from supervisor.supervisor import run_supervisor   # now safe to import

def main():
    print("LangGraph Supervisor Demo (Modular Version)")
    print("NOTE: API keys must be set in .env as OPENROUTER_API_KEY.")

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("❌ OPENROUTER_API_KEY not found in environment. Check your .env file!")

    print(f"✅ Loaded OPENROUTER_API_KEY (length {len(api_key)} characters)")

    user_objective = input("Enter user objective: ")
    result = run_supervisor(user_objective)

    print("\nSupervisor finished. Summaries:\n")
    for s in result.get("summaries", []):
        print(s)

if __name__ == "__main__":
    main()
