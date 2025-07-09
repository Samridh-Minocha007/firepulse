from sqlalchemy.orm import Session
from ..models.user import User as UserModel
from ..models.trivia import UserAnswer, TriviaQuestion
from ..crud import badge as badge_crud

def check_and_award_badges(db: Session, user: UserModel) -> list[str]:
    """
    Checks user's trivia performance and awards new badges.
    Returns a list of names of newly awarded badges.
    """
    
    user = db.merge(user)

    newly_awarded_badges = []

    
    first_correct_badge = badge_crud.get_badge_by_name(db, name="First Correct Answer")
    if first_correct_badge and first_correct_badge not in user.badges:
        correct_answers_count = db.query(UserAnswer).filter_by(user_id=user.id, was_correct=True).count()
        if correct_answers_count >= 1:
            user.badges.append(first_correct_badge)
            newly_awarded_badges.append(first_correct_badge.name)

    
    movie_novice_badge = badge_crud.get_badge_by_name(db, name="Movie Novice")
    if movie_novice_badge and movie_novice_badge not in user.badges:
        correct_movie_answers = (
            db.query(UserAnswer)
            .join(TriviaQuestion)
            .filter(
                UserAnswer.user_id == user.id,
                UserAnswer.was_correct == True,
                TriviaQuestion.category.ilike('%movie%')
            )
            .count()
        )
        if correct_movie_answers >= 5:
            user.badges.append(movie_novice_badge)
            newly_awarded_badges.append(movie_novice_badge.name)

    if newly_awarded_badges:
        db.commit()

    return newly_awarded_badges
