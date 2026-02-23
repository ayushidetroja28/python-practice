from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

async def fake_video_streamer():
    for i in range(10):
        yield f"some fake video bytes {i}\n".encode()

@app.get("/video-stream")
async def main():
    return StreamingResponse(fake_video_streamer(), media_type="video/mp4")