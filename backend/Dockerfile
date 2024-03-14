FROM python:3.10
LABEL authors="olegafanasev"
WORKDIR /backend/
COPY requiremnts.txt .
RUN pip install -r requiremnts.txt
COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]