from typing import Optional

from .user import User


class Patient(User):
    insurance_number: Optional[str] = None
