from sqlalchemy import VARCHAR, create_engine, or_, update, Column, Integer, String
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.ext.declarative import declarative_base
import events_pb2 as events
import logging
Base = declarative_base()

class Tasks(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer)
    executor_id = Column(Integer)
    title = Column(VARCHAR)
    description = Column(String)
    priority = Column(Integer)
    status = Column(String)

def get_task_fields(value: dict):
    fields = [
        "creator_id",
        "executor_id",
        "title",
        "description",
        "priority",
        "status"
    ]
    logging.error(value)
    return {
        field: value[field] for field in fields if field in value
    }


class Executor:
    def __init__(self, engine_config: str) -> None:
        self.engine = create_engine(engine_config)
        Base.metadata.create_all(self.engine)

    def create_task(self, params: dict) -> int:

        with Session(self.engine) as session:
            new_task = Tasks(**get_task_fields(params))
            session.add(new_task)
            session.commit()
            session.refresh(new_task)
            return new_task.id

    def update_task(self, params: dict):
        with Session(self.engine) as session:
            task = session.query(Tasks).filter(Tasks.id == params["id"]).first()
            if not task:
                raise RuntimeError("task doesn't exists")
            session.execute(
                update(Tasks).where(Tasks.id == params["id"]).values(
                    **get_task_fields(params)
                )
            )
            session.commit()

    def delete_task(self, task_id: int, user_id: int):
        with Session(self.engine) as session:
            task = session.query(Tasks).filter(Tasks.id == task_id).first()
            if not task:
                return
            if task.creator_id != user_id and task.executor_id != user_id:
                return
            session.delete(task)
            session.commit()

    def get_task_by_id(self, task_id: int, user_id: int) -> Tasks | None:
        with Session(self.engine) as session:
            task = session.query(Tasks).filter(Tasks.id == task_id).first()
            if not task:
                return None  
            if task.creator_id != user_id and task.executor_id != user_id:
                return None
            return task

    def get_tasks(self, count: int, offset: int, user_id: int):
        with Session(self.engine) as session:
            tasks = session.query(Tasks).filter(
                or_(
                    Tasks.creator_id == user_id,
                    Tasks.executor_id == user_id
                )
            ).offset(offset).limit(count).all()
            return tasks