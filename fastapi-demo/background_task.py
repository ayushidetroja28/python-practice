from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

def write_log(message: str):
    with open("log.txt", mode="a") as log:
        log.write(message)

@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    message = f"Notification sent to {email}\n"
    background_tasks.add_task(write_log, message)
    return {"message": "Notification sent"}