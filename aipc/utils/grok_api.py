import os
import requests

def call_grok_api(messages, temperature=0.7):
    """
    Helper function to call Groq Cloud API (Llama3 model). 
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise Exception("GROQ_API_KEY not found in environment variables. Please check your .env file.")
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile", 
        "messages": messages,
        "temperature": temperature
    }
    
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        error_details = ""
        if 'response' in locals() and hasattr(response, 'text'):
            error_details = response.text
        return f"Error generating response from AI. Exception: {str(e)} | Details: {error_details}"
