from fastapi import FastAPI
from routes import summarizer

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(summarizer.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)