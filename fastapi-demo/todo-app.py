from fastapi import FastAPI,status, HTTPException,  UploadFile, File, BackgroundTasks, Request,Depends, status, APIRouter
from pymongo import MongoClient
from typing import List
from pymongo.errors import PyMongoError
from pydantic import BaseModel
import aiofiles
import os
import asyncio
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from auth import create_access_token, get_current_user
from transformers import pipeline

app = FastAPI()

nlp = pipeline(
    task="sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

protected_router = APIRouter(
    dependencies=[Depends(get_current_user)]
)
client = MongoClient()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Add your production frontend URL here when deploying
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specific origins are best practice
    allow_credentials=True, # Allows cookies, authorization headers, etc.
    allow_methods=["*"],    # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],    # Allow all headers
)

# Define a Custom Exception:
class UnicornException(Exception):
    def __init__(self, name :str):
        self.name = name

# Register a Custom Handler
@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(status_code=418, content={"message": f"opps! {exc.name} did somting wrong, the server says 'I'm a teapot'."})

# Override the Default HTTPException Handler (Optional):
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_detail": exc.detail},
    )

class Book(BaseModel):
    id: int
    title: str
    author: str
    publisher: str
    _id: str

class TODO(BaseModel):
    title: str
    task: str
    time: str
    _id: str

class TODORES(BaseModel):
    title: str
    task: str
    time: str
    sentiment: list
    _id: str

class User(BaseModel):
    name: str
    username: str
    password: str
    _id: str

class BookListResponse(BaseModel):
    status: str
    count: int
    data: List[Book]

class TodoListResponse(BaseModel):
    status: str
    count: int
    data: List[TODORES]

class LoginModel(BaseModel):
    username: str
    password: str

DB = "library_db"              # database name
BOOK_COLLECTION = "books"      # collection name
USER_COLLECTION = "users"      # collection name
TODO_COLLECTION = "todos"      # collection name

# Helper: Convert MongoDB object
def convert_mongo_book(book):
    book["_id"] = str(book["_id"])
    return book

def convert_mongo_todo(todo):
    todo["_id"] = str(todo["_id"])
    return todo

@app.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: User):
    try:
        with MongoClient() as client:
            user_collection = client[DB][USER_COLLECTION]
            existing = user_collection.find_one({"username" : user.username})
            if existing:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{user.username} already exists")
            
            result = user_collection.insert_one(user.dict())
            if not result.acknowledged:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to insert the user")
            
            token = create_access_token({"sub": user.username})

            return {
                "status" : "success",
                "message": "User created successfully",
                "user_id": str(result.inserted_id),
                "access_token": token
            }
        
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@app.post("/login")
async def login(user: LoginModel):
    try:
        with MongoClient() as client:
            user_collection = client[DB][USER_COLLECTION]
            existing = user_collection.find_one({"username" : user.username})
            print("-----ss---", existing)
            if not existing:
                 raise HTTPException(status_code=401, detail="Invalid credentials")
            
            token = create_access_token({"sub": user.username})

            return {
                "status" : "success",
                "message": "User login successfully",
                "access_token": token
            }
        
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@protected_router.get("/users/me")
async def read_users_me(current_user= Depends(get_current_user)):
    return {"username": current_user}


@protected_router.get("/unicorn/${name}")
async def read_unicorn(name: str):
    if name == 'yolo':
        raise UnicornException(name='yolo')
    return {"unicorn_name": name}

@protected_router.post("/add_todo", status_code=status.HTTP_201_CREATED)
async def add_todo(todo: TODO):
    try:
        with MongoClient() as client:
            todo_collection = client[DB][TODO_COLLECTION]
            existing = todo_collection.find_one({"title" : todo.title})
            if existing:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Book with id {todo.title} already exists")
            
            result = todo_collection.insert_one(todo.dict())
            if not result.acknowledged:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to insert the todo")
                
            return {
                "status" : "success",
                "message": "Todo added successfully",
                "book_id": str(result.inserted_id)
            }
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@protected_router.get("/get_todo", response_model=TodoListResponse)
async def get_todo():
    try:
        with MongoClient() as client:
            todo_collection = client[DB][TODO_COLLECTION]
            # Get all todos
            todos = list(todo_collection.find())
            array = []
            for a in todos:
                r = nlp(a['title'])
                print("-r---",r)
                array.append({**a,  **{'sentiment': r}})
                # print("-------",a['title'])

            if array:
                return {
                    "status": "success",
                    "count": len(array),
                    "data": array
                }
            else:
                raise HTTPException( status_code=status.HTTP_200_OK, detail=f"Todo not found!")
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@protected_router.get("/get_todo_by_id/${id}")
async def get_todo_by_id(id: int):
    try:
        with MongoClient() as client:
            todo_collection = client[DB][TODO_COLLECTION]
            # Get all books
            todo = todo_collection.find_one({"_id": id})

            if todo:
                return {
                    "status": "success",
                    "data": convert_mongo_todo(todo)
                }
            else:
                raise HTTPException( status_code=status.HTTP_200_OK, detail=f"Todo not found!")
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@protected_router.put("/update_todo/${id}")
async def update_todo(id: int, todo: TODO):
    try:
        with MongoClient() as client:
            todo_collection = client[DB][TODO_COLLECTION]
            # Get all todos
            todos = todo_collection.find_one({"_id": id})

            if todos:
                update_data = todo.dict(exclude={"_id"})
                result = todo_collection.update_one({"_id": id}, {"$set": update_data})
                if result.modified_count == 0:
                    return {"status": "success", "message": "No changes applied"}
                
                return {"status": "success", "message": "Todo updated successfully"}
            else:
                raise HTTPException( status_code=status.HTTP_200_OK, detail=f"Todo not found!")
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
        

@protected_router.delete("/delete_todo/${id}")
async def delete_todo(id: int):
    try:
        with MongoClient() as client:
            todo_collection = client[DB][TODO_COLLECTION]
            # Get all todos
            result = todo_collection.delete_one({"_id": id})

            if result.deleted_count == 0:
                raise HTTPException(404, "Todo not found!")

            return {
                "status": "success",
                "message": f"Todo with id {id} deleted successfully"
            }
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    

@protected_router.post("/add_book", status_code=status.HTTP_201_CREATED)
async def add_book(book: Book):
    try:
        with MongoClient() as client:
            book_collection = client[DB][BOOK_COLLECTION]
            existing = book_collection.find_one({"id" : book.id})
            if existing:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Book with id {book.id} already exists")
            
            result = book_collection.insert_one(book.dict())
            if not result.acknowledged:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to insert the book")
                
            return {
                "status" : "success",
                "message": "Book added successfully",
                "book_id": str(result.inserted_id)
            }
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@protected_router.get("/get_book", response_model=BookListResponse)
async def get_book():
    try:
        with MongoClient() as client:
            book_collection = client[DB][BOOK_COLLECTION]
            # Get all books
            books = list(book_collection.find())

            if books:
                return {
                    "status": "success",
                    "count": len(books),
                    "data": books
                }
            else:
                raise HTTPException( status_code=status.HTTP_200_OK, detail=f"Book not found!")
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@protected_router.get("/get_book_by_id/${id}")
async def get_book(id: int):
    try:
        with MongoClient() as client:
            book_collection = client[DB][BOOK_COLLECTION]
            # Get all books
            book = book_collection.find_one({"id": id})

            if book:
                return {
                    "status": "success",
                    "data": convert_mongo_book(book)
                }
            else:
                raise HTTPException( status_code=status.HTTP_200_OK, detail=f"Book not found!")
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@protected_router.put("/update_book/${id}")
async def update_book(id: int, book: Book):
    try:
        with MongoClient() as client:
            book_collection = client[DB][BOOK_COLLECTION]
            # Get all books
            book1 = book_collection.find_one({"id": id})

            if book1:
                update_data = book.dict(exclude={"_id"})
                result = book_collection.update_one({"id": id}, {"$set": update_data})
                if result.modified_count == 0:
                    return {"status": "success", "message": "No changes applied"}
                
                return {"status": "success", "message": "Book updated successfully"}
            else:
                raise HTTPException( status_code=status.HTTP_200_OK, detail=f"Book not found!")
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
        

@protected_router.delete("/delete_book/${id}")
async def delete_book(id: int):
    try:
        with MongoClient() as client:
            book_collection = client[DB][BOOK_COLLECTION]
            # Get all books
            result = book_collection.delete_one({"id": id})

            if result.deleted_count == 0:
                raise HTTPException(404, "Book not found!")

            return {
                "status": "success",
                "message": f"Book with id {id} deleted successfully"
            }
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    

class FileContent(BaseModel):
    fileName : str
    content: str

BASE_DIR = "files"
os.makedirs(BASE_DIR, exist_ok=True)


# ----------------------------------------------------------
# Background Task: Log every write/append operation
# ----------------------------------------------------------
async def log_operation(fileName: str, operation: str):
    log_path = os.path.join(BASE_DIR, "logs.txt")
    async with aiofiles.open(log_path, 'a') as f:
        await f.write(f"{operation.upper()} -> {fileName}\n" )


# ----------------------------------------------------------
# ASYNC WRITE FILE + BACKGROUND LOG
# ----------------------------------------------------------
@protected_router.post("/write")
async def write_file(data: FileContent, background: BackgroundTasks):
    file_path = os.path.join(BASE_DIR, data.fileName)
    try:
        async with aiofiles.open(file_path, mode='w') as f:
            await f.write(data.content)

        # Add background task
        background.add_task(log_operation, data.fileName, "write")
        return {"message": "File writter successfully", "file": data.fileName}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@protected_router.post("/append")
async def write_file(data: FileContent, background : BackgroundTasks):
    file_path = os.path.join(BASE_DIR, data.fileName)
    try:
        async with aiofiles.open(file_path, mode='a') as f:
            await f.write(data.content)

        # Add background log
        background.add_task(log_operation, data.fileName, "append")

        return {"message": "File append successfully", "file": data.fileName}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
  
   

@protected_router.post("/read/${fileName}")
async def read_file(fileName: str):
    file_path = os.path.join(BASE_DIR, fileName)
    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found!")
        
        async with aiofiles.open(file_path, mode='r') as f:
            content = await f.read()
        return {"fileName": fileName, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def file_streamer(path):
    async with aiofiles.open(path, 'rb') as f:
        chunk = await f.read(1024)
        print("------chunk-----", chunk)
        while chunk:
            yield chunk
            chunk = await f.read(1024)

@protected_router.get('/stream/${fileName}')
async def stream_file(fileName: str):
    file_path = os.path.join(BASE_DIR, fileName)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found!")
    
    return StreamingResponse(file_streamer(file_path), media_type="text/plain")
    

@protected_router.post("/read-multiple")
async def read_multiple_file(files : list[str]):

    async def read_file_async(path):
        async with aiofiles.open(path, mode='r') as f:
            return await f.read()
        
    tasks = []
    for fileName in files:
        file_path = os.path.join(BASE_DIR, fileName)
        if not os.path.exists(file_path):
            raise HTTPException(status_code= 400, detail="File not found!")
        tasks.append(read_file_async(file_path))

    result = await asyncio.gather(*tasks)
    return {"Files": files, "result" : result}
  

@protected_router.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    async with aiofiles.open(f"{file.filename}", mode="wb") as out_file:
        while content := await file.read(1024):  # Read in chunks asynchronously
            await out_file.write(content)
    async with aiofiles.open(f"{file.filename}", mode='r') as f:
        content = await f.read()

    return {"filename": file.filename, "content_type": file.content_type, "content": content}

@protected_router.get("/readfile/{filename}")
async def read_file(filename: str):
    try:
        async with aiofiles.open(f"{filename}", mode="r") as in_file:
            content = await in_file.read()
        return {"filename": filename, "content": content}
    except FileNotFoundError:
        return {"message": "File not found"}

app.include_router(protected_router)
