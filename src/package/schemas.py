# Pydantic models
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


# Pydantic data validator
class TodoRequest(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    complete: bool = False

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"title": "Drink Water", "description": "Get a glass of water and drink it", "complete": False}
        }
    )


class TodoRead(BaseModel):
    id: int
    title: str
    description: str
    complete: bool

    model_config = ConfigDict(from_attributes=True)
