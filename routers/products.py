from fastapi import APIRouter, HTTPException
from models import Product

router = APIRouter(prefix="/products", 
    tags=["products"],
    responses={404: {"message": "Not found"}
    })

products = [
    {
        "id": 1,
        "name": "Product 1",
        "price": 100.0,
        "description": "Description of product 1"
    },
    {
        "id": 2,
        "name": "Product 2",
        "price": 200.0,
        "description": "Description of product 2"
    },
    {
        "id": 3,
        "name": "Product 3",
        "price": 300.0,
        "description": "Description of product 3"
    }
]

@router.get("/")
async def products():
    return products

@router.get("/{id}")
async def product(id: int):
    return search_product(id)

@router.post("/", status_code=201)
async def create_product(product: Product):
    if search_product(product.id):
        raise HTTPException(status_code=409, detail="Product already exists")
    products.append(product)
    return product

def search_product(id: int):
    product = filter(lambda product: product.id == id, products)
    try:
        return list(product)[0]
    except: 
        return {"message": "Product not found"}