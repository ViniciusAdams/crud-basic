from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
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


# By opening GET /users, the function below will be run
@app.get("/users")
def get_users():
    # Opens the database connection
    with engine.connect() as connection:
        # Runs normal SQL
        result = connection.execute(
            text("SELECT id, name, email, created_at FROM users;")
        )

        users = []

        # Turns MariaDB rows into Python dictionaries
        for row in result.mappings():
            users.append(dict(row))

    return users
#if access is executed 
@app.post("/users")
#Expect the incoming request body to match the UserCreate shape.
def create_user(user:UserCreate):
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
    