from fastapi import APIRouter, HTTPException
from models import User

router = APIRouter(
        prefix="/users",
        tags=["users"],
        responses={404: {"message": "Not found"}
    })

users = [User(id=1, name="Rick"), User(id=2, name="Morty"), User(id=3, name="Summer")]

@router.get("/")
async def users():
    return users

@router.post("/", status_code=201)
async def create_user(user: User):
    if search_user(user.id):
        raise HTTPException(status_code=409, detail="User already exists")
    users.append(user)
    return user

@router.put("/{id}")
async def update_user(id: int, user: User):
    user = search_user(id)
    if "message" in user:
        raise HTTPException(status_code=404, detail="User not found")
    user.name = user.name
    return user

@router.get("/{id}")
async def user(id: int):
    return search_user(id)
    
def search_user(id: int):
    users = filter(lambda user: user.id == id, users)
    try:
        return list(users)[0]
    except: 
        raise HTTPException(status_code=404, detail="User not found")
    
@router.delete("/{id}")
async def delete_user(id: int):
    user = search_user(id)
    if "message" in user:
        raise HTTPException(status_code=404, detail="User not found")
    users.remove(user)
    return user