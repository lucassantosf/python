from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    """
    Pure Domain Model for User.
    Does not know about SQLAlchemy or FastAPI.
    """
    id: Optional[int] = None
    email: str
    password_hash: str
    role: str = "user"
