from pydantic import BaseModel

# Pydantic product class ; different syntax from sqlalchemy, requires database_model.py
class Product(BaseModel):   
    id: int
    name: str
    description: str
    price: float
    quantity: int