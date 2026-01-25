from fastapi import FastAPI , APIRouter, Depends,UploadFile, status
from fastapi.responses import JSONResponse
from helpers.config import get_settings , Settings
from controllers.DataController import DataController
from controllers.ProjectController import ProjectController
import aiofiles
import os
from models import ResponseSignal
import logging

logger = logging.getLogger("uvicorn-error")
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1_data"]
)

@data_router.post("/upload/{project_id}")
async def upload_project(project_id :str, file:UploadFile
                         ,app_settigs: Settings = Depends(get_settings)):
    data_controller=DataController()
    #file type and size validation
    is_valid, result_signal=data_controller.validate_uploaded_file(file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": result_signal.value
            }
        )


    project_dir_path=ProjectController().get_project_path(project_id)
    file_path=data_controller.generate_unique_filename(
        orig_file_name=file.filename,
        project_id=project_id
    )
    try:
        async with aiofiles.open(file_path, 'wb') as f:

            while chunk := await file.read(app_settigs.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )

    return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value
            }
        )