import json
import logging
import os

from typing import Any

import requests

from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import Nominatim
from pydantic import BaseModel
from redis import Redis


logger = logging.getLogger(__name__)


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class WeatherService:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.cache_ttl = 7200  # 2 hours in seconds
        logger.info("WeatherService initialized with cache TTL: %d seconds", self.cache_ttl)

    def _get_zip_code(self, address: str) -> str | None:
        # Simple implementation - in a real application, you would use a proper geocoding service
        # This is just a placeholder that extracts the first number sequence that looks like a zip code
        import re

        match = re.search(r"\b\d{5}\b", address)
        return match.group(0) if match else None

    def _get_country_code(self, address: str) -> str | None:
        # Simple implementation - in a real application, you would use a proper geocoding service
        # This is just a placeholder that extracts the last word as country
        country = address.split(",")[-1].strip()
        return country

    async def _get_coordinates(self, address: str) -> Coordinates | None:
        # Warning: makes additional http-call, maybe address should be a cache key.
        async with Nominatim(
            user_agent="peaky blinders",
            adapter_factory=AioHTTPAdapter,
        ) as geolocator:
            location = await geolocator.geocode(address)
            if not location:
                return None
            return Coordinates(latitude=location.latitude, longitude=location.longitude)

    async def _get_openweathermap(self, coordinates: Coordinates) -> dict[str, Any] | None:
        params = dict(lat=coordinates.latitude, lon=coordinates.longitude, appid=self.api_key)
        try:
            logger.info("Making request to OpenWeatherMap API")
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            weather_data = response.json()
            logger.info(
                "Successfully retrieved weather data for %s", f"{coordinates.latitude} : {coordinates.longitude}"
            )
        except requests.exceptions.RequestException as e:
            logger.error("Failed to get weather data: %s", str(e))
            return None
        return weather_data

    async def get_weather(self, address: str) -> dict[str, Any] | None:
        logger.info("Getting weather for address: %s", address)

        coordinates = await self._get_coordinates(address)
        if not coordinates:
            return None
        cache_key = f"weather_lat_lon:{coordinates.latitude}:{coordinates.longitude}"
        cached_weather = self.redis_client.get(cache_key)
        if cached_weather:
            logger.info("Found cached weather data for %s", cache_key)
            return json.loads(cached_weather)

        logger.info("No cached data found, making API request")
        weather_data = await self._get_openweathermap(coordinates=coordinates)
        if not weather_data:
            return None

        # Cache the weather data
        try:
            self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(weather_data))
            logger.info("Cached weather data for %s with TTL %d", cache_key, self.cache_ttl)
        except Exception as e:
            logger.error("Failed to cache weather data: %s", str(e))

        return weather_data
