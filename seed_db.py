from firepulse.core.db import SessionLocal
from firepulse.crud.badge import create_badge

def seed_badges():
    print("Seeding badges...")
    db = SessionLocal()
    try:
        create_badge(db, name="Movie Novice", description="Answer 5 movie trivia questions correctly.")
        create_badge(db, name="Music Maestro", description="Answer 5 music trivia questions correctly.")
        create_badge(db, name="First Correct Answer", description="Get your first trivia answer right!")
        print("Badges seeded successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_badges()