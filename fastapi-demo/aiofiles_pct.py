from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
import aiofiles
import os
import asyncio
from fastapi.responses import StreamingResponse

app = FastAPI()

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
@app.post("/write")
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
    

@app.post("/append")
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
  
   

@app.post("/read/${fileName}")
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

@app.get('/stream/${fileName}')
async def stream_file(fileName: str):
    file_path = os.path.join(BASE_DIR, fileName)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found!")
    
    return StreamingResponse(file_streamer(file_path), media_type="text/plain")
    

@app.post("/read-multiple")
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
  

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    async with aiofiles.open(f"{file.filename}", mode="wb") as out_file:
        while content := await file.read(1024):  # Read in chunks asynchronously
            await out_file.write(content)
    async with aiofiles.open(f"{file.filename}", mode='r') as f:
        content = await f.read()

    return {"filename": file.filename, "content_type": file.content_type, "content": content}

@app.get("/readfile/{filename}")
async def read_file(filename: str):
    try:
        async with aiofiles.open(f"{filename}", mode="r") as in_file:
            content = await in_file.read()
        return {"filename": filename, "content": content}
    except FileNotFoundError:
        return {"message": "File not found"}
