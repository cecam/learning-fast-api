from pydantic import BaseModel

# User model
class User(BaseModel):
    id: int
    name: str

class AuthenticatedUser(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool

class UserDB(AuthenticatedUser):
    hashed_password: str

class Product(BaseModel):
    id: int
    name: str
    price: float
    description: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None
    fulln_name: str = None