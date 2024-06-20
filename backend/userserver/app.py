import db
from fastapi import FastAPI, HTTPException, Response, Cookie
from fastapi.responses import JSONResponse
import psycopg2
from user import User
from task import Task
import grpc
from google.protobuf.json_format import MessageToJson
import events_pb2 as events
import events_pb2_grpc as events_grpc
from typing import Annotated
import json
import logging

DBAPI_ENGINE_CONFIG = "postgresql+psycopg2://user:password@db:5432/postgres"
db_api = db.DBAPI(DBAPI_ENGINE_CONFIG)
app = FastAPI()
channel = grpc.insecure_channel("task_storage:8001", options=(('grpc.enable_http_proxy', 0),))
stub = events_grpc.TaskStorageStub(channel)


@app.post("/signup")
def create_user(user: User):
    if db_api.user_exists(user):
        raise HTTPException(status_code=404, detail="User exists")
    db_api.create_user(user)


@app.post("/signin")
def authorize(user: User, response: Response):
    if not db_api.user_exists(user):
        raise HTTPException(status_code=404, detail="User doesn't exist")
    user_info = db_api.get_user(user)
    if user_info.login != user.login:
        raise HTTPException(status_code=404, detail="User doesn't exist")
    response.set_cookie("token", db_api.get_user_id(user))
    response.status_code = 200
    response.body = bytes(json.dumps({"id": db_api.get_user_id(user)}), encoding="utf8")
    return response


@app.put("/user")
def update(user: User, token: Annotated[int, Cookie()]):
    if not db_api.user_exists(user):
        raise HTTPException(status_code=404, detail="User doesn't exist")
    if db_api.get_user(user).password != user.password or db_api.get_user_id(user) != token:
        raise HTTPException(status_code=404, detail="Invalid data")
    db_api.update_user(user)

@app.post("/tasks")
def create_task(task: Task, token: Annotated[int, Cookie()]):
    if task.executor_id <= 0 or task.priority <= 0:
        raise HTTPException(404, "Bad request")
    task_request = events.CreateTaskRequest(
       creator_id=token,
       executor_id=task.executor_id,
       title=task.title,
       description=task.description,
       priority=task.priority        
    )
    task_response = stub.CreateTask(task_request)
    return JSONResponse(json.loads(MessageToJson(task_response)))

@app.put("/tasks")
def update_task(task: Task, token: Annotated[int, Cookie()]):
    if task.executor_id <= 0 or task.priority <= 0 and task.id <= 0:
        raise HTTPException(404, "Bad request")
    request = task.__dict__
    request["user_id"] = token
    del request["creator_id"]
    task_request = events.UpdateTaskRequest(**request)
    task_response = stub.UpdateTask(task_request)
    return JSONResponse(json.loads(MessageToJson(task_response)))

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, token: Annotated[int, Cookie()]):
    task_request = events.DeleteTaskRequest(id=task_id, user_id=token)
    task_response = stub.DeleteTask(task_request)
    return JSONResponse(json.loads(MessageToJson(task_response)))

@app.get("/tasks/{task_id}")
def get_task(task_id: int, token: Annotated[int, Cookie()]):
    task_request = events.GetTaskRequest(id=task_id, user_id=token)
    task_response = stub.GetTask(task_request)
    return JSONResponse(json.loads(MessageToJson(task_response)))

@app.get("/tasks")
def get_tasks(offset: int, count: int, token: Annotated[int, Cookie()]):
    task_request = events.GetTasksRequest(offset=offset, count=count, user_id=token)
    task_response = stub.GetTasks(task_request)
    return JSONResponse(json.loads(MessageToJson(task_response)))