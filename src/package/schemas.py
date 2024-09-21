# Pydantic models
from pydantic import BaseModel
from pydantic import Field


# Pydantic data validator
class TodoRequest(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    complete: bool = False

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {"title": "Drink Water", "description": "Get a glass of water and drink it", "complete": False}
        }
