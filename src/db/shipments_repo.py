from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import and_, select

from src.api.schemas.shipment import ArticleCreate, ShipmentCreate
from src.db.models.shipment import Article as ArticleModel, Shipment as ShipmentModel


class ShipmentsRepo:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def fetch_all(self) -> Sequence[ShipmentModel]:
        stmt = select(ShipmentModel).options(selectinload(ShipmentModel.articles))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_one_by_tracking(self, tracking_number: str) -> ShipmentModel | None:
        stmt = (
            select(ShipmentModel)
            .options(selectinload(ShipmentModel.articles))
            .where(
                ShipmentModel.tracking_number == tracking_number,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def filter_by_carrier(self, carrier: str) -> Sequence[ShipmentModel]:
        stmt = (
            select(ShipmentModel).options(selectinload(ShipmentModel.articles)).where(ShipmentModel.carrier == carrier)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def find_one_by_params(self, tracking_number: str, carrier: str) -> ShipmentModel | None:
        stmt = (
            select(ShipmentModel)
            .options(selectinload(ShipmentModel.articles))
            .where(and_(ShipmentModel.tracking_number == tracking_number, ShipmentModel.carrier == carrier))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_shipment(self, shipment: ShipmentCreate, articles: list[ArticleCreate]) -> ShipmentModel:
        db_shipment = ShipmentModel(
            tracking_number=shipment.tracking_number,
            carrier=shipment.carrier,
            sender_address=shipment.sender_address,
            receiver_address=shipment.receiver_address,
            status=shipment.status,
        )
        self.db.add(db_shipment)
        await self.db.flush()  # Get the ID without committing

        for article in articles:
            db_article = ArticleModel(
                shipment_id=db_shipment.id,
                name=article.name,
                quantity=article.quantity,
                price=article.price,
                sku=article.sku,
            )
            self.db.add(db_article)

        await self.db.commit()
        await self.db.refresh(db_shipment)
        return db_shipment
