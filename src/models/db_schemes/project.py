from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from bson import ObjectId


class Project(BaseModel):
   
    id: Optional[ObjectId] = Field(default=None, alias="_id")

    project_id: str = Field(..., min_length=1)

    @field_validator("project_id")
    @classmethod
    def validate_project_id(cls, v):
        if not v.isalnum():
            raise ValueError("project_id must be alphanumeric")
        return v

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key":[ # take one or more fields to index
                    ("project_id", 1) # the object is indexed in ascending order
                ],
                "name":"project_id_index_1",
                "unique": True
            }
            ]
