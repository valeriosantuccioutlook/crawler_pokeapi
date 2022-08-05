import uvicorn
from fastapi import FastAPI
from crawler_api.v1.main import app

crawler_api = FastAPI()
crawler_api.mount("/v1", app)

if __name__ == "__main__":
    uvicorn.run("main:crawler_api", reload=True)
