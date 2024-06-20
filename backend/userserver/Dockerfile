FROM python
WORKDIR /backend/
COPY ./userserver/requiremnts.txt .
RUN pip install -r requiremnts.txt
COPY ./proto ./proto
RUN python3 -m grpc_tools.protoc -I./proto --python_out=. --pyi_out=. --grpc_python_out=. ./proto/events.proto
COPY ./userserver .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]