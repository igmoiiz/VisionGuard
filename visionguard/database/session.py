"""
VisionGuard Database Engine and Session Factory.
"""

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from visionguard.database.models import Base
from visionguard.logging.logger import logger


class DatabaseManager:
    def __init__(self, db_url: str = "sqlite:///data/visionguard.db", echo: bool = False) -> None:
        self.db_url = db_url

        # Ensure sqlite parent dir exists
        if db_url.startswith("sqlite:///"):
            db_path = Path(db_url.replace("sqlite:///", ""))
            db_path.parent.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(db_url, echo=echo, connect_args={"check_same_thread": False} if "sqlite" in db_url else {})
        self.SessionFactory = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
        self.init_db()

    def init_db(self) -> None:
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info(f"DatabaseManager: Initialized tables for DB '{self.db_url}'")
        except Exception as e:
            logger.error(f"DatabaseManager: Init DB error: {e}")

    def get_session(self) -> Session:
        return self.SessionFactory()
