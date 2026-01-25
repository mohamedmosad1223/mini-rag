from fastapi import FastAPI
from routes import base
from dotenv import load_dotenv

load_dotenv(".env")
app =FastAPI()

# @app.get("/welcome")
# def welcome():
#     return {
#         "message": "Welcome to the API"
#     }
app.include_router(base.base_router)
