from datetime import datetime
from typing import List, Optional, Dict, Any

from repositories import rentals_repo, cars_repo, customers_repo
from services import cars_service


DATE_FMT = "%Y-%m-%d"


def _parse_date(value: str) -> datetime:
    return datetime.strptime(value, DATE_FMT)


def calculate_days(start: str, end: str) -> int:
    start_dt = _parse_date(start)
    end_dt = _parse_date(end)
    if end_dt < start_dt:
        raise ValueError("La date de fin doit être supérieure ou égale à la date de début.")
    days = (end_dt - start_dt).days + 1
    if days <= 0:
        raise ValueError("Le nombre de jours doit être supérieur à 0.")
    return days


def list_rentals(
    customer_id: Optional[int] = None,
    car_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[dict]:
    return rentals_repo.list_rentals(customer_id, car_id, start_date, end_date)


def create_rental(data: Dict[str, Any]) -> int:
    # basic checks
    customer = customers_repo.get_customer(data["customer_id"])
    if not customer:
        raise ValueError("Client introuvable.")

    car = cars_repo.get_car(data["car_id"])
    if not car:
        raise ValueError("Voiture introuvable.")

    if car["status"] == "rented":
        raise ValueError("Cette voiture est déjà en location.")

    days = calculate_days(data["start_date"], data["end_date"])
    daily_price = float(car["price_per_day"])
    if daily_price <= 0:
        raise ValueError("Le prix par jour doit être supérieur à 0.")

    total = days * daily_price

    payload = {
        "customer_id": data["customer_id"],
        "car_id": data["car_id"],
        "start_date": data["start_date"],
        "end_date": data["end_date"],
        "days": days,
        "daily_price": daily_price,
        "total": total,
        "status": "active",
    }
    rental_id = rentals_repo.create_rental(payload)
    # mark car rented
    cars_service.set_car_status(data["car_id"], "rented")
    return rental_id


def return_rental(rental_id: int) -> None:
    rental = rentals_repo.get_rental(rental_id)
    if not rental:
        raise ValueError("Location introuvable.")
    if rental["status"] != "active":
        raise ValueError("Seules les locations actives peuvent être retournées.")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rentals_repo.set_rental_status(rental_id, "returned", now)
    cars_service.set_car_status(rental["car_id"], "available")


def cancel_rental(rental_id: int) -> None:
    rental = rentals_repo.get_rental(rental_id)
    if not rental:
        raise ValueError("Location introuvable.")
    if rental["status"] != "active":
        raise ValueError("Seules les locations actives peuvent être annulées.")
    rentals_repo.set_rental_status(rental_id, "canceled", rental.get("returned_at"))
    cars_service.set_car_status(rental["car_id"], "available")


def total_revenue() -> float:
    return rentals_repo.total_revenue()


def latest_rentals(limit: int = 5) -> List[dict]:
    return rentals_repo.latest_rentals(limit)

