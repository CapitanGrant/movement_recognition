from fastapi import FastAPI
from app.opencv_cam.router import router

app = FastAPI()

app.include_router(router)
