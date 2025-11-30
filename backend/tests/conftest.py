import pytest
import httpx
import json

@pytest.fixture
def mock_httpx_client(mocker):
    """
    Fixture to mock httpx.AsyncClient and its post method.
    """
    mock_response = httpx.Response(
        200,
        json={
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "difficulty": "easy",
                            "questions": [
                                {
                                    "question": "What is 2 + 2?",
                                    "options": ["A) 3", "B) 4", "C) 5", "D) 6"],
                                    "answer": "B",
                                    "explanation": "Because 2 + 2 = 4",
                                    "difficulty_rating": "easy"
                                },
                                {
                                    "question": "What is the capital of France?",
                                    "options": ["A) London", "B) Paris", "C) Berlin", "D) Madrid"],
                                    "answer": "B",
                                    "explanation": "Paris is the capital of France.",
                                    "difficulty_rating": "easy"
                                },
                                {
                                    "question": "What is the color of the sky?",
                                    "options": ["A) Green", "B) Blue", "C) Red", "D) Yellow"],
                                    "answer": "B",
                                    "explanation": "The sky is blue.",
                                    "difficulty_rating": "easy"
                                },
                                {
                                    "question": "What is the largest planet in our solar system?",
                                    "options": ["A) Earth", "B) Jupiter", "C) Mars", "D) Saturn"],
                                    "answer": "B",
                                    "explanation": "Jupiter is the largest planet in our solar system.",
                                    "difficulty_rating": "easy"
                                },
                                {
                                    "question": "What is the powerhouse of the cell?",
                                    "options": ["A) Nucleus", "B) Mitochondria", "C) Ribosome", "D) Cytoplasm"],
                                    "answer": "B",
                                    "explanation": "Mitochondria is the powerhouse of the cell.",
                                    "difficulty_rating": "easy"
                                }
                            ]
                        })
                    }
                }
            ]
        },
        request=httpx.Request(method="POST", url="https://openrouter.ai/api/v1/chat/completions")
    )

    mock_post = mocker.patch(
        "httpx.AsyncClient.post",
        return_value=mock_response
    )

    return mock_post
