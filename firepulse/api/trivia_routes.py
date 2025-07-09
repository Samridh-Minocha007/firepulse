# firepulse/api/trivia_routes.py
from fastapi import APIRouter, HTTPException, Body, Request, Depends, status
from sqlalchemy.orm import Session
import httpx
import json
import random

from ..core.config import settings
from ..core.db import SessionLocal
from ..api.auth_routes import get_current_user
from ..models.user import User as UserModel
from ..crud import trivia as trivia_crud
from ..schemas import trivia as trivia_schema
from ..services import gamification # Ensure this import is correct

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

async def generate_trivia_question_from_gemini(client: httpx.AsyncClient, topic: str) -> dict | None:
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key not configured.")

    prompt = f'''
    Generate a unique and factually accurate trivia question about the topic: "{topic}".
    The question should be multiple-choice. Before generating, double-check the factual accuracy of the question and the correct answer.
    Provide your response STRICTLY in JSON format with the following structure:
    {{
      "question_text": "The trivia question text?",
      "answers": [
        {{"text": "An incorrect answer", "is_correct": false}},
        {{"text": "The single correct answer", "is_correct": true}},
        {{"text": "Another incorrect answer", "is_correct": false}},
        {{"text": "A third incorrect answer", "is_correct": false}}
      ]
    }}
    Ensure exactly one answer has "is_correct": true. Ensure there are exactly four distinct options. Do not repeat answers.'''
    
    api_url_with_key = f"{GEMINI_API_BASE_URL}?key={settings.GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json"}}
    try:
        response = await client.post(api_url_with_key, json=payload)
        response.raise_for_status()
        result_json = response.json()
        if not result_json.get("candidates"):
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Invalid response structure from Gemini API.")
        trivia_data_str = result_json["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(trivia_data_str)
    except Exception as e:
        print(f"An unexpected error occurred during trivia generation: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Trivia generation failed: {e}")


@router.post("/trivia/start", response_model=trivia_schema.TriviaQuestion, tags=["Trivia"])
async def start_trivia_game(
    request: Request,
    topic: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_question = trivia_crud.get_unanswered_question(db, category=topic, user_id=current_user.id)

    if not db_question:
        print("No unanswered questions in DB, generating new one from Gemini...")
        client: httpx.AsyncClient = request.app.state.httpx_client
        generated_question_data = await generate_trivia_question_from_gemini(client, topic)
        if not generated_question_data:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to generate trivia question.")

        db_question = trivia_crud.create_trivia_question(db, question_data=generated_question_data, category=topic)

    if not db_question:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not retrieve or create a trivia question.")

    answers_for_client = [
        {"text": db_question.correct_answer},
        {"text": db_question.incorrect_answer_1},
        {"text": db_question.incorrect_answer_2},
        {"text": db_question.incorrect_answer_3},
    ]
    random.shuffle(answers_for_client)

    return trivia_schema.TriviaQuestion(
        id=db_question.id,
        category=db_question.category,
        question_text=db_question.question_text,
        answers=answers_for_client
    )

@router.post("/trivia/submit", tags=["Trivia"])
def submit_trivia_answer(submission: trivia_schema.AnswerSubmission, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    question = trivia_crud.get_question_by_id(db, question_id=submission.question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found.")

    is_correct = (submission.selected_answer_text.lower() == question.correct_answer.lower())
    
    trivia_crud.record_user_answer(db, user_id=current_user.id, question_id=question.id, was_correct=is_correct)
    
    points_awarded = 0
    message = ""
    new_badges = []

    if is_correct:
        points_awarded = 10
        # --- START OF CHANGE (Fix InvalidRequestError for persistency) ---
        # Re-fetch the user within this session to ensure it's persistent
        # This is safer when modifying an object obtained from a dependency
        user_to_update = db.query(UserModel).filter(UserModel.id == current_user.id).first()
        if user_to_update: # Ensure user is found
            user_to_update.total_points = (user_to_update.total_points or 0) + points_awarded
            db.commit()
            db.refresh(user_to_update) # Refresh the re-fetched object
            # Update current_user in case it's used later in this function
            current_user.total_points = user_to_update.total_points
            current_user.badges = user_to_update.badges # Also update badges if needed for gamification
        # --- END OF CHANGE ---

        message = f"Correct! You earned {points_awarded} points."
        
        # Pass the updated user object to gamification.check_and_award_badges
        new_badges = gamification.check_and_award_badges(db, user=user_to_update) # Pass user_to_update
        if new_badges:
            badge_names = [badge.name for badge in new_badges]
            message += f" You've earned new badges: {', '.join(badge_names)}!"
    else:
        message = f"Wrong. The correct answer was: '{question.correct_answer}'."

    return {"message": message, "was_correct": is_correct, "points_awarded": points_awarded, "new_badges_awarded": new_badges}


@router.get("/trivia/score", tags=["Trivia"])
def get_user_trivia_score(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return {"total_score": current_user.total_points}
