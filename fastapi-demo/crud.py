from fastapi import FastAPI,status, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List
from pymongo.errors import PyMongoError

app = FastAPI()
client = MongoClient()
data = []

class Book(BaseModel):
    id: int
    title: str
    author: str
    publisher: str
    _id: str

class BookListResponse(BaseModel):
    status: str
    count: int
    data: List[Book]

DB = "library_db"              # database name
BOOK_COLLECTION = "books"      # collection name

# Helper: Convert MongoDB object
def convert_mongo_book(book):
    book["_id"] = str(book["_id"])
    return book

@app.post("/add_book", status_code=status.HTTP_201_CREATED)
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

    # data.append(book.dict())
    # return {"message": "Book added successfully", "data": data}


@app.get("/get_book", response_model=BookListResponse)
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


@app.get("/get_book_by_id/${id}")
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


@app.put("/update_book/${id}")
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
        

@app.delete("/delete_book/${id}")
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