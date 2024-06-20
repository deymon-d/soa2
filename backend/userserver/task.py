from pydantic import BaseModel

class Task(BaseModel):
    id: int | None = None
    creator_id: int | None
    executor_id: int | None
    title: str | None
    description: str | None
    priority: int | None
    status: str | None
