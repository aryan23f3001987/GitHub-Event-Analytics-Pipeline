from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "GitHub Event Analytics Pipeline is running"}