import uuid
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Post(BaseModel):
    postID: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    userID: str
    title: Optional[str]
    date: Optional[datetime] = Field(default_factory=datetime.utcnow().timestamp)
    file: str

    class Config:
        schema_extra = {
            "example": {
                "title": "title",
            }
        }


class UpdatePostModel(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    file: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "title": "title",
                "description": "description",
                "file": "file"
            }
        }