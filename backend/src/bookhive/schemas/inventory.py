from pydantic import BaseModel, ConfigDict, Field

from bookhive.schemas.locations import LocationOut


class InventoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    book_id: int
    on_hand: int
    min_threshold: int | None = None
    location: LocationOut | None


class StockAdjustIn(BaseModel):
    delta: int = Field(..., description="Positive to add stock, negative to remove stock")
    reason: str = Field(min_length=1, max_length=255)


class ThresholdUpdateIn(BaseModel):
    min_threshold: int | None = Field(
        default=None,
        description="Per-book low-stock threshold. Null clears custom threshold (falls back to default).",
        ge=0,
        le=100000,
    )
