import os
import tomllib
from google import genai
from groq import Groq
import time

def verify_providers():
    secrets_path = os.path.join(".streamlit", "secrets.toml")
    if not os.path.exists(secrets_path):
        print("❌ secrets.toml not found")
        return

    with open(secrets_path, "rb") as f:
        secrets = tomllib.load(f)

    gemini_key = secrets.get("GEMINI_API_KEY")
    groq_key = secrets.get("GROQ_API_KEY")

    print("--- Provider Verification ---")

    # Verify Gemini
    if gemini_key:
        print(f"\n[Gemini] Testing key: {gemini_key[:5]}...")
        try:
            client = genai.Client(api_key=gemini_key)
            resp = client.models.generate_content(model="gemini-2.0-flash", contents="Test")
            print(f"PASS Gemini OK: {resp.text[:20]}...")
        except Exception as e:
            print(f"FAIL Gemini Failed: {e}")
    else:
        print("\nSKIP Gemini key missing")

    # Verify Groq
    if groq_key and groq_key != "paste_your_groq_key_here":
        print(f"\n[Groq] Testing key: {groq_key[:5]}...")
        try:
            client = Groq(api_key=groq_key)
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "Test"}]
            )
            print(f"PASS Groq OK: {resp.choices[0].message.content[:20]}...")
        except Exception as e:
            print(f"FAIL Groq Failed: {e}")
    else:
        print("\nSKIP Groq key missing or placeholder")

if __name__ == "__main__":
    verify_providers()
