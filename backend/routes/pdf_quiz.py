"""
PDF Quiz Generation Route
Handles PDF file uploads and generates quiz questions from PDF content
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import PyPDF2
import io
from utils.auth import verify_user
from agents.quiz_agent import generate_quiz_with_fallback
import time

router = APIRouter(
    prefix="/quiz",
    tags=["quiz", "pdf"]
)


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    answer: str
    explanation: str


class PdfQuizResponse(BaseModel):
    questions: List[QuizQuestion]
    quiz: List[QuizQuestion]  # Alias for compatibility
    metadata: dict


def extract_text_from_pdf(pdf_file: bytes) -> str:
    """
    Extract text content from PDF file
    
    Args:
        pdf_file: PDF file bytes
    
    Returns:
        Extracted text content
    """
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        text = ""
        
        # Extract text from all pages
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n"
        
        # Clean up the text
        text = text.strip()
        
        if not text:
            raise ValueError("No text content found in PDF")
        
        return text
    
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def chunk_text(text: str, max_chars: int = 3000) -> str:
    """
    Truncate text to a reasonable length for quiz generation
    
    Args:
        text: Full text content
        max_chars: Maximum characters to keep
    
    Returns:
        Truncated text
    """
    if len(text) <= max_chars:
        return text
    
    # Try to cut at a sentence boundary
    truncated = text[:max_chars]
    last_period = truncated.rfind('.')
    
    if last_period > max_chars * 0.7:  # If we found a period in the last 30%
        return truncated[:last_period + 1]
    
    return truncated


@router.post("/generate-from-pdf", response_model=PdfQuizResponse)
async def generate_quiz_from_pdf(
    file: UploadFile = File(..., description="PDF file to generate quiz from"),
    num_questions: int = Form(5, ge=1, le=10, description="Number of questions to generate"),
    current_user: dict = Depends(verify_user)
):
    """
    Generate quiz questions from uploaded PDF file
    
    **Workflow:**
    1. Validate PDF file (type, size)
    2. Extract text content from PDF
    3. Generate quiz questions using AI
    4. Return questions with metadata
    
    **Request:**
    - Multipart form data with PDF file
    - num_questions: 1-10 (default: 5)
    
    **Response:**
    ```json
    {
        "questions": [
            {
                "question": "What is...?",
                "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
                "answer": "B",
                "explanation": "..."
            }
        ],
        "metadata": {
            "num_questions": 5,
            "pdf_pages": 3,
            "content_length": 1234,
            "generation_time_ms": 2500
        }
    }
    ```
    
    **Limits:**
    - File size: 10MB max
    - File type: PDF only
    - Questions: 1-10
    
    Requires authentication.
    """
    start_time = time.time()
    
    try:
        # Validate file type
        if not file.content_type == "application/pdf":
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PDF files are supported."
            )
        
        # Read file content
        pdf_content = await file.read()
        
        # Validate file size (10MB max)
        if len(pdf_content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB."
            )
        
        # Extract text from PDF
        try:
            full_text = extract_text_from_pdf(pdf_content)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        
        # Chunk text to manageable size
        text_chunk = chunk_text(full_text, max_chars=3000)
        
        # Count pages (for metadata)
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        num_pages = len(pdf_reader.pages)
        
        # Generate quiz questions using AI
        try:
            quiz_data = await generate_quiz_with_fallback(
                notes=text_chunk,
                num_questions=num_questions
            )
            
            questions = quiz_data.get('questions', [])
            
            if not questions:
                raise ValueError("No questions generated")
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate quiz questions: {str(e)}"
            )
        
        # Calculate generation time
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        # Return response
        return {
            "questions": questions,
            "quiz": questions,  # Alias for compatibility
            "metadata": {
                "num_questions": len(questions),
                "pdf_pages": num_pages,
                "content_length": len(text_chunk),
                "generation_time_ms": generation_time_ms,
                "filename": file.filename
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error processing PDF: {str(e)}"
        )
