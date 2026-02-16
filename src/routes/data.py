from fastapi import FastAPI , APIRouter, Depends,UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings , Settings
from controllers.DataController import DataController
from controllers.ProjectController import ProjectController
from controllers.Process_Controller import ProcessController
from .schemes.data import ProcessRequest
import aiofiles
import os
from models import ResponseSignal
import logging
from models.ProjectModel import ProjectModel
from models.db_schemes import DataChunk, Asset
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.enums.AsseetTypeEnum import AssetTypeEnum
from controllers import NLPController
logger = logging.getLogger("uvicorn-error")
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1_data"]
)

@data_router.post("/upload/{project_id}")
async def upload_project(request:Request,project_id :int, file:UploadFile
                         ,app_settigs: Settings = Depends(get_settings)):
    project_model=await ProjectModel.create_instance(db_client=request.app.db_client)

    project= await project_model.get_project_or_create_one(project_id=project_id)
    
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
    file_path, file_id=data_controller.generate_unique_filepath(
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
    # store asset into database
    asset_model=await AssetModel.create_instance(db_client=request.app.db_client)
    asset_resource=Asset(
        asset_name=file_id,
        asset_project_id=project.project_id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_size=os.path.getsize(file_path)
    )

    asset_resource=await asset_model.create_asset(asset_resource)
    return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": str(asset_resource.asset_name),
            }
        )

@data_router.post("/process/{project_id}")
async def process_endpoint(request:Request, project_id:int, process_request:ProcessRequest):

    chunk_size=process_request.chunk_size
    overlap_size=process_request.overlap_size
    do_reset=process_request.do_reset
    project_model=await ProjectModel.create_instance(db_client=request.app.db_client)

    project= await project_model.get_project_or_create_one(project_id=project_id)

    nlp_controller=NLPController(
        vectordb_client=request.app.vectordb_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generation_client,
        template_parser=request.app.template_parser,

    )
    chunk_model=await ChunkModel.create_instance(db_client=request.app.db_client)
    asset_model=await AssetModel.create_instance(db_client=request.app.db_client)

    project_files_id={}
    if process_request.file_id :
        asset_record=await asset_model.get_asset_record(
            asset_project=project.project_id,
            asset_name=process_request.file_id
        )
        project_files_id=[process_request.file_id]
        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.FILE_NOT_FOUND.value
                }
            )
        project_files_id={
            asset_record.asset_id:asset_record.asset_name
        }
        

    else:
        project_files=await asset_model.get_all_project_asset(
            asset_project_id=project.project_id,
            asset_type=AssetTypeEnum.FILE.value
            )
        project_files_id={
            record.asset_id:record.asset_name
            for record in project_files 
        }
    if len( project_files_id)==0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.NO_FILES_TO_PROCESS.value
            }
        )
    

    process_controller=ProcessController(project_id=project_id)
    no_record=0
    no_files=0
    if do_reset ==1:
            collection_name=nlp_controller.create_collection_name(project_id=project.project_id)
            
            _= await request.app.vectordb_client.delete_collection(collection_name=collection_name)

            await chunk_model.delete_chunks_by_project_id(project_id=project.project_id)


    for asset_id,file_id in project_files_id.items():

        file_content=process_controller.get_file_content(file_id)
        if file_content is None :
            logger.error(f"Failed to load content for file_id: {file_id}")
            continue

        file_chunks=process_controller.process_file_content(file_id=file_id,file_content=file_content,chunk_size=chunk_size,overlap_size=overlap_size)

        if file_chunks is None or len(file_chunks)==0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.PROCESSING_FAILED.value
                }
            )
        file_chunks_records=[
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i+1,
                chunk_project_id=project.project_id
                ,chunk_asset_id=asset_id
            )
            for i, chunk in enumerate(file_chunks)
        ]

        no_record= await chunk_model.insert_many_chunks(file_chunks_records)
        no_files+=1
    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "number_of_chunks": no_record,
            "number_of_files": no_files
        }
    )


