import db
from fastapi import FastAPI, HTTPException
import psycopg2
from user import User

DBAPI_ENGINE_CONFIG = "postgresql+psycopg2://user:password@db:5432/postgres"
db_api = db.DBAPI(DBAPI_ENGINE_CONFIG)
app = FastAPI()


@app.post("/signup")
def create_user(user: User):
    if db_api.user_exists(user):
        raise HTTPException(status_code=404, detail="User exists")
    db_api.create_user(user)


@app.post("/signin")
def authorize(user: User):
    if not db_api.user_exists(user):
        raise HTTPException(status_code=404, detail="User doesn't exist")
    # в будущем токен отдавать будем видимо


@app.put("/user")
def update(user: User):
    if not db_api.user_exists(user):
        raise HTTPException(status_code=404, detail="User1 doesn't exist")
    if db_api.get_user(user).password != user.password:
        print(db_api.get_user(user))
        raise HTTPException(status_code=404, detail="User doesn't exist")
    db_api.update_user(user)

