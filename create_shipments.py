import asyncio

from http import HTTPStatus
from typing import List

import aiohttp

from faker import Faker

from src.api.schemas.shipment import ArticleCreate, ShipmentCreate
from src.db.enums import ShipmentStatus


fake = Faker()

# API endpoint
SHIPMENTS_API_URL = "http://localhost:8000/api/v1/shipments"


def collect_specific_shipments() -> List[ShipmentCreate]:
    """Create specific shipments with predefined data."""
    shipments = []
    
    # Shipment 1: TN12345678
    shipment1 = ShipmentCreate(
        tracking_number="TN12345678",
        carrier="DHL",
        sender_address="Street 10, 75001 Paris, France",
        receiver_address="Lisa-Fittko-Str 13, 10557 Berlin, Germany",
        status=ShipmentStatus.in_transit,
    )
    shipment1.articles = [
        ArticleCreate(name="Laptop", quantity=1, price=800.0, sku="LP123"),
        ArticleCreate(name="Mouse", quantity=1, price=25.0, sku="MO456")
    ]
    shipments.append(shipment1)
    
    # Shipment 2: TN12345679
    shipment2 = ShipmentCreate(
        tracking_number="TN12345679",
        carrier="UPS",
        sender_address="Street 2, 20144 Hamburg, Germany",
        receiver_address="Street 20, 1000 Brussels, Belgium",
        status=ShipmentStatus.inbound_scan
    )
    shipment2.articles = [
        ArticleCreate(name="Monitor", quantity=2, price=200.0, sku="MT789")
    ]
    shipments.append(shipment2)
    
    # Shipment 3: TN12345680
    shipment3 = ShipmentCreate(
        tracking_number="TN12345680",
        carrier="DPD",
        sender_address="Street 3, 80331 Munich, Germany",
        receiver_address="Street 5, 28013 Madrid, Spain",
        status=ShipmentStatus.delivery
    )
    shipment3.articles = [
        ArticleCreate(name="Keyboard", quantity=1, price=50.0, sku="KB012"),
        ArticleCreate(name="Mouse", quantity=1, price=25.0, sku="MO456")
    ]
    shipments.append(shipment3)
    
    # Shipment 4: TN12345681
    shipment4 = ShipmentCreate(
        tracking_number="TN12345681",
        carrier="FedEx",
        sender_address="Street 4, 50667 Cologne, Germany",
        receiver_address="Street 9, 1016 Amsterdam, Netherlands",
        status=ShipmentStatus.transit
    )
    shipment4.articles = [
        ArticleCreate(name="Laptop", quantity=1, price=900.0, sku="LP345"),
        ArticleCreate(name="Headphones", quantity=1, price=100.0, sku="HP678")
    ]
    shipments.append(shipment4)
    
    # Shipment 5: TN12345682
    shipment5 = ShipmentCreate(
        tracking_number="TN12345682",
        carrier="GLS",
        sender_address="Street 5, 70173 Stuttgart, Germany",
        receiver_address="Street 15, 1050 Copenhagen, Denmark",
        status=ShipmentStatus.scanned
    )
    shipment5.articles = [
        ArticleCreate(name="Smartphone", quantity=1, price=500.0, sku="SP901"),
        ArticleCreate(name="Charger", quantity=1, price=20.0, sku="CH234")
    ]
    shipments.append(shipment5)
    
    return shipments

async def create_shipment(session: aiohttp.ClientSession, shipment: ShipmentCreate) -> None:
    """Create a single shipment via API."""
    json_data = {
        "shipment": shipment.model_dump(),
        "articles": [article.model_dump() for article in shipment.articles],
    }
    try:
        async with session.post(SHIPMENTS_API_URL, json=json_data) as response:
            if response.status == HTTPStatus.CREATED:
                print(f"Created shipment: {shipment.tracking_number}")
            else:
                print(f"Failed to create shipment {shipment.tracking_number}: {response.status=}")
                print(await response.json())
    except Exception as err:
        print(f"Error creating shipment {shipment.tracking_number}: {err}")

async def main():
    """Main function to create multiple shipments."""
    # Generate specific shipments
    shipments = collect_specific_shipments()
    
    # Create aiohttp session
    async with aiohttp.ClientSession() as session:
        # Create tasks for all shipments
        tasks = [create_shipment(session, shipment) for shipment in shipments]
        
        # Run all tasks concurrently
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main()) 