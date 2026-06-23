from fastapi import FastAPI
from sqlalchemy import create_engine, text

app = FastAPI()

DATABASE_URL = "mysql+pymysql://crud_user:db159@127.0.0.1:3306/crud_basic"

engine = create_engine(DATABASE_URL)


@app.get("/")
def home():
    return {"message":"API is working"}


@app.get("/db-test")
def db_test():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT DATABASE();"))
        database_name = result.scalar()

        return {
            "message": "Database connection is working",
            "database": database_name
        }