from fastapi import FastAPI
from routers import users

app = FastAPI()

# Include the routers
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}