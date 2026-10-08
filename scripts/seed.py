import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, Base, engine
from app import crud
from app.logger import logger

def main():
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        logger.info("Seeding sample data into PocketLedger database...")
        created = crud.seed_sample_data(db)
        logger.info(f"Successfully seeded {len(created)} sample transactions!")
    except Exception as e:
        logger.error(f"Failed to seed database: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
