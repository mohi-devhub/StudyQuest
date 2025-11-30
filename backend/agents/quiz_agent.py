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


async def generate_quiz(notes: str, num_questions: int = 5, model: str = None) -> dict:
    """
    Generate quiz questions from study notes using Google Gemini API.
    
    Args:
        notes: The study notes to generate questions from
        num_questions: Number of questions to generate (default 5)
        model: The Gemini model to use (defaults to GEMINI_MODEL env var)
        
    Returns:
        dict with 'questions' list containing quiz questions
    """
    sanitize_input(notes)
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    if not notes or not notes.strip():
        raise ValueError("Notes cannot be empty")
    
    model_name = model or GEMINI_MODEL
    
    # Construct the prompt
    prompt = f"""Based on the following study material, create {num_questions} multiple-choice questions to test understanding.

Study Material:
{notes}

Requirements:
1. Create exactly {num_questions} unique questions
2. Each question must have 4 options labeled A, B, C, and D
3. Each question must have exactly ONE correct answer
4. Questions should cover different aspects of the material
5. Questions should be clear and unambiguous
6. Include a brief explanation for the correct answer

Format your response as a JSON array with this exact structure:
[
  {{
    "question": "What is the main purpose of...",
    "options": [
      "A) First option",
      "B) Second option",
      "C) Third option",
      "D) Fourth option"
    ],
    "answer": "B",
    "explanation": "Brief explanation of why B is correct"
  }}
]

Make sure:
- The "answer" field contains only the letter (A, B, C, or D)
- Options are properly labeled with letters and parentheses
- Questions are diverse and not repetitive
- The JSON is valid and properly formatted"""
    
    try:
        # Initialize the model
        model_instance = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.8,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2000,
                "response_mime_type": "application/json"
            }
        )
        
        # Generate content
        response = model_instance.generate_content(prompt)
        
        # Parse the JSON content
        parsed_content = json.loads(response.text)
        
        # Handle both direct array and object with array
        if isinstance(parsed_content, list):
            questions = parsed_content
        elif isinstance(parsed_content, dict) and "questions" in parsed_content:
            questions = parsed_content["questions"]
        else:
            raise ValueError("Unexpected response format from AI")
        
        # Validate the questions
        validated_questions = validate_questions(questions, num_questions)
        
        return validated_questions
            
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")


def validate_questions(questions: List[Dict], expected_count: int) -> List[Dict]:
    """
    Validate and normalize quiz questions.
    
    Args:
        questions: List of question dictionaries
        expected_count: Expected number of questions
    
    Returns:
        list: Validated and normalized questions
    
    Raises:
        ValueError: If questions are invalid
    """
    if not questions:
        raise ValueError("No questions were generated")
    
    validated = []
    seen_questions = set()
    
    for i, q in enumerate(questions):
        # Check required fields
        if not all(key in q for key in ["question", "options", "answer"]):
            continue  # Skip invalid questions
        
        # Normalize the question
        question_text = q["question"].strip()
        
        # Check for uniqueness
        if question_text.lower() in seen_questions:
            continue  # Skip duplicate questions
        
        seen_questions.add(question_text.lower())
        
        # Validate options
        options = q["options"]
        if not isinstance(options, list) or len(options) != 4:
            continue  # Skip if not exactly 4 options
        
        # Normalize options
        normalized_options = []
        for opt in options:
            opt_str = str(opt).strip()
            # Ensure option has letter prefix
            if not any(opt_str.startswith(f"{letter})") or opt_str.startswith(f"{letter}.") 
                      for letter in ["A", "B", "C", "D"]):
                # Add letter prefix if missing
                letter = ["A", "B", "C", "D"][len(normalized_options)]
                opt_str = f"{letter}) {opt_str}"
            normalized_options.append(opt_str)
        
        # Validate answer
        answer = q["answer"].strip().upper()
        if answer not in ["A", "B", "C", "D"]:
            # Try to extract letter from answer
            for letter in ["A", "B", "C", "D"]:
                if letter in answer:
                    answer = letter
                    break
            else:
                continue  # Skip if no valid answer
        
        # Get explanation (optional)
        explanation = q.get("explanation", "").strip()
        
        validated.append({
            "question": question_text,
            "options": normalized_options,
            "answer": answer,
            "explanation": explanation
        })
        
        # Stop if we have enough questions
        if len(validated) >= expected_count:
            break
    
    if len(validated) < expected_count:
        raise ValueError(f"Only generated {len(validated)} valid questions, expected {expected_count}")
    
    return validated[:expected_count]


async def generate_quiz_with_fallback(notes: str, num_questions: int = 5) -> dict:
    """Try multiple Gemini models in order until one succeeds."""
    models = [
        "models/gemini-2.0-flash",
        "models/gemini-flash-latest",
        "models/gemini-pro-latest"
    ]
    
    last_error = None
    
    for model in models:
        try:
            logger.info("Attempting quiz generation with model", model=model, num_questions=num_questions)
            result = await generate_quiz(notes, num_questions, model)
            logger.info("Quiz generation succeeded", model=model, questions_generated=len(result))
            # Return as dict with 'questions' key for consistency
            return {"questions": result}
        except Exception as e:
            logger.warning("Model failed for quiz generation", model=model, error=str(e))
            last_error = e
            continue
    
    # If all models failed, raise the last error
    raise Exception(f"All models failed. Last error: {str(last_error)}")


async def generate_quiz_from_topic(topic: str, summary: str, key_points: List[str], num_questions: int = 5) -> List[Dict]:
    """
    Generate quiz from structured notes (topic, summary, key points).
    
    Args:
        topic: The topic name
        summary: Brief summary of the topic
        key_points: List of key points
        num_questions: Number of questions to generate
    
    Returns:
        list: List of question dictionaries
    """
    # Format the notes
    notes = f"Topic: {topic}\n\n"
    notes += f"Summary: {summary}\n\n"
    notes += "Key Points:\n"
    for i, point in enumerate(key_points, 1):
        notes += f"{i}. {point}\n"
    
    result = await generate_quiz_with_fallback(notes, num_questions)
    # Extract questions list from dict
    return result.get("questions", [])
