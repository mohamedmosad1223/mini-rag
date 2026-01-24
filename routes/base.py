from fastapi import FastAPI , APIRouter
from dotenv import load_dotenv
import os
load_dotenv(".env")
base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"]
)
app =FastAPI()
# to cheak your app
@base_router.get("/")
async def welcome():
    app_name=os.getenv("APP_NAME")
    app_version=os.getenv("APP_VERSION")
    return {
        "app_name": app_name,
        "app_version": app_version
    }
