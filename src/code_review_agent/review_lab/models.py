"""Contract models for messages received by the checkout example."""

from pydantic import BaseModel, ConfigDict, Field


class CheckoutRequest(BaseModel):
    """Validate a client request before it reaches the receipt builder."""

    model_config = ConfigDict(extra="ignore")

    sku: str = Field(min_length=1)
    quantity: int = Field(gt=0)
