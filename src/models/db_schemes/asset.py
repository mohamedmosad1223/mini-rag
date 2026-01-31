from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from bson import ObjectId
from datetime import datetime

class Asset(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    asset_project_id :ObjectId
    asset_type: str = Field(..., min_length=1)
    asset_name: str = Field(..., min_length=1)
    asset_size: int = Field(ge=0, default=None)
    asset_config: dict = Field(default=None)
    asset_pushed_at: datetime = Field(default_factory=datetime.utcnow)


    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key":[ # take one or more fields to index
                    ("asset_project_id", 1) # the object is indexed in ascending order
                ],
                "name":"asset_project_id_index_1",
                "unique": False
            },
             {
                "key":[ # take one or more fields to index
                    ("asset_project_id", 1), # the object is indexed in ascending order
                    ("asset_name", 1)
                ],
                "name":"asset_project_id_asset_name_index_1",
                "unique": True
            },

            ]
