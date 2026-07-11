from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr

app = FastAPI()

# Allows your React frontend to talk to your FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "mysql+pymysql://crud_user:crud_password_123@localhost:3306/crud_basic"

engine = create_engine(DATABASE_URL)


class UserCreate(BaseModel):
    name: str
    email: EmailStr


class UserUpdate(BaseModel):
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


@app.get("/users/{user_id}")
def get_user(user_id: int):
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT id, name, email, created_at
                FROM users
                WHERE id = :id
            """),
            {"id": user_id}
        )

        user = result.mappings().fetchone()

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

    return dict(user)


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


@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserUpdate):
    try:
        with engine.connect() as connection:
            existing_user = connection.execute(
                text("SELECT id FROM users WHERE id = :id"),
                {"id": user_id}
            ).fetchone()

            if existing_user is None:
                raise HTTPException(
                    status_code=404,
                    detail="User not found"
                )

            connection.execute(
                text("""
                    UPDATE users
                    SET name = :name, email = :email
                    WHERE id = :id
                """),
                {
                    "id": user_id,
                    "name": user.name,
                    "email": user.email
                }
            )

            connection.commit()

        return {
            "message": "User updated successfully",
            "id": user_id,
            "name": user.name,
            "email": user.email
        }

    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    with engine.connect() as connection:
        result = connection.execute(
            text("DELETE FROM users WHERE id = :id"),
            {"id": user_id}
        )

        connection.commit()

        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

    return {
        "message": "User deleted successfully",
        "id": user_id
    }