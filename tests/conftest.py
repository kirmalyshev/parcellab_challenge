import os

from typing import AsyncGenerator
from unittest.mock import Mock

import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session
from sqlmodel import SQLModel, text

from src.api.schemas.shipment import ArticleCreate, ShipmentCreate
from src.db.enums import ShipmentStatus


@pytest.fixture
def mock_db():
    return Mock(spec=Session)


@pytest.fixture
def mock_redis():
    return Mock()


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
    if not TEST_DATABASE_URL:
        raise ValueError("TEST_DATABASE_URL environment variable is not set")

    postgres_url = TEST_DATABASE_URL.replace("/parcellab_test", "/postgres")

    postgres_engine = create_async_engine(
        postgres_url,
        echo=False,
    )

    # Create test DB
    try:
        async with postgres_engine.begin() as conn:
            await conn.execute(text("COMMIT"))  # Commit any transaction first
            await conn.execute(text("CREATE DATABASE parcellab_test"))
    except Exception as e:
        if "already exists" not in str(e):
            raise e

    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    try:
        async with async_session() as session:
            yield session
    finally:
        await session.close()


@pytest.fixture
def weather_data_stub():
    return {"weather": [{"description": "clear sky"}], "main": {"temp": 20.5}, "name": "Paris"}


@pytest.fixture
def shipments_stub() -> list[ShipmentCreate]:
    """Create specific shipments with predefined data."""
    shipments = []

    # Shipment 1: TN12345678
    shipment1 = ShipmentCreate(
        tracking_number="TN12345678",
        carrier="DHL",
        sender_address="Street 10, 75001 Paris, France",
        receiver_address="Lisa-Fittko-Str 13, 10557 Berlin, Germany",
        status=ShipmentStatus.in_transit,
        articles=[
            ArticleCreate(name="Laptop", quantity=1, price=800.0, sku="LP123"),
            ArticleCreate(name="Mouse", quantity=1, price=25.0, sku="MO456"),
        ],
    )
    shipments.append(shipment1)

    # Shipment 2: TN12345679
    shipment2 = ShipmentCreate(
        tracking_number="TN12345679",
        carrier="UPS",
        sender_address="Street 2, 20144 Hamburg, Germany",
        receiver_address="Street 20, 1000 Brussels, Belgium",
        status=ShipmentStatus.inbound_scan,
        articles=[ArticleCreate(name="Monitor", quantity=2, price=200.0, sku="MT789")],
    )
    shipments.append(shipment2)

    # Shipment 3: TN12345680
    shipment3 = ShipmentCreate(
        tracking_number="TN12345680",
        carrier="DPD",
        sender_address="Street 3, 80331 Munich, Germany",
        receiver_address="Street 5, 28013 Madrid, Spain",
        status=ShipmentStatus.delivery,
        articles=[
            ArticleCreate(name="Keyboard", quantity=1, price=50.0, sku="KB012"),
            ArticleCreate(name="Mouse", quantity=1, price=25.0, sku="MO456"),
        ],
    )
    shipments.append(shipment3)

    # Shipment 4: TN12345681
    shipment4 = ShipmentCreate(
        tracking_number="TN12345681",
        carrier="FedEx",
        sender_address="Street 4, 50667 Cologne, Germany",
        receiver_address="Street 9, 1016 Amsterdam, Netherlands",
        status=ShipmentStatus.transit,
        articles=[
            ArticleCreate(name="Laptop", quantity=1, price=900.0, sku="LP345"),
            ArticleCreate(name="Headphones", quantity=1, price=100.0, sku="HP678"),
        ],
    )
    shipments.append(shipment4)

    # Shipment 5: TN12345682
    shipment5 = ShipmentCreate(
        tracking_number="TN12345682",
        carrier="GLS",
        sender_address="Street 5, 70173 Stuttgart, Germany",
        receiver_address="Street 15, 1050 Copenhagen, Denmark",
        status=ShipmentStatus.scanned,
        articles=[
            ArticleCreate(name="Smartphone", quantity=1, price=500.0, sku="SP901"),
            ArticleCreate(name="Charger", quantity=1, price=20.0, sku="CH234"),
        ],
    )
    shipments.append(shipment5)

    return shipments
