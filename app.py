import os
import json
import requests

def chat_completion(messages):
    try:
        # Get environment variables
        api_url = os.environ.get("NILAI_API_URL", "https://nilai-a779.nillion.network")
        api_key = os.environ.get("NILAI_API_KEY", "Nillion2025")
        
        # Prepare the request
        url = f"{api_url}/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": "meta-llama/Llama-3.1-8B-Instruct",
            "messages": messages,
            "temperature": 0.2
        }
        
        # Make the API call
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Return the JSON response
        return response.json()
    
    except Exception as error:
        print(f"Chat error: {error}")
        return {"error": "Failed to process chat request"}
      
      
result = chat_completion([
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, who are you?"}
])
print(result)