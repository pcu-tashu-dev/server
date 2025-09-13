from fastapi import FastAPI
import uvicorn
import os

app = FastAPI()

@app.get("/")
async def index():
    return {"message": "Welcome!"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000 if os.path.exists("./is-server") else 3000,
        reload=not os.path.exists("./is-server"),
    )