# firepulse/schemas/trivia.py
from pydantic import BaseModel, ConfigDict
from typing import List

class TriviaAnswer(BaseModel):
    text: str

class TriviaQuestion(BaseModel):
    id: int
    category: str
    question_text: str
    answers: List[TriviaAnswer]

    model_config = ConfigDict(from_attributes=True)

class AnswerSubmission(BaseModel):
    question_id: int
    selected_answer_text: str

class Badge(BaseModel):
    id: int
    name: str
    description: str

    model_config = ConfigDict(from_attributes=True)
