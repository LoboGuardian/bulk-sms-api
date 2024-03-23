from fastapi import APIRouter, Depends, HTTPException
# from src.auth.schemas import Users
from auth.schemas import Users
from auth.models import User
from fastapi import FastAPI, Form
# from auth.utils import Authenticate
# from utils import Authenticate
from typing import Annotated
from database import SessionLocal
import hashlib
router = APIRouter(
    prefix='/users',
    tags=['users'],
)


@router.get("/root/", tags=["users"])
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


# auth_service = Authenticate()


@router.post("/register/", tags=['users'])
async def register_user(username: Annotated[str, Form()], email: Annotated[str, Form()], password: Annotated[str, Form()]):
    db = SessionLocal()
    salt = "Your Salt"
    password_hash = hashlib.sha256(
        (password + salt).encode('utf-8')).hexdigest()
    # print(password_hash)
    try:
        # Create a new user instance
        new_user = User(user_name=username,
                        password=password_hash, email=email)
        # print(new_user)
        # Add user to the database
        db.add(new_user)
        # Commit the transaction
        db.commit()
        # Refresh the user instance to access its generated id
        db.refresh(new_user)
        return {"message": "User registered successfully", "user_id": new_user.id}
    except Exception as e:
        # Rollback the transaction in case of any error
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        # Close the database session
        db.close()
