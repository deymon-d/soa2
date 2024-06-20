FROM python
WORKDIR /backend/
COPY ./task_storage/requirements.txt  .
RUN pip install -r requirements.txt
COPY ./proto ./proto
RUN python3 -m grpc_tools.protoc -I./proto --python_out=. --pyi_out=. --grpc_python_out=. ./proto/events.proto
COPY ./task_storage .
CMD ["python3", "app.py"]
