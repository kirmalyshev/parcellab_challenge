from http import HTTPStatus
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio

from fastapi import HTTPException, Response

from src.api.routes.shipments import create_shipment as create_shipment_route, find_shipments, get_one_shipment
from src.services.weather_service import WeatherService


@pytest_asyncio.fixture(scope="function")
async def created_shipments(test_db, shipments_stub):
    """Create shipments in the test database."""
    for shipment in shipments_stub:
        # TODO direct insert into DB
        await create_shipment_route(shipment=shipment, articles=shipment.articles, response=Response(), db=test_db)


@pytest.mark.asyncio
class TestGetOne:
    async def test_get_shipment_not_found(self, test_db, mock_redis):
        with pytest.raises(HTTPException) as exc_info:
            await get_one_shipment(tracking_number="NONEXISTENT", db=test_db, redis=mock_redis)

        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert exc_info.value.detail == "Shipment not found"

    async def test_no_number_passed(self, test_db, mock_redis, created_shipments):
        """Test filtering shipments by carrier."""
        # Act
        with pytest.raises(HTTPException) as exc_info:
            await get_one_shipment(tracking_number="", db=test_db, redis=mock_redis)

        # Assert
        assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
        assert exc_info.value.detail == "Tracking number is required"

    async def test_get_shipment_with_weather(self, test_db, mock_redis, created_shipments, weather_data_stub):
        mock_weather_service = Mock(spec=WeatherService)
        mock_weather_service.get_weather = AsyncMock(return_value=weather_data_stub)

        with (
            patch("src.api.routes.shipments.WeatherService", return_value=mock_weather_service),
        ):
            # Act
            result = await get_one_shipment(tracking_number="TN12345681", db=test_db, redis=mock_redis)

            # Assert
            assert result.tracking_number == "TN12345681"
            assert result.carrier == "FedEx"
            assert result.weather == weather_data_stub
            assert len(result.articles) == 2
            mock_weather_service.get_weather.assert_called_once_with(address="Street 9, 1016 Amsterdam, Netherlands")

    async def test_get_shipment_weather_service_error(self, test_db, mock_redis, created_shipments):
        # Mock the weather service to raise an exception
        mock_weather_service = Mock(spec=WeatherService)
        mock_weather_service.get_weather = AsyncMock(side_effect=Exception("Weather service error"))

        with (
            patch("src.api.routes.shipments.WeatherService", return_value=mock_weather_service),
        ):
            # Act
            result = await get_one_shipment(tracking_number="TN12345680", db=test_db, redis=mock_redis)

            assert result.tracking_number == "TN12345680"
            assert result.weather is None

            # Assert
            mock_weather_service.get_weather.assert_called_once_with(address="Street 5, 28013 Madrid, Spain")


@pytest.mark.asyncio
class TestFilteringShipments:
    """Test filtering shipments by tracking number and carrier."""

    async def test_filter_1(self, test_db, mock_redis, created_shipments):
        """Test filtering shipments by tracking number."""
        # Act
        result = await find_shipments(carrier="DHL", db=test_db)

        # Assert
        assert len(result.shipments) == 1
        found_shipment = result.shipments[0]
        assert found_shipment.tracking_number == "TN12345678"
        assert found_shipment.carrier == "DHL"
