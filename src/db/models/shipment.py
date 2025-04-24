from sqlmodel import Field, Relationship, SQLModel

from src.db.enums import ShipmentStatus


class Article(SQLModel, table=True):
    __tablename__ = "article"

    id: int = Field(default=None, primary_key=True)
    shipment_id: int | None = Field(default=None, foreign_key="shipment.id")
    name: str
    quantity: int | None = None
    price: float | None = None
    sku: str = Field(index=True)

    shipment: "Shipment" = Relationship(back_populates="articles")


class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"

    id: int | None = Field(default=None, primary_key=True)
    tracking_number: str = Field(unique=True, index=True)
    carrier: str | None = Field(default=None, index=True)
    sender_address: str | None = None
    receiver_address: str
    status: ShipmentStatus = Field(index=True)

    articles: list[Article] = Relationship(back_populates="shipment")
