from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Repository
from app.schemas import RepositoryCreate

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