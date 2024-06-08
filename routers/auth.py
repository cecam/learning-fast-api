from fastapi import APIRouter, Depends, HTTPException, status
from models import AuthenticatedUser, UserDB
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

usersDB = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "email@mail.com",
        "disabled": False,
        "hashed_password": "123456"
    }, 
    "janedoe": {
        "username": "janedoe",
        "full_name": "Jane Doe",
        "email": "mail@mail.com",
        "disabled": True,
        "hashed_password": "123456"
    }
}


router = APIRouter(tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def search_user(username: str):
    if username in usersDB:
        return UserDB(**usersDB[username])
    return None

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = usersDB.get(form.username)
    if not user_db:
        raise HTTPException(status_code=400, detail="User not found")
    
    user = search_user(form.username)
    if user.password != form.password:
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    return {"access_token": user.username, "token_type": "bearer"}

async def current_user(token: str = Depends(oauth2_scheme)):
    user = search_user(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found", headers={"WWW-Authenticate": "Bearer"})
    
    if user.disabled:
        raise HTTPException(status_code=400, detail="User is disabled")
    
    return user

@router.get("/users/me", response_model=AuthenticatedUser)
async def read_users_me(user: UserDB = Depends(current_user)):
    return user
    

