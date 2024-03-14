from pydantic import BaseModel
from dataclasses import dataclass

class User(BaseModel):
    login: str = None
    password: str = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    birthday: str | None = None
