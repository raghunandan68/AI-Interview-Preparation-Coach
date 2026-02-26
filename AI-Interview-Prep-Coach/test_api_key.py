from google import genai
import tomllib
import os

def test_api():
    try:
        # Streamlit secrets are usually in .streamlit/secrets.toml
        secrets_path = os.path.join(".streamlit", "secrets.toml")
        if not os.path.exists(secrets_path):
            print(f"Error: {secrets_path} not found.")
            return

        with open(secrets_path, "rb") as f:
            secrets = tomllib.load(f)
        
        api_key = secrets.get("GEMINI_API_KEY")
        if not api_key:
            print("Error: GEMINI_API_KEY not found in secrets.toml")
            return
            
        print(f"Testing with key: {api_key[:5]}...{api_key[-5:]}")
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Say 'API is working!'"
        )
        print(f"Success: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
