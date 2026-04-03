from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
#from fastapi import HTTPException
from model import Product
from database import SessionLocal, engine
import database_models
from sqlalchemy.orm import Session

#----------------------------------------------------
import os
from dotenv import load_dotenv

# Loading the variables from .env
load_dotenv()

# Accessing them using os.getenv
db_url = os.getenv("db_url")
app = FastAPI()

@app.get("/")
def read_root():
    return {"db_status": "Connected to " + db_url}
#----------------------------------------------------


# For running frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_methods = ["*"]
)

database_models.Base.metadata.create_all(bind = engine)

@app.get("/")
def Msg1():
    return "Welcome to backend project"


products = [
    Product(id = 1, name = "Phone", description = "Samsung phone", price = 175, quantity = 25),
    Product(id = 2, name = "Laptop", description = "Gaming laptop", price = 399.99, quantity = 20),
    Product(id = 3, name = "Pen", description = "Gel pen", price = 2.99, quantity = 50),
    Product(id = 7, name = "Table", description = "Foldable table", price = 199.99, quantity = 10),
]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Can't pass object product from products directly into db since it is a model.py class (pydantic)
# Need to map the object to database_models.py class (sqlalchemy)
# Key-value pair is accepted by Product() to convert product into database_models.py object
# .model_dump() gives dict from the object
# Unpacking is done by ** to convert dict to key-value pair
def init_db():
    db = SessionLocal()

    count = db.query(database_models.Product).count

    if count == 0:
        for product in products:
            db.add(database_models.Product(**product.model_dump()))
        
        # Since we set autocommit = False
        db.commit()

init_db()


@app.get("/products")       # /x is an endpoint (/ = Home page)
def get_all_products(db: Session = Depends(get_db)):
    # db = session() NOT required anymore
    # db.query()

    db_products = db.query(database_models.Product).all()
    return db_products


@app.get("/products/{id}")
def get_one_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        return db_product
    
    return "Product not found."
    #raise HTTPException(status_code=404, detail="Product not found")
    

@app.post("/products")
def add_product(product: Product, db: Session = Depends(get_db)):
    db.add(database_models.Product(**product.model_dump()))
    db.commit()
    return product


@app.put("/products/{id}")
def update_product(id: int, product: Product, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()

    if db_product:
        db_product.name = product.name
        db_product.description = product.description
        db_product.price = product.price
        db_product.quantity = product.quantity
        db.commit()
        return "Product updated successfully."

    return "Product not found."
    

@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()

    if db_product:
        db.delete(db_product)
        db.commit()
        return "Product deleted."
        
    return "Product not found."