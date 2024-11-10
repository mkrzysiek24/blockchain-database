from typing import Any

from pydantic import BaseModel, Json


class Transaction(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    data: Json[Any]

    class Config:
        arbitrary_types_allowed = True

    def is_valid(self) -> bool:
        return True
