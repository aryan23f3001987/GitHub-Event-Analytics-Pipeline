from pydantic import BaseModel


class RepositoryCreate(BaseModel):
    owner: str
    repo_name: str


class RepositoryResponse(BaseModel):

    id: int

    github_repo_id: int

    owner: str

    repo_name: str

    stars: int

    forks: int

    open_issues: int

    language: str | None = None

    class Config:
        from_attributes = True