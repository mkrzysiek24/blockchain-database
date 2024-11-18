from typing import Any
from datetime import datetime
from pydantic import BaseModel, Json


class Transaction(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    data: Json[Any]
    date: datetime

    class Config:
        arbitrary_types_allowed = True

    def is_valid(self) -> bool:
        return True
