from pydantic import BaseModel

class User(BaseModel):
    login: str = None
    password: str = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    birthday: str | None = None
