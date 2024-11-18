from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    public_key: str = None
    private_key: str = None
