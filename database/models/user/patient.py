from user import User
from typing import Optional

class Patient(User):
  insurance_number: Optional[str] = None
  blood_type: Optional[str] = None
