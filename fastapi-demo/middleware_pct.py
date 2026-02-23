from fastapi import FastAPI, Request
import time

app = FastAPI()

@app.middleware("http")
async def addMiddleware(request: Request, call_next):
    print("Middleware Work!")
    response = await call_next(request)
    return response

@app.get("/")
async def index():
    return {"message": "Hello World!"}

@app.get("/{name}")
async def hello(name: str):
    return {"message": f"Hello {name}"}
