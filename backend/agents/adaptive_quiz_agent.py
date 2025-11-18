"""
Adaptive Quiz Agent - Adjusts quiz difficulty based on user performance
Uses past quiz data from Supabase to personalize difficulty
"""

import httpx
import os
import json
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from utils.logger import get_logger
from utils.ai_cache import get_quiz_cache

load_dotenv()

logger = get_logger(__name__)
quiz_cache = get_quiz_cache()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"


class AdaptiveQuizAgent:
    """
    Generates adaptive quizzes based on user performance and difficulty preferences.
    
    Difficulty Levels:
    - easy: Basic recall and understanding
    - medium: Application and analysis
    - hard: Advanced synthesis and evaluation
    - expert: Complex problem-solving and critical thinking
    """
    
    # Difficulty adjustment thresholds
    INCREASE_THRESHOLD = 80  # If score > 80%, increase difficulty
    DECREASE_THRESHOLD = 50  # If score < 50%, decrease difficulty
    
    # Difficulty progression
    DIFFICULTY_LEVELS = ['easy', 'medium', 'hard', 'expert']
    
    # Model preferences for different difficulties
    MODELS = {
        'primary': "google/gemini-2.0-flash-exp:free",
        'fallback': [
            "meta-llama/llama-3.2-3b-instruct:free",
            "meta-llama/llama-3.2-1b-instruct:free",
            "qwen/qwen-2.5-7b-instruct:free"
        ]
    }
    
    @staticmethod
    def determine_next_difficulty(
        current_difficulty: Optional[str],
        avg_score: Optional[float],
        user_preference: Optional[str] = None
    ) -> str:
        """
        Determine the next quiz difficulty based on performance.
        
        Logic:
        - If score > 80% → increase difficulty (unless already at max)
        - If score < 50% → decrease difficulty (unless already at min)
        - If user has preference, respect it (but suggest based on performance)
        
        Args:
            current_difficulty: Current difficulty level (None for new users)
            avg_score: User's average score (0-100, None for new users)
            user_preference: User's preferred difficulty (optional)
            
        Returns:
            Next difficulty level as string
        """
        # Respect user preference if provided and valid
        if user_preference and user_preference.lower() in AdaptiveQuizAgent.DIFFICULTY_LEVELS:
            return user_preference.lower()
        
        # Default to medium for new users or missing data
        if current_difficulty is None or avg_score is None:
            return 'medium'
        
        # Get current difficulty index
        try:
            current_idx = AdaptiveQuizAgent.DIFFICULTY_LEVELS.index(current_difficulty.lower())
        except (ValueError, AttributeError):
            current_idx = 1  # Default to medium if invalid
        
        # Adjust based on score
        if avg_score >= AdaptiveQuizAgent.INCREASE_THRESHOLD:
            # Increase difficulty if not already at max
            next_idx = min(current_idx + 1, len(AdaptiveQuizAgent.DIFFICULTY_LEVELS) - 1)
            new_difficulty = AdaptiveQuizAgent.DIFFICULTY_LEVELS[next_idx]
            return new_difficulty
        elif avg_score < AdaptiveQuizAgent.DECREASE_THRESHOLD:
            # Decrease difficulty if not already at min
            next_idx = max(current_idx - 1, 0)
            new_difficulty = AdaptiveQuizAgent.DIFFICULTY_LEVELS[next_idx]
            return new_difficulty
        else:
            # Maintain current difficulty
            return current_difficulty.lower()
    
    @staticmethod
    def get_difficulty_context(difficulty: str) -> Dict:
        """
        Get contextual information for quiz generation based on difficulty.
        
        Returns:
            Dictionary with difficulty-specific prompts and parameters
        """
        contexts = {
            'easy': {
                'temperature': 0.6,
                'cognitive_level': 'remembering and understanding',
                'question_types': ['recall', 'definition', 'basic concepts'],
                'description': 'beginner-friendly with basic recall questions',
                'question_style': 'straightforward, clear definitions, basic concepts',
                'complexity': 'simple vocabulary, direct questions',
                'hints': 'include helpful hints in questions',
                'context_prompt': 'Focus on basic recall and foundational understanding'
            },
            'medium': {
                'temperature': 0.7,
                'cognitive_level': 'applying and analyzing',
                'question_types': ['application', 'analysis', 'scenarios'],
                'description': 'standard difficulty with application-based questions',
                'question_style': 'scenario-based, requiring application of concepts',
                'complexity': 'moderate vocabulary, some inference needed',
                'hints': 'minimal hints, focus on understanding',
                'context_prompt': 'Focus on applying concepts to scenarios'
            },
            'hard': {
                'temperature': 0.8,
                'cognitive_level': 'evaluating and creating',
                'question_types': ['evaluation', 'synthesis', 'comparison'],
                'description': 'advanced with synthesis and evaluation questions',
                'question_style': 'complex scenarios, comparing concepts, evaluating solutions',
                'complexity': 'advanced vocabulary, multi-step reasoning',
                'hints': 'no hints, test deep understanding',
                'context_prompt': 'Focus on evaluating solutions and synthesizing concepts'
            },
            'expert': {
                'temperature': 0.85,
                'cognitive_level': 'analyzing complex systems and creating solutions',
                'question_types': ['problem-solving', 'critical thinking', 'edge cases'],
                'description': 'expert-level with critical thinking and problem-solving',
                'question_style': 'real-world problems, edge cases, advanced applications',
                'complexity': 'technical terminology, requires synthesis of multiple concepts',
                'hints': 'no hints, expect mastery-level knowledge',
                'context_prompt': 'Focus on complex problem-solving and mastery-level understanding'
            }
        }
        
        return contexts.get(difficulty.lower(), contexts['medium'])
    
    @staticmethod
    async def generate_adaptive_quiz(
        notes: str,
        difficulty: str = 'medium',
        num_questions: int = 5,
        user_context: Optional[Dict] = None
    ) -> Dict:
        """
        Generate an adaptive quiz with difficulty-appropriate questions.
        
        Args:
            notes: Study material to generate questions from
            difficulty: Difficulty level (easy, medium, hard, expert)
            num_questions: Number of questions to generate
            user_context: Optional user performance context
            
        Returns:
            Dictionary with questions and metadata
        """
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        if not notes or not notes.strip():
            raise ValueError("Notes cannot be empty")
        
        # Check cache first
        cache_key_params = {
            'difficulty': difficulty,
            'num_questions': num_questions
        }
        cached_response = quiz_cache.get(
            notes,
            AdaptiveQuizAgent.MODELS['primary'],
            **cache_key_params
        )
        
        if cached_response:
            logger.info(
                "Quiz retrieved from cache",
                difficulty=difficulty,
                num_questions=num_questions,
                cache_hit=True
            )
            return cached_response
        
        # Get difficulty context
        diff_context = AdaptiveQuizAgent.get_difficulty_context(difficulty)
        
        # Build adaptive prompt
        prompt = f"""Based on the following study material, create {num_questions} multiple-choice questions at {difficulty.upper()} difficulty level.

Study Material:
{notes}

Difficulty Level: {difficulty.upper()}
- Description: {diff_context['description']}
- Cognitive Level: {diff_context['cognitive_level']}
- Question Style: {diff_context['question_style']}
- Complexity: {diff_context['complexity']}
- Guidance: {diff_context['hints']}

Requirements:
1. Create exactly {num_questions} unique questions appropriate for {difficulty} level
2. Each question must have 4 options labeled A, B, C, and D
3. Each question must have exactly ONE correct answer
4. Questions should match the {difficulty} difficulty level in complexity
5. For {difficulty} level, focus on {diff_context['cognitive_level']}
6. Use {diff_context['question_style']} approach
7. Include a detailed explanation for the correct answer
8. Ensure questions are progressively challenging within the {difficulty} level

Format your response as a JSON object with this exact structure:
{{
  "difficulty": "{difficulty}",
  "questions": [
    {{
      "question": "Question text here...",
      "options": [
        "A) First option",
        "B) Second option",
        "C) Third option",
        "D) Fourth option"
      ],
      "answer": "B",
      "explanation": "Detailed explanation of why B is correct and why others are wrong",
      "difficulty_rating": "{difficulty}"
    }}
  ]
}}

Make sure:
- Questions are appropriate for {difficulty} difficulty
- The "answer" field contains only the letter (A, B, C, or D)
- Options are properly labeled with letters and parentheses
- Questions test {diff_context['cognitive_level']}
- Explanations are thorough and educational
- The JSON is valid and properly formatted"""
        
        # Prepare the API request
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "StudyQuest Adaptive Quiz"
        }
        
        # Get temperature from difficulty context
        temperature = diff_context.get('temperature', 0.7)
        
        payload = {
            "model": AdaptiveQuizAgent.MODELS['primary'],
            "messages": [
                {
                    "role": "system",
                    "content": f"You are an expert educational content creator specializing in {difficulty}-level quiz questions. Generate questions that accurately reflect {difficulty} difficulty."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": 2500,
            "response_format": {"type": "json_object"}
        }
        
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
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
                
                # Extract questions
                if "questions" in parsed_content:
                    questions = parsed_content["questions"]
                elif isinstance(parsed_content, list):
                    questions = parsed_content
                else:
                    raise ValueError("Unexpected response format from AI")
                
                # Validate questions
                validated_questions = AdaptiveQuizAgent._validate_adaptive_questions(
                    questions, num_questions, difficulty
                )
                
                result = {
                    "difficulty": difficulty,
                    "questions": validated_questions,
                    "metadata": {
                        "model": AdaptiveQuizAgent.MODELS['primary'],
                        "cognitive_level": diff_context['cognitive_level'],
                        "generated_count": len(validated_questions),
                        "cached": False
                    }
                }
                
                # Cache the result
                quiz_cache.set(
                    notes,
                    AdaptiveQuizAgent.MODELS['primary'],
                    result,
                    **cache_key_params
                )
                
                logger.info(
                    "Quiz generated and cached",
                    difficulty=difficulty,
                    num_questions=num_questions,
                    cache_hit=False
                )
                
                return result
                
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            raise Exception(f"OpenRouter API error: {e.response.status_code} - {error_detail}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to generate adaptive quiz: {str(e)}")
    
    @staticmethod
    def _validate_adaptive_questions(
        questions: List[Dict],
        expected_count: int,
        difficulty: str
    ) -> List[Dict]:
        """
        Validate and normalize adaptive quiz questions.
        
        Args:
            questions: List of question dictionaries
            expected_count: Expected number of questions
            difficulty: Expected difficulty level
        
        Returns:
            List of validated questions
        """
        if not questions:
            raise ValueError("No questions were generated")
        
        validated = []
        seen_questions = set()
        
        for q in questions:
            # Check required fields
            if not all(key in q for key in ["question", "options", "answer"]):
                continue
            
            question_text = q["question"].strip()
            
            # Check for uniqueness
            if question_text.lower() in seen_questions:
                continue
            
            seen_questions.add(question_text.lower())
            
            # Validate options
            options = q["options"]
            if not isinstance(options, list) or len(options) != 4:
                continue
            
            # Normalize options
            normalized_options = []
            for idx, opt in enumerate(options):
                opt_str = str(opt).strip()
                # Ensure option has letter prefix
                if not any(opt_str.startswith(f"{letter})") or opt_str.startswith(f"{letter}.")
                          for letter in ["A", "B", "C", "D"]):
                    letter = ["A", "B", "C", "D"][idx]
                    opt_str = f"{letter}) {opt_str}"
                normalized_options.append(opt_str)
            
            # Validate answer
            answer = q["answer"].strip().upper()
            if answer not in ["A", "B", "C", "D"]:
                for letter in ["A", "B", "C", "D"]:
                    if letter in answer:
                        answer = letter
                        break
                else:
                    continue
            
            # Get explanation
            explanation = q.get("explanation", "").strip()
            
            validated.append({
                "question": question_text,
                "options": normalized_options,
                "answer": answer,
                "explanation": explanation,
                "difficulty": difficulty
            })
            
            if len(validated) >= expected_count:
                break
        
        if len(validated) < expected_count:
            raise ValueError(f"Only generated {len(validated)} valid questions, expected {expected_count}")
        
        return validated[:expected_count]
    
    @staticmethod
    async def generate_adaptive_quiz_with_fallback(
        notes: str,
        difficulty: str = 'medium',
        num_questions: int = 5,
        user_context: Optional[Dict] = None
    ) -> Dict:
        """
        Generate adaptive quiz with model fallback.
        
        Tries primary model first, then falls back to alternative models.
        """
        models = [AdaptiveQuizAgent.MODELS['primary']] + AdaptiveQuizAgent.MODELS['fallback']
        
        last_error = None
        
        for model in models:
            try:
                logger.info("Attempting quiz generation with model", model=model, difficulty=difficulty, num_questions=num_questions)
                # Temporarily set the model
                original_model = AdaptiveQuizAgent.MODELS['primary']
                AdaptiveQuizAgent.MODELS['primary'] = model
                
                result = await AdaptiveQuizAgent.generate_adaptive_quiz(
                    notes, difficulty, num_questions, user_context
                )
                
                # Restore original model
                AdaptiveQuizAgent.MODELS['primary'] = original_model
                
                logger.info("Quiz generation succeeded", model=model, difficulty=difficulty, questions_generated=len(result.get('questions', [])))
                return result
                
            except Exception as e:
                logger.warning("Model failed for quiz generation", model=model, difficulty=difficulty, error=str(e))
                last_error = e
                # Restore original model before trying next
                AdaptiveQuizAgent.MODELS['primary'] = original_model
                continue
        
        raise Exception(f"All models failed. Last error: {str(last_error)}")
    
    @staticmethod
    @staticmethod
    def get_difficulty_recommendation(
        avg_score: Optional[float],
        current_difficulty: Optional[str],
        recommended_difficulty: str,
        total_attempts: int
    ) -> str:
        """
        Get a difficulty recommendation with reasoning.
        
        Returns:
            String explanation of the difficulty recommendation
        """
        reasons = []
        
        # New user
        if avg_score is None or current_difficulty is None:
            return f"Welcome! Starting at {recommended_difficulty} difficulty. We'll adjust based on your performance."
        
        if avg_score >= AdaptiveQuizAgent.INCREASE_THRESHOLD and recommended_difficulty != current_difficulty:
            reasons.append(f"Your average score of {avg_score:.1f}% shows strong mastery.")
            reasons.append(f"Ready to challenge yourself at {recommended_difficulty} level.")
        elif avg_score < AdaptiveQuizAgent.DECREASE_THRESHOLD and recommended_difficulty != current_difficulty:
            reasons.append(f"Your average score of {avg_score:.1f}% suggests you need more practice.")
            reasons.append(f"Trying {recommended_difficulty} level will help build confidence.")
        else:
            reasons.append(f"Your score of {avg_score:.1f}% is in the optimal range.")
            reasons.append(f"Continue at {recommended_difficulty} level to solidify understanding.")
        
        if total_attempts < 3:
            reasons.append("Complete more quizzes for better difficulty calibration.")
        
        return " ".join(reasons)

