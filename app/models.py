from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, DateTime, BigInteger
from app.database import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)

    github_repo_id = Column(BigInteger, unique=True)

    owner = Column(String(100))

    repo_name = Column(String(200))

    stars = Column(Integer)

    forks = Column(Integer)

    open_issues = Column(Integer)

    language = Column(String(100))

    created_at = Column(DateTime)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)

    repository_id = Column(Integer, ForeignKey("repositories.id"))

    github_event_id = Column(String(100), unique=True)

    event_type = Column(String(100))

    actor = Column(String(100))

    created_at = Column(DateTime)