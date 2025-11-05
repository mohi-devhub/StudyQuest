import httpx
import os
import json
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

def sanitize_input(input_text: str):
    """
    Sanitizes user input to prevent prompt injection.
    """
    prompt_injection_phrases = [
        "ignore previous instructions",
        "ignore the above",
        "ignore the instructions above",
        "ignore your instructions",
        "ignore your previous instructions",
        "forget your instructions",
        "disregard your instructions",
        "ignore all previous instructions",
    ]
    for phrase in prompt_injection_phrases:
        if phrase in input_text.lower():
            raise ValueError("Prompt injection attempt detected.")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"


async def generate_notes(topic: str, model: str = "google/gemini-2.0-flash-exp:free") -> dict:
    """
    Generate study notes for a given topic using OpenRouter API.
    
    Args:
        topic: The topic to generate notes for
        model: The OpenRouter model ID to use
        
    Returns:
        dict with 'summary' and 'key_points' keys
    """
    sanitize_input(topic)
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    # Construct the prompt
    prompt = f"""Explain the topic "{topic}" in 5-7 concise bullet points for a beginner.

Format your response as JSON with this structure:
{{
  "summary": "A brief 1-2 sentence overview of the topic",
  "key_points": [
    "First key point...",
    "Second key point...",
    "Third key point...",
    "Fourth key point...",
    "Fifth key point..."
  ]
}}

Make sure each bullet point is clear, concise, and easy to understand for someone learning this topic for the first time."""
    
    # Prepare the API request
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",  # Optional, for rankings
        "X-Title": "StudyQuest"  # Optional, shows in rankings
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000,
        "response_format": {"type": "json_object"}  # Request JSON response
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                OPENROUTER_BASE_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # Parse the JSON content
            parsed_content = json.loads(content)
            
            return {
                "topic": topic,
                "summary": parsed_content.get("summary", ""),
                "key_points": parsed_content.get("key_points", [])
            }
            
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        raise Exception(f"OpenRouter API error: {e.response.status_code} - {error_detail}")
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
    except KeyError as e:
        raise Exception(f"Unexpected API response structure: missing {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to generate notes: {str(e)}")


async def generate_notes_with_fallback(topic: str) -> dict:
    """Try multiple models in order until one succeeds."""
    models = [
        "google/gemini-2.0-flash-exp:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        "meta-llama/llama-3.2-1b-instruct:free",
        "qwen/qwen-2.5-7b-instruct:free",
        "microsoft/phi-3-mini-128k-instruct:free"
    ]
    
    last_error = None
    
    for model in models:
        try:
            print(f"Trying model: {model}")
            result = await generate_notes(topic, model)
            print(f"✅ Model {model} succeeded!")
            return result
        except Exception as e:
            print(f"Model {model} failed: {str(e)}")
            last_error = e
            continue
    
    # If all models failed, raise the last error
    raise Exception(f"All models failed. Last error: {str(last_error)}")
