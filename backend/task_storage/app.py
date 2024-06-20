from concurrent import futures

import grpc
import events_pb2 as events
import events_pb2_grpc as events_grpc
from google.protobuf.json_format import MessageToJson
import json

import db

db_engine = db.Executor("postgresql+psycopg2://postgres:password@taskdb:5432/postgres")

def create_task_from_dict(params: dict):
    fields = [
        "id",
        "creator_id",
        "executor_id",
        "title",
        "description",
        "priority",
        "status"
    ]
    res = {
        field: params[field] for field in fields if field in params
    }
    return events.Task(**res)      


class TaskStorageServicer(events_grpc.TaskStorageServicer):
    def CreateTask(self, request: events.CreateTaskRequest, context):
        json_var = dict(json.loads(MessageToJson(request)))
        json_var["creator_id"] = json_var["creatorId"]
        json_var["executor_id"] = json_var["executorId"]
        task_id = db_engine.create_task(json_var)
        return events.CreateTaskResponse(id=task_id)

    def UpdateTask(self, request: events.UpdateTaskRequest, context):
        json_var = dict(json.loads(MessageToJson(request)))
        json_var["executor_id"] = json_var["executorId"]
        db_engine.update_task(json_var)
        return events.UpdateTaskResponse()

    def DeleteTask(self, request: events.DeleteTaskRequest, context):
        db_engine.delete_task(request.id, request.user_id)
        return events.DeleteTaskResponse()

    def GetTask(self, request: events.GetTaskRequest, context):
        task = db_engine.get_task_by_id(request.id, request.user_id)
        if not task:
            return events.Task()
        return create_task_from_dict(task.__dict__)

    def GetTasks(self, request: events.GetTasksRequest, context):
        result = db_engine.get_tasks(
            count=request.count,
            offset=request.offset,
            user_id=request.user_id
        )
        return events.GetTasksResponse(tasks=list(map(
            lambda task: create_task_from_dict(task.__dict__),
            result
        )))


if __name__ == "__main__":
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    events_grpc.add_TaskStorageServicer_to_server(
        TaskStorageServicer(), server)
    server.add_insecure_port("0.0.0.0:8001")
    server.start()
    server.wait_for_termination()