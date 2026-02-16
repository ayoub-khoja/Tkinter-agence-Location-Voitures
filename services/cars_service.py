# Service pour la gestion des voitures - logique métier
from typing import List, Optional, Dict, Any

from repositories import cars_repo


def list_cars(search: Optional[str] = None) -> List[dict]:
    """
    Jib liste mte3 les voitures avec possibilité de recherche
    search: terme de recherche optionnel
    """
    return cars_repo.list_cars(search)


def list_available_cars() -> List[dict]:
    """
    Jib liste mte3 les voitures disponibles seulement
    Utilisé pour le formulaire de location
    """
    return cars_repo.list_available_cars()


def save_car(car_id: Optional[int], data: Dict[str, Any]) -> int:
    """
    Sauvegarder voiture (création ou modification)
    Si car_id existe: modification, sinon: création
    Retourne: ID mte3 la voiture
    """
    if car_id:
        # Modification de voiture existante
        cars_repo.update_car(car_id, data)
        return car_id
    # Création de nouvelle voiture
    return cars_repo.create_car(data)


def delete_car(car_id: int) -> None:
    """
    S7ab voiture avec vérification
    Ma t3ammelch suppression si la voiture 3andha location active
    """
    if cars_repo.has_active_rental(car_id):
        raise ValueError(
            "Impossible de supprimer cette voiture : elle est liée à une location active."
        )
    cars_repo.delete_car(car_id)


def set_car_status(car_id: int, status: str) -> None:
    """
    Badal statut mte3 voiture (available, rented, maintenance)
    car_id: ID mte3 la voiture
    status: nouveau statut
    """
    car = cars_repo.get_car(car_id)
    if not car:
        raise ValueError("Voiture introuvable.")
    car["status"] = status
    cars_repo.update_car(car_id, car)

