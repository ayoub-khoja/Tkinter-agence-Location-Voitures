# Importation des types pour les annotations
from typing import List, Optional, Dict, Any
# Importation du repository pour les voitures
from repositories import cars_repo


def list_cars(search: Optional[str] = None) -> List[dict]:
    """Liste des voitures avec recherche optionnelle"""
    # Appeler la fonction du repository pour lister les voitures
    return cars_repo.list_cars(search)


def list_available_cars() -> List[dict]:
    """Liste des voitures disponibles"""
    # Appeler la fonction du repository pour lister les voitures disponibles
    return cars_repo.list_available_cars()


def save_car(car_id: Optional[int], data: Dict[str, Any]) -> int:
    """Sauvegarder voiture (création ou modification)"""
    # Si un ID est fourni, c'est une modification
    if car_id:
        # Mettre à jour la voiture existante
        cars_repo.update_car(car_id, data)
        # Retourner l'ID de la voiture modifiée
        return car_id
    # Sinon, c'est une création
    # Créer une nouvelle voiture et retourner son ID
    return cars_repo.create_car(data)


def delete_car(car_id: int) -> None:
    """Supprimer voiture (vérifie qu'elle n'est pas en location)"""
    # Vérifier si la voiture a une location active
    if cars_repo.has_active_rental(car_id):
        # Si oui, lever une exception
        raise ValueError("Impossible de supprimer cette voiture : elle est liée à une location active.")
    # Sinon, supprimer la voiture
    cars_repo.delete_car(car_id)


def set_car_status(car_id: int, status: str) -> None:
    """Modifier le statut d'une voiture"""
    # Récupérer la voiture par son ID
    car = cars_repo.get_car(car_id)
    # Vérifier que la voiture existe
    if not car:
        # Si non, lever une exception
        raise ValueError("Voiture introuvable.")
    # Modifier le statut dans l'objet voiture
    car["status"] = status
    # Mettre à jour la voiture dans la base de données
    cars_repo.update_car(car_id, car)

