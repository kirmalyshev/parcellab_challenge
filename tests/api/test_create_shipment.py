import pytest

from fastapi import Response
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.api.routes.shipments import create_shipment as create_shipment_route
from src.db.models.shipment import Shipment as ShipmentModel


@pytest.mark.asyncio
async def test_create_shipment(test_db: AsyncSession, shipments_stub):
    """Test creating shipments via the API route with a real database."""
    for shipment in shipments_stub[0:1]:
        result = await create_shipment_route(
            shipment=shipment, articles=shipment.articles, response=Response(), db=test_db
        )

        assert result.tracking_number == shipment.tracking_number
        assert result.carrier == shipment.carrier
        assert result.sender_address == shipment.sender_address
        assert result.receiver_address == shipment.receiver_address
        assert result.status == shipment.status
        assert len(result.articles) == len(shipment.articles)

        for created_article, expected_article in zip(result.articles, shipment.articles, strict=False):
            assert created_article.name == expected_article.name
            assert created_article.quantity == expected_article.quantity
            assert created_article.price == expected_article.price
            assert created_article.sku == expected_article.sku

        stmt = (
            select(ShipmentModel)
            .options(selectinload(ShipmentModel.articles))
            .where(
                ShipmentModel.tracking_number == shipment.tracking_number,
            )
        )
        result = await test_db.execute(stmt)
        saved_shipment = result.scalar_one_or_none()

        assert saved_shipment is not None
        assert saved_shipment.tracking_number == shipment.tracking_number
        assert saved_shipment.carrier == shipment.carrier
        assert saved_shipment.sender_address == shipment.sender_address
        assert saved_shipment.receiver_address == shipment.receiver_address
        assert saved_shipment.status == shipment.status
        assert len(saved_shipment.articles) == len(shipment.articles)
