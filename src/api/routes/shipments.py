import logging

from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.shipment import ArticleCreate, Shipment, ShipmentCreate, ShipmentsResponse, ShipmentWithWeather
from src.config.redis import get_redis
from src.db.session import get_db
from src.db.shipments_repo import ShipmentsRepo
from src.services.weather_service import WeatherService


router = APIRouter()

logger = logging.getLogger()


@router.get("/shipments/", response_model=ShipmentsResponse)
async def find_shipments(carrier: str = "", db: AsyncSession = Depends(get_db)):
    repo = ShipmentsRepo(db)

    if carrier:
        db_shipments = await repo.filter_by_carrier(carrier=carrier)
    else:
        db_shipments = await repo.fetch_all()
    if not db_shipments:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="No shipments found")
    return ShipmentsResponse(shipments=[Shipment.model_validate(db_obj) for db_obj in db_shipments])


@router.get("/shipments/{tracking_number}", response_model=ShipmentWithWeather)
async def get_one_shipment(tracking_number: str, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    if not tracking_number:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Tracking number is required")

    repo = ShipmentsRepo(db)
    db_shipment = await repo.get_one_by_tracking(tracking_number=tracking_number)
    if not db_shipment:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Shipment not found")
    logger.info(f"{db_shipment.receiver_address=}")

    weather_service = WeatherService(redis)
    try:
        weather = await weather_service.get_weather(address=db_shipment.receiver_address)
    except Exception as err:
        logger.exception(err)
        weather = None
    shipment = Shipment.model_validate(db_shipment)
    return ShipmentWithWeather(**shipment.model_dump(), weather=weather)


@router.post("/shipments/", response_model=Shipment, status_code=HTTPStatus.CREATED)
async def create_shipment(
    shipment: ShipmentCreate,
    articles: List[ArticleCreate],
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    repo = ShipmentsRepo(db)
    if found_shipment := await repo.get_one_by_tracking(shipment.tracking_number):
        response.status_code = HTTPStatus.NO_CONTENT
        return found_shipment

    created = await repo.create_shipment(shipment, articles)
    return Shipment.model_validate(created)
