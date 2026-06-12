from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import Repository, Event
from sqlalchemy import func
from app.database import get_db
from app.models import Repository, Event
from app.schemas import RepositoryCreate
from app.github_fetcher import (
    fetch_repository,
    fetch_repository_events
)

router = APIRouter()


@router.get("/repositories")
def get_repositories(db: Session = Depends(get_db)):
    return db.query(Repository).all()

@router.post("/repositories")
def create_repository(
    repository: RepositoryCreate,
    db: Session = Depends(get_db)
):
    new_repo = Repository(
        owner=repository.owner,
        repo_name=repository.repo_name
    )

    db.add(new_repo)
    db.commit()
    db.refresh(new_repo)

    return new_repo

@router.post("/fetch-repo/{owner}/{repo_name}")
def fetch_and_store_repository(
    owner: str,
    repo_name: str,
    db: Session = Depends(get_db)
):
    github_data = fetch_repository(owner, repo_name)

    if github_data is None:
        return {
            "error": "Repository not found"
        }

    existing_repo = (
        db.query(Repository)
        .filter(
            Repository.github_repo_id == github_data["id"]
        )
        .first()
    )

    if existing_repo:
        return existing_repo

    repository = Repository(
        github_repo_id=github_data["id"],
        owner=github_data["owner"]["login"],
        repo_name=github_data["name"],
        stars=github_data["stargazers_count"],
        forks=github_data["forks_count"],
        open_issues=github_data["open_issues_count"],
        language=github_data["language"]
    )

    db.add(repository)
    db.commit()
    db.refresh(repository)

    return repository

@router.post("/fetch-events/{owner}/{repo_name}")
def fetch_and_store_events(
    owner: str,
    repo_name: str,
    db: Session = Depends(get_db)
):
    repository = (
        db.query(Repository)
        .filter(
            Repository.owner == owner,
            Repository.repo_name == repo_name
        )
        .first()
    )

    if not repository:
        return {
            "error": "Repository not found in database. Fetch repository first."
        }

    events_data = fetch_repository_events(owner, repo_name)

    if events_data is None:
        return {
            "error": "Could not fetch events from GitHub"
        }

    inserted = 0

    for event in events_data:

        existing_event = (
            db.query(Event)
            .filter(
                Event.github_event_id == event["id"]
            )
            .first()
        )

        if existing_event:
            continue

        new_event = Event(
            repository_id=repository.id,
            github_event_id=event["id"],
            event_type=event["type"],
            actor=event["actor"]["login"]
        )

        db.add(new_event)
        inserted += 1

    db.commit()

    return {
        "repository": f"{owner}/{repo_name}",
        "events_inserted": inserted
    }

@router.get("/events")
def get_events(
    db: Session = Depends(get_db)
):
    return db.query(Event).all()

@router.get("/event-count")
def event_count(
    db: Session = Depends(get_db)
):
    total = db.query(func.count(Event.id)).scalar()

    return {
        "total_events": total
    }

@router.get("/event-types")
def event_types(
    db: Session = Depends(get_db)
):
    results = (
        db.query(
            Event.event_type,
            func.count(Event.id).label("count")
        )
        .group_by(Event.event_type)
        .all()
    )

    return [
        {
            "event_type": row.event_type,
            "count": row.count
        }
        for row in results
    ]

@router.get("/top-actors")
def top_actors(
    db: Session = Depends(get_db)
):
    results = (
        db.query(
            Event.actor,
            func.count(Event.id).label("count")
        )
        .group_by(Event.actor)
        .order_by(
            func.count(Event.id).desc()
        )
        .limit(10)
        .all()
    )

    return [
        {
            "actor": row.actor,
            "count": row.count
        }
        for row in results
    ]

@router.get("/repository/{owner}/{repo_name}/event-types")
def repository_event_types(
    owner: str,
    repo_name: str,
    db: Session = Depends(get_db)
):
    repository = (
        db.query(Repository)
        .filter(
            Repository.owner == owner,
            Repository.repo_name == repo_name
        )
        .first()
    )

    if not repository:
        return {
            "error": "Repository not found"
        }

    results = (
        db.query(
            Event.event_type,
            func.count(Event.id).label("count")
        )
        .filter(
            Event.repository_id == repository.id
        )
        .group_by(Event.event_type)
        .all()
    )

    return [
        {
            "event_type": row.event_type,
            "count": row.count
        }
        for row in results
    ]

@router.get("/repository/{owner}/{repo_name}/top-actors")
def repository_top_actors(
    owner: str,
    repo_name: str,
    db: Session = Depends(get_db)
):
    repository = (
        db.query(Repository)
        .filter(
            Repository.owner == owner,
            Repository.repo_name == repo_name
        )
        .first()
    )

    if not repository:
        return {
            "error": "Repository not found"
        }

    results = (
        db.query(
            Event.actor,
            func.count(Event.id).label("count")
        )
        .filter(
            Event.repository_id == repository.id
        )
        .group_by(Event.actor)
        .order_by(
            func.count(Event.id).desc()
        )
        .limit(10)
        .all()
    )

    return [
        {
            "actor": row.actor,
            "count": row.count
        }
        for row in results
    ]

@router.get("/repositories/event-counts")
def repository_event_counts(
    db: Session = Depends(get_db)
):
    results = (
        db.query(
            Repository.owner,
            Repository.repo_name,
            func.count(Event.id).label("event_count")
        )
        .join(
            Event,
            Repository.id == Event.repository_id
        )
        .group_by(
            Repository.id
        )
        .all()
    )

    return [
        {
            "repository": f"{row.owner}/{row.repo_name}",
            "events": row.event_count
        }
        for row in results
    ]

@router.get("/repository/{owner}/{repo_name}/summary")
def repository_summary(
    owner: str,
    repo_name: str,
    db: Session = Depends(get_db)
):
    repository = (
        db.query(Repository)
        .filter(
            Repository.owner == owner,
            Repository.repo_name == repo_name
        )
        .first()
    )

    if not repository:
        return {
            "error": "Repository not found"
        }

    total_events = (
        db.query(func.count(Event.id))
        .filter(
            Event.repository_id == repository.id
        )
        .scalar()
    )

    return {
        "repository": f"{owner}/{repo_name}",
        "stars": repository.stars,
        "forks": repository.forks,
        "open_issues": repository.open_issues,
        "language": repository.language,
        "total_events": total_events
    }

@router.get("/most-active-repositories")
def most_active_repositories(
    db: Session = Depends(get_db)
):
    results = (
        db.query(
            Repository.owner,
            Repository.repo_name,
            func.count(Event.id).label("event_count")
        )
        .join(
            Event,
            Repository.id == Event.repository_id
        )
        .group_by(
            Repository.id
        )
        .order_by(
            func.count(Event.id).desc()
        )
        .all()
    )

    return [
        {
            "repository": f"{row.owner}/{row.repo_name}",
            "events": row.event_count
        }
        for row in results
    ]

@router.get("/repository/{owner}/{repo_name}/dashboard")
def repository_dashboard(
    owner: str,
    repo_name: str,
    db: Session = Depends(get_db)
):
    repository = (
        db.query(Repository)
        .filter(
            Repository.owner == owner,
            Repository.repo_name == repo_name
        )
        .first()
    )

    if not repository:
        return {
            "error": "Repository not found"
        }

    total_events = (
        db.query(func.count(Event.id))
        .filter(
            Event.repository_id == repository.id
        )
        .scalar()
    )

    event_types = (
        db.query(
            Event.event_type,
            func.count(Event.id).label("count")
        )
        .filter(
            Event.repository_id == repository.id
        )
        .group_by(
            Event.event_type
        )
        .all()
    )

    top_actors = (
        db.query(
            Event.actor,
            func.count(Event.id).label("count")
        )
        .filter(
            Event.repository_id == repository.id
        )
        .group_by(
            Event.actor
        )
        .order_by(
            func.count(Event.id).desc()
        )
        .limit(5)
        .all()
    )

    return {
        "repository": f"{owner}/{repo_name}",
        "stars": repository.stars,
        "forks": repository.forks,
        "open_issues": repository.open_issues,
        "language": repository.language,
        "total_events": total_events,
        "event_types": [
            {
                "event_type": row.event_type,
                "count": row.count
            }
            for row in event_types
        ],
        "top_actors": [
            {
                "actor": row.actor,
                "count": row.count
            }
            for row in top_actors
        ]
    }

@router.delete("/repository/{owner}/{repo_name}")
def delete_repository(
    owner: str,
    repo_name: str,
    db: Session = Depends(get_db)
):
    repository = (
        db.query(Repository)
        .filter(
            Repository.owner == owner,
            Repository.repo_name == repo_name
        )
        .first()
    )

    if not repository:
        return {
            "error": "Repository not found"
        }

    db.query(Event).filter(
        Event.repository_id == repository.id
    ).delete()

    db.delete(repository)

    db.commit()

    return {
        "message": f"{owner}/{repo_name} deleted successfully"
    }