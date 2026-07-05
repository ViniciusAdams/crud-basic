from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr

app = FastAPI()

DATABASE_URL = "mysql+pymysql://crud_user:crud_password_123@localhost:3306/crud_basic"

engine = create_engine(DATABASE_URL)


class UserCreate(BaseModel):
    name: str
    email: EmailStr


@app.get("/")
def home():
    return {"message": "API is working"}


@app.get("/db-test")
def db_test():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT DATABASE();"))
        database_name = result.scalar()

    return {
        "message": "Database connection is working",
        "database": database_name
    }


@app.get("/users")
def get_users():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT id, name, email, created_at FROM users;")
        )

        users = []

        for row in result.mappings():
            users.append(dict(row))

    return users


@app.post("/users")
def create_user(user: UserCreate):
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                    INSERT INTO users (name, email)
                    VALUES (:name, :email)
                """),
                {
                    "name": user.name,
                    "email": user.email
                }
            )

            connection.commit()

            new_user_id = result.lastrowid

        return {
            "message": "User created successfully",
            "id": new_user_id,
            "name": user.name,
            "email": user.email
        }

    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )