from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from ..core.db import Base

user_badge_association = Table(
    'user_badge', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('badge_id', Integer, ForeignKey('badges.id'))
)

class TriviaQuestion(Base):
    __tablename__ = "trivia_questions"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    question_text = Column(String, unique=True, nullable=False)
    correct_answer = Column(String, nullable=False)

    
    incorrect_answer_1 = Column(String, nullable=False, server_default="Default Answer 1")
    incorrect_answer_2 = Column(String, nullable=False, server_default="Default Answer 2")
    incorrect_answer_3 = Column(String, nullable=False, server_default="Default Answer 3")


class UserAnswer(Base):
    __tablename__ = "user_answers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question_id = Column(Integer, ForeignKey("trivia_questions.id"))
    was_correct = Column(Boolean, default=False)
    user = relationship("User") 
    question = relationship("TriviaQuestion")

class Badge(Base):
    __tablename__ = "badges"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)

