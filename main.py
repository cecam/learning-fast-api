from fastapi import FastAPI
from routers import users, products
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Include the routers
app.include_router(users.router)
app.include_router(products.router)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Hello World"}