# Pydantic models
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class TodoRequest(BaseModel):
    """Payload to create or update a todo (`POST /todos`, `PUT /todos/{id}`)."""

    title: str = Field(
        description="Short title of the todo. Must be at least 1 character.",
        min_length=1,
        examples=["Drink Water"],
    )
    description: str = Field(
        description="Longer description of the todo (1 to 100 characters).",
        min_length=1,
        max_length=100,
        examples=["Get a glass of water and drink it"],
    )
    complete: bool = Field(
        default=False,
        description="Whether the todo has been completed.",
        examples=[False],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Drink Water",
                "description": "Get a glass of water and drink it",
                "complete": False,
            }
        }
    )


class TodoRead(BaseModel):
    """A todo row as returned by the API."""

    id: int = Field(description="Database id of the todo.", examples=[1])
    title: str = Field(description="Short title of the todo.", examples=["Drink Water"])
    description: str = Field(
        description="Longer description of the todo.", examples=["Get a glass of water and drink it"]
    )
    complete: bool = Field(description="Whether the todo has been completed.", examples=[False])

    model_config = ConfigDict(from_attributes=True)
