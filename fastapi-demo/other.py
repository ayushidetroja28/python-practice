from fastapi import FastAPI, Path, Form, Cookie, Header
import uvicorn
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse

app = FastAPI()

class User(BaseModel):
    username: str
    password: str

class Student(BaseModel):
    id: int
    name: str = Field(None, title="Name of student", max_length=10, min_length=3)
    subjects: List[str] = []
    marks: List[int] = []
    percent_marks: float

class percent(BaseModel):
   id:int
   name :str = Field(None, title="name of student", max_length=10)
   percent_marks: float

@app.post("/marks", response_model=percent)
async def get_parcent(s1:Student):
    s1.percent_marks = sum(s1.marks)/2
    return s1

@app.get("/headers/")
async def read_header(accept_language: Optional[str] = Header(None)):
   return {"Accept-Language": accept_language} 

@app.get("/rspheader/")
def set_rsp_headers():
   content = {"message": "Hello World"}
   headers = {"X-Web-Framework": "FastAPI", "Content-Language": "en-US"}
   return JSONResponse(content=content, headers=headers)

@app.post("/add_cookie/")
async def create_cookie():
    content= {"message" : "Cookie set"}
    response = JSONResponse(content=content)
    response.set_cookie(key="username", value="admin")
    return response

@app.post("/get_cookie/")
async def get_cookie(username : str= Cookie(None)):
    return username

@app.post("/login/", response_model=User)
async def login_form(nm: str = Form(...), pwd: str = Form(...)):
    return User(username=nm, password=pwd)

@app.post("/student/")
async def student_data(s1: Student):
    return s1

@app.post("/students/{college}")
async def student_data(college:str, age:int, student:Student):
   retval={"college":college, "age":age, **student.dict()}
   return retval

@app.get("/")
async def index():
    return {"message": "Hello Ayushi!"}

@app.get("/hello/${name}/${age}")
async def hello(name:str=Path(..., min_length = 3, max_length = 10), age:int = Path(..., ge=1, le=100)):
    return {"name": name, "age": age}