from typing import Tuple
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
   "http://192.168.211.:8000",
   "http://localhost",
   "http://localhost:8080",
]

app.add_middleware(
   CORSMiddleware,
   allow_origins=origins,
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)

class supplier(BaseModel):
    supplierID: int
    supplierName: str

class product(BaseModel):
    productID: int
    productName: str
    productPrice: int
    supp: supplier

class customer(BaseModel):
    custID: int
    custname: str
    prod: Tuple[product]

class dependency:
   def __init__(self, id: str, name: str, age: int):
      self.id = id
      self.name = name
      self.age = age 

async def dependency(id: str, name: str, age: int):
   return {"id": id, "name": name, "age": age}

async def validate(dep: dependency = Depends(dependency)):
   if dep.age > 18:
      raise HTTPException(status_code=400, detail="You are not eligible")

@app.get("/user/", dependencies=[Depends(validate)])
async def user():
   return {"message": "You are eligible"}

@app.get("/admin/")
async def admin(dep: dependency = Depends(dependency)):
   return dep 


@app.post("/invoice")
async def getInvoice(c1: customer):
    return c1