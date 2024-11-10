from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
