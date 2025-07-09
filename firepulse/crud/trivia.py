from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from ..models.trivia import TriviaQuestion as TriviaQuestionModel, UserAnswer as UserAnswerModel

def create_trivia_question(db: Session, question_data: dict, category: str):
    """
    Saves a new trivia question and all its answers to the database.
    """
    question_text = question_data.get('question_text') or question_data.get('question')
    if not question_text:
        return None

    db_question = db.query(TriviaQuestionModel).filter_by(question_text=question_text).first()
    if db_question:
        
        return db_question

    correct_answer_text = ""
    incorrect_answers = []
    for answer in question_data['answers']:
        if answer.get('is_correct'): 
            correct_answer_text = answer.get('text')
        else:
            incorrect_answers.append(answer.get('text'))

    
    while len(incorrect_answers) < 3:
        incorrect_answers.append("Generated incorrect answer") 

    db_question = TriviaQuestionModel(
        category=category,
        question_text=question_text,
        correct_answer=correct_answer_text,
        incorrect_answer_1=incorrect_answers[0],
        incorrect_answer_2=incorrect_answers[1],
        incorrect_answer_3=incorrect_answers[2],
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

def get_unanswered_question(db: Session, category: str, user_id: int):
    """Fetches a random trivia question from the database that the user has not yet answered."""
    answered_question_ids = db.query(UserAnswerModel.question_id).filter_by(user_id=user_id)

    return (
        db.query(TriviaQuestionModel)
        .filter(
            and_(
                TriviaQuestionModel.category.ilike(f'%{category}%'),
                TriviaQuestionModel.id.notin_(answered_question_ids) 
            )
        )
        .order_by(func.random())
        .first()
    )

def record_user_answer(db: Session, user_id: int, question_id: int, was_correct: bool):
    """Records a user's answer to a question."""
    db_answer = UserAnswerModel(user_id=user_id, question_id=question_id, was_correct=was_correct)
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer

def get_question_by_id(db: Session, question_id: int):
    """Fetches a question by its ID."""
    return db.query(TriviaQuestionModel).filter_by(id=question_id).first()


def get_user_score(db: Session, user_id: int) -> int:
    """Calculates the total trivia score for a user."""
    correct_answers_count = (
        db.query(UserAnswerModel)
        .filter_by(user_id=user_id, was_correct=True)
        .count()
    )
    return correct_answers_count * 10 
