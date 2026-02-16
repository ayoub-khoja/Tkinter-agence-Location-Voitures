# Importation de datetime pour les calculs de dates
from datetime import datetime
# Importation des types pour les annotations
from typing import List, Optional, Dict, Any
# Importation des repositories nécessaires
from repositories import rentals_repo, cars_repo, customers_repo
# Importation du service des voitures
from services import cars_service


def calculate_days(start: str, end: str) -> int:
    """Calculer nombre de jours entre deux dates"""
    # Convertir la date de début en objet datetime
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    # Convertir la date de fin en objet datetime
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    # Vérifier que la date de fin n'est pas avant la date de début
    if end_dt < start_dt:
        # Lever une exception si la date de fin est invalide
        raise ValueError("La date de fin doit être supérieure ou égale à la date de début.")
    # Calculer le nombre de jours (inclus) entre les deux dates
    days = (end_dt - start_dt).days + 1
    # Vérifier que le nombre de jours est valide
    if days <= 0:
        # Lever une exception si le nombre de jours est invalide
        raise ValueError("Le nombre de jours doit être supérieur à 0.")
    # Retourner le nombre de jours
    return days


def list_rentals(
    customer_id: Optional[int] = None,
    car_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[dict]:
    """Liste des locations avec filtres optionnels"""
    # Appeler la fonction du repository pour lister les locations
    return rentals_repo.list_rentals(customer_id, car_id, start_date, end_date)


def create_rental(data: Dict[str, Any]) -> int:
    """Créer une nouvelle location"""
    # Récupérer le client par son ID
    customer = customers_repo.get_customer(data["customer_id"])
    # Vérifier que le client existe
    if not customer:
        # Lever une exception si le client n'existe pas
        raise ValueError("Client introuvable.")

    # Récupérer la voiture par son ID
    car = cars_repo.get_car(data["car_id"])
    # Vérifier que la voiture existe
    if not car:
        # Lever une exception si la voiture n'existe pas
        raise ValueError("Voiture introuvable.")

    # Vérifier que la voiture n'est pas déjà en location
    if car["status"] == "rented":
        # Lever une exception si la voiture est déjà louée
        raise ValueError("Cette voiture est déjà en location.")

    # Calculer le nombre de jours de location
    days = calculate_days(data["start_date"], data["end_date"])
    # Récupérer le prix par jour de la voiture
    daily_price = float(car["price_per_day"])
    # Vérifier que le prix est valide
    if daily_price <= 0:
        # Lever une exception si le prix est invalide
        raise ValueError("Le prix par jour doit être supérieur à 0.")

    # Calculer le total à payer (jours × prix par jour)
    total = days * daily_price

    # Préparer les données pour créer la location
    payload = {
        "customer_id": data["customer_id"],  # ID du client
        "car_id": data["car_id"],  # ID de la voiture
        "start_date": data["start_date"],  # Date de début
        "end_date": data["end_date"],  # Date de fin
        "days": days,  # Nombre de jours calculé
        "daily_price": daily_price,  # Prix par jour
        "total": total,  # Total calculé
        "status": "active",  # Statut initial: active
    }
    # Créer la location dans la base de données
    rental_id = rentals_repo.create_rental(payload)
    # Marquer la voiture comme "rented" (en location)
    cars_service.set_car_status(data["car_id"], "rented")
    # Retourner l'ID de la location créée
    return rental_id


def return_rental(rental_id: int) -> None:
    """Marquer location comme retournée"""
    # Récupérer la location par son ID
    rental = rentals_repo.get_rental(rental_id)
    # Vérifier que la location existe
    if not rental:
        # Lever une exception si la location n'existe pas
        raise ValueError("Location introuvable.")
    # Vérifier que la location est active
    if rental["status"] != "active":
        # Lever une exception si la location n'est pas active
        raise ValueError("Seules les locations actives peuvent être retournées.")
    # Obtenir la date et l'heure actuelles
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Modifier le statut de la location à "returned"
    rentals_repo.set_rental_status(rental_id, "returned", now)
    # Libérer la voiture (statut "available")
    cars_service.set_car_status(rental["car_id"], "available")


def cancel_rental(rental_id: int) -> None:
    """Annuler location active"""
    # Récupérer la location par son ID
    rental = rentals_repo.get_rental(rental_id)
    # Vérifier que la location existe
    if not rental:
        # Lever une exception si la location n'existe pas
        raise ValueError("Location introuvable.")
    # Vérifier que la location est active
    if rental["status"] != "active":
        # Lever une exception si la location n'est pas active
        raise ValueError("Seules les locations actives peuvent être annulées.")
    # Modifier le statut de la location à "canceled"
    rentals_repo.set_rental_status(rental_id, "canceled", rental.get("returned_at"))
    # Libérer la voiture (statut "available")
    cars_service.set_car_status(rental["car_id"], "available")


def total_revenue() -> float:
    """Total des revenus"""
    # Appeler la fonction du repository pour calculer le total
    return rentals_repo.total_revenue()


def latest_rentals(limit: int = 5) -> List[dict]:
    """Dernières locations"""
    # Appeler la fonction du repository pour récupérer les dernières locations
    return rentals_repo.latest_rentals(limit)

