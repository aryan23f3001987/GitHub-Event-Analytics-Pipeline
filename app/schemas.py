from pydantic import BaseModel


class RepositoryCreate(BaseModel):
    owner: str
    repo_name: str


class RepositoryResponse(BaseModel):
    id: int
    owner: str
    repo_name: str

    class Config:
        from_attributes = True