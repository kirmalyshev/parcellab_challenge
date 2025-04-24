from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field

from src.db.enums import ShipmentStatus


class ArticleBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    quantity: int
    price: float
    sku: str


class ArticleCreate(ArticleBase):
    pass


class Article(ArticleBase):
    id: int


class ShipmentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tracking_number: str
    carrier: str
    sender_address: str
    receiver_address: str
    status: ShipmentStatus


class ShipmentCreate(ShipmentBase):
    articles: list[ArticleCreate] = Field(default_factory=list)


class Shipment(ShipmentBase):
    id: int
    articles: list[Article] = Field(default_factory=list)


class ShipmentWithWeather(Shipment):
    weather: dict | None = None


class ShipmentsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    shipments: Sequence[Shipment]
