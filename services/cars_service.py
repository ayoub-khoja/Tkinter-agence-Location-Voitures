from typing import List, Optional, Dict, Any

from repositories import cars_repo


def list_cars(search: Optional[str] = None) -> List[dict]:
    return cars_repo.list_cars(search)


def list_available_cars() -> List[dict]:
    return cars_repo.list_available_cars()


def save_car(car_id: Optional[int], data: Dict[str, Any]) -> int:
    if car_id:
        cars_repo.update_car(car_id, data)
        return car_id
    return cars_repo.create_car(data)


def delete_car(car_id: int) -> None:
    if cars_repo.has_active_rental(car_id):
        raise ValueError(
            "Impossible de supprimer cette voiture : elle est liée à une location active."
        )
    cars_repo.delete_car(car_id)


def set_car_status(car_id: int, status: str) -> None:
    car = cars_repo.get_car(car_id)
    if not car:
        raise ValueError("Voiture introuvable.")
    car["status"] = status
    cars_repo.update_car(car_id, car)

