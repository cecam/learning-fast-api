from pydantic import BaseModel

# User model
class User(BaseModel):
    id: int
    name: str