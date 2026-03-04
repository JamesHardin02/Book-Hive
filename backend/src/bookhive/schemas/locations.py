from pydantic import BaseModel, ConfigDict, Field


class LocationCreate(BaseModel):
    aisle: str = Field(min_length=1, max_length=20)
    shelf: str = Field(min_length=1, max_length=20)


class LocationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    aisle: str
    shelf: str
