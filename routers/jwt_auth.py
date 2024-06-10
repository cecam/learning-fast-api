from fastapi import APIRouter, Depends, HTTPException, status
from models import AuthenticatedUser, UserDB, Token, TokenData
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import InvalidTokenError

# Sectret key for the JWT token
SECRET_KEY = "ea480dc9fd80680bde59fa4d340cb2b68ad8d9373e01ec5a0f3860e9ac561e54"
# Algorithm used to sign the JWT token
ALGORITHM = "HS256"
ACCESS_TOKEN_EXP_MINUTES = 30

crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

usersDB = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "email@mail.com",
        "disabled": False,
        "hashed_password": "$2a$12$oJCK3EmBSF6EJhS8lfblHOu/DKtcgG9xGZzFPQ1lhV/4V9w3Q2E8"
    }, 
    "janedoe": {
        "username": "janedoe",
        "full_name": "Jane Doe",
        "email": "mail@mail.com",
        "disabled": True,
        "hashed_password": "$2a$12$oJCK3EmBSF6EJhS8lfblHOu/DKtcgG9xGZzFPQ1lhV/4V9w3Q2E8"
    }
}


router = APIRouter(tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def search_user(username: str):
    if username in usersDB:
        return UserDB(**usersDB[username])
    return None

def verify_password(plain_password, hashed_password):
    return crypt.verify(plain_password, hashed_password)


def get_password_hash(password):
    return crypt.hash(password)

def access_token_expires():
    return datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXP_MINUTES)

async def auth_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=400, detail="Invalid token")
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")
    return search_user(token_data.username)

async def current_user(token: str = Depends(oauth2_scheme)):
    user = auth_user(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found", headers={"WWW-Authenticate": "Bearer"})
    
    if user.disabled:
        raise HTTPException(status_code=400, detail="User is disabled")
    
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": access_token_expires()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = usersDB.get(form.username)
    if not user_db:
        raise HTTPException(status_code=400, detail="User not found")
    
    user = search_user(form.username)

    if not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    access_token = {
        "username": user.username,
        "full_name": user.full_name,
        "exp": access_token_expires()
    }

    return {"access_token": create_access_token(access_token), "token_type": "bearer"}

@router.get("/users/me", response_model=AuthenticatedUser)
async def read_users_me(user: UserDB = Depends(current_user)):
    return user
    

    