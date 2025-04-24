from enum import StrEnum, unique


@unique
class ShipmentStatus(StrEnum):
    """Enum for allowed shipment status values."""

    created = "created"
    active = "active"
    pending = "pending"
    transit = "transit"
    in_transit = "in_transit"
    inbound_scan = "inbound_scan"
    delivery = "delivery"
    scanned = "scanned"
    failed = "failed"
    canceled = "canceled"
    returned = "returned"
    lost = "lost"
