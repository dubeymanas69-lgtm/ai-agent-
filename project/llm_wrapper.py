import os
import json
import urllib.request
import urllib.error

LLM_API_URL = os.environ.get("LLM_API_URL")
LLM_API_KEY = os.environ.get("LLM_API_KEY")

def call_llm_system(prompt, max_tokens=512, temperature=0.0):
    if not LLM_API_URL or not LLM_API_KEY:
        return '{"action": "chat", "parameters": {"response": "Error: LLM_API_URL or LLM_API_KEY not set."}}'

    # Detect if using Google Gemini (generativelanguage.googleapis.com)
    is_google = "generativelanguage.googleapis.com" in LLM_API_URL
    
    if is_google:
        # Google Gemini REST API format
        # URL should be like: https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=API_KEY
        # But we usually pass key in header or query param. 
        # If user put key in env var, we might need to append it if not in URL.
        
        # Construct payload for Gemini
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }
        
        # Google API key is often passed as query param 'key', but can also be in header 'x-goog-api-key'
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": LLM_API_KEY
        }
        
    else:
        # Fallback to generic/OpenAI-like format (often used by local servers or proxies)
        # OpenAI Chat Completions format
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        # Some generic endpoints might still want "prompt", but "messages" is more standard now.
        # If this is a raw completion endpoint, it might fail. 
        # But let's try to be robust.
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLM_API_KEY}"
        }

    data = json.dumps(payload).encode("utf-8")
    
    try:
        req = urllib.request.Request(LLM_API_URL, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as res:
            resp_text = res.read().decode("utf-8")
            
        # Parse response to extract text
        resp_json = json.loads(resp_text)
        
        if is_google:
            # Extract from Gemini response
            # {"candidates": [{"content": {"parts": [{"text": "..."}]}}]}
            try:
                return resp_json["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                return json.dumps({"action": "chat", "parameters": {"response": "Error: Empty or invalid response from Gemini."}})
        else:
            # Extract from OpenAI-like response
            # {"choices": [{"message": {"content": "..."}}]}
            try:
                if "choices" in resp_json:
                    return resp_json["choices"][0]["message"]["content"]
                # Fallback if it returns raw text or other format
                return resp_text
            except (KeyError, IndexError):
                 return resp_text

    except urllib.error.URLError as e:
        return json.dumps({"action": "chat", "parameters": {"response": f"LLM API Error: {e}"}})
    except json.JSONDecodeError:
        return json.dumps({"action": "chat", "parameters": {"response": "Error: Invalid JSON response from API."}})
