from pydantic import BaseModel

# User model
class User(BaseModel):
    id: int
    name: str

class Product(BaseModel):
    id: int
    name: str
    price: float
    description: str