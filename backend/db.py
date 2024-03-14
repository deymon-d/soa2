from sqlalchemy import Column, Integer, String, create_engine, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

import user as user_lib

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, index=True)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone = Column(String)
    birthday = Column(String)

class DBAPI:
    def __init__(self, engine_config: str) -> None:
        self.engine = create_engine(engine_config)
        Base.metadata.create_all(self.engine)

    def create_user(self, user: user_lib.User) -> None:
        with Session(self.engine) as session:
            new_user = User(login=user.login, password=user.password)
            session.add(new_user)
            session.commit()

    def user_exists(self, user: user_lib.User) -> bool:
        with Session(self.engine) as session:
            users = session.query(User).filter(User.login == user.login).all()
            session.commit()
        return len(users)

    def get_user(self, user: user_lib.User) -> user_lib.User:
        with Session(self.engine) as session:
            users = session.query(User).filter(User.login == user.login).all()
            session.commit()
            user = user_lib.User()
            user.login = users[0].login
            user.password = users[0].password
            user.first_name = users[0].first_name
            user.last_name = users[0].last_name
            user.email = users[0].email,
            user.phone = users[0].phone,
            user.birthday = users[0].birthday
            return user

    def update_user(self, user: user_lib.User) -> None:
        with Session(self.engine) as session:
            session.execute(update(User).where(User.login == user.login).values(
                first_name = user.first_name,
                last_name = user.last_name,
                email = user.email,
                phone = user.phone,
                birthday = user.birthday
            ))
            session.commit()


