import google.generativeai as genai
import os
import json
from typing import Dict, List
from dotenv import load_dotenv
from utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

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

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash")

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


async def generate_notes(topic: str, model: str = None) -> dict:
    """
    Generate study notes for a given topic using Google Gemini API.
    
    Args:
        topic: The topic to generate notes for
        model: The Gemini model to use (defaults to GEMINI_MODEL env var)
        
    Returns:
        dict with 'summary' and 'key_points' keys
    """
    sanitize_input(topic)
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    model_name = model or GEMINI_MODEL
    
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
    
    try:
        # Initialize the model
        model_instance = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1000,
            }
        )
        
        # Generate content
        response = model_instance.generate_content(prompt)
        
        # Parse the JSON response - handle markdown code blocks
        response_text = response.text.strip()
        if response_text.startswith("```"):
            # Remove markdown code block markers
            lines = response_text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            response_text = "\n".join(lines)
        
        parsed_content = json.loads(response_text)
        
        return {
            "topic": topic,
            "summary": parsed_content.get("summary", ""),
            "key_points": parsed_content.get("key_points", [])
        }
            
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")


async def generate_notes_with_fallback(topic: str) -> dict:
    """Try multiple Gemini models in order until one succeeds."""
    models = [
        "models/gemini-2.0-flash",
        "models/gemini-flash-latest",
        "models/gemini-pro-latest"
    ]
    
    last_error = None
    
    for model in models:
        try:
            logger.info("Attempting note generation with model", model=model, topic=topic)
            result = await generate_notes(topic, model)
            logger.info("Note generation succeeded", model=model, topic=topic, key_points_count=len(result.get('key_points', [])))
            return result
        except Exception as e:
            logger.warning("Model failed for note generation", model=model, topic=topic, error=str(e))
            last_error = e
            continue
    
    # If all models failed, raise the last error
    raise Exception(f"All models failed. Last error: {str(last_error)}")
