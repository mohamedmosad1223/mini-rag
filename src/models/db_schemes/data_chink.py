from pydantic import BaseModel,Field,validator
from typing import Optional,Any
from bson.objectid import ObjectId

class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")

    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId



    class Config:
        arbitrary_types_allowed = True
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key":[ # take one or more fields to index
                    ("chunk_project_id", 1) # the object is indexed in ascending order
                ],
                "name":"chunk_project_id_index_1",
                "unique": False
            }
            ]
