from fastapi import FastAPI
from routers import users, products

app = FastAPI()

# Include the routers
app.include_router(users.router)
app.include_router(products.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}