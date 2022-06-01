from fastapi import FastAPI
from app.routers.camera import camera
from app.config.app_config import info_app


app = FastAPI(**info_app)

app.include_router(camera)