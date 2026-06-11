from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from app.database import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    owner = Column(String(100), nullable=False)
    repo_name = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"))
    github_event_id = Column(String(100), unique=True)
    event_type = Column(String(100), nullable=False)
    actor = Column(String(100))
    created_at = Column(TIMESTAMP)