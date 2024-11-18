from pydantic import BaseModel
from typing import Optional
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    _public_key: str = None
    _private_key: str = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self._public_key = self._private_key.public_key()

