from fastapi import APIRouter, HTTPException, Body, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import json
import random
from ..core.config import GEMINI_API_KEY

router = APIRouter()

# --- FIX: Updated to a current and widely available Gemini model ---
GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

class TriviaAnswer(BaseModel):
    text: str
    is_correct: bool

class GeneratedTriviaQuestion(BaseModel):
    question_text: str
    answers: List[TriviaAnswer]

class TriviaResponse(BaseModel):
    message: str
    question: Optional[GeneratedTriviaQuestion] = None

async def generate_trivia_question_from_gemini(client: httpx.AsyncClient, topic: str) -> Optional[GeneratedTriviaQuestion]:
    """Generates a trivia question by calling the Gemini API."""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key not configured.")
        
    prompt = f"""
    Generate a unique and engaging trivia question about the topic: "{topic}".
    The question should be multiple-choice.
    Provide your response STRICTLY in JSON format with the following structure:
    {{
      "question_text": "The trivia question text?",
      "answers": [
        {{"text": "Option A (Incorrect)", "is_correct": false}},
        {{"text": "Option B (Correct Answer)", "is_correct": true}},
        {{"text": "Option C (Incorrect)", "is_correct": false}},
        {{"text": "Option D (Incorrect)", "is_correct": false}}
      ]
    }}
    Ensure exactly one answer has "is_correct": true. Ensure there are exactly four distinct options.
    """
    api_url_with_key = f"{GEMINI_API_BASE_URL}?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }
    
    try:
        response = await client.post(api_url_with_key, json=payload)
        response.raise_for_status() # This will raise an error for 4xx or 5xx responses
        result_json = response.json()
        
        if not result_json.get("candidates"):
            print(f"Error: Invalid response structure from Gemini API: {result_json}")
            raise HTTPException(status_code=502, detail="Invalid response structure from Gemini API.")
            
        trivia_data_str = result_json["candidates"][0]["content"]["parts"][0]["text"]
        trivia_data = json.loads(trivia_data_str)
        
        return GeneratedTriviaQuestion(**trivia_data)
        
    except httpx.HTTPStatusError as e:
        # This will give you more detailed info in your server log if the API call fails
        print(f"Error generating trivia question: HTTP Status {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during trivia generation: {e}")
        return None

@router.post("/start_session/{user_id}", response_model=TriviaResponse)
async def start_trivia_session(user_id: str, request: Request, topic: str = Body(..., embed=True)):
    client: httpx.AsyncClient = request.app.state.httpx_client
    question = await generate_trivia_question_from_gemini(client, topic)
    if not question:
        raise HTTPException(status_code=502, detail="Failed to generate trivia question.")
    return TriviaResponse(message=f"Trivia started for {user_id} on '{topic}'.", question=question)

@router.post("/submit_answer/{user_id}", response_model=Dict[str, Any])
async def submit_answer(user_id: str, answers: List[TriviaAnswer] = Body(...), selected_answer_text: str = Body(...)):
    correct_answer_obj = next((ans for ans in answers if ans.is_correct), None)
    submitted_answer_obj = next((ans for ans in answers if ans.text == selected_answer_text), None)

    if not submitted_answer_obj or not correct_answer_obj:
        raise HTTPException(status_code=400, detail="Invalid answer data provided.")
        
    is_correct = submitted_answer_obj.is_correct
    points = 5 if is_correct else 0
    message = f"Correct! You earned {points} points." if is_correct else f"Wrong. The correct answer was: '{correct_answer_obj.text}'."
    
    return {"message": message, "was_correct": is_correct, "points_awarded": points}