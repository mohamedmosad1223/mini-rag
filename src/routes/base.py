from fastapi import FastAPI , APIRouter, Depends
from helpers.config import get_settings , Settings
import os

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"]
)
app =FastAPI()
# to cheak your app
@base_router.get("/")
async def welcome(app_settigs: Settings = Depends(get_settings)):
    # app_settigs=get_settings() insted of this use depend to ensure that the settings are loaded correctly

    app_name=app_settigs.APP_NAME
    app_version=app_settigs.APP_VERSION

    return {
        "app_name": app_name,
        "app_version": app_version
    }
