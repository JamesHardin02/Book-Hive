from pydantic import BaseModel, Field


class LowStockThresholdOut(BaseModel):
    threshold: int


class LowStockThresholdIn(BaseModel):
    threshold: int = Field(ge=0, le=100000)
