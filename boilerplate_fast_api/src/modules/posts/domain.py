from pydantic import BaseModel
from typing import Optional


class Post(BaseModel):
    """
    Pure Domain Model for Post.
    Does not know about SQLAlchemy or FastAPI.
    """
    id: Optional[int] = None
    title: str
    content: str
    author_id: int
