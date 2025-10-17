from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from app.schemas.user import UserOut, UserCreate, UserUpdate
from app.db.memory import list_users, get_user, create_user, update_user, delete_user

router = APIRouter(tags=["users"])


@router.get("/users", response_model=List[UserOut])
def list_users_endpoint(status: Optional[str] = None):
    users = list_users()
    if status:
        return [u for u in users if u.status == status]
    return users


@router.get("/users/{user_id}", response_model=UserOut)
def get_user_endpoint(user_id: int):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(data: UserCreate):
    return create_user(data)


@router.put("/users/{user_id}", response_model=UserOut)
def update_user_endpoint(user_id: int, data: UserUpdate):
    user = update_user(user_id, data)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(user_id: int):
    ok = delete_user(user_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return None