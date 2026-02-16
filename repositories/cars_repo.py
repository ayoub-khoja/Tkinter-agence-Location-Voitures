# Importation des types et modules nécessaires
from typing import List, Optional, Dict, Any
from datetime import datetime

from db import get_db_cursor


def list_cars(search: Optional[str] = None) -> List[dict]:
    """
    Jib liste mte3 toutes les voitures
    search: optionnel - recherche par marque, modèle ou immatriculation
    Retourne: liste de dictionnaires contenant les informations des voitures
    """
    with get_db_cursor(dictionary=True) as cur:
        if search:
            # Si recherche spécifiée, chercher dans marque, modèle ou immatriculation
            pattern = f"%{search}%"
            cur.execute(
                """
                SELECT * FROM cars
                WHERE brand LIKE %s OR model LIKE %s OR plate LIKE %s
                ORDER BY created_at DESC
                """,
                (pattern, pattern, pattern),
            )
        else:
            # Sinon, jib toutes les voitures triées par date de création
            cur.execute("SELECT * FROM cars ORDER BY created_at DESC")
        return cur.fetchall()


def list_available_cars() -> List[dict]:
    """
    Jib liste mte3 les voitures disponibles seulement (status = 'available')
    Utilisé pour afficher les voitures disponibles pour location
    """
    with get_db_cursor(dictionary=True) as cur:
        cur.execute(
            "SELECT * FROM cars WHERE status = 'available' ORDER BY brand, model, year"
        )
        return cur.fetchall()


def get_car(car_id: int) -> Optional[dict]:
    """
    Jib information mte3 voiture spécifique par ID
    car_id: ID mte3 la voiture
    Retourne: dictionnaire avec les infos de la voiture ou None si pas trouvée
    """
    with get_db_cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM cars WHERE id = %s", (car_id,))
        return cur.fetchone()


def create_car(data: Dict[str, Any]) -> int:
    """
    Zid voiture jdida fi la base de données
    data: dictionnaire contenant les informations de la voiture
    Retourne: ID mte3 la voiture créée
    """
    with get_db_cursor(dictionary=True) as cur:
        cur.execute(
            """
            INSERT INTO cars (brand, model, year, plate, price_per_day, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data["brand"],  # Marque
                data["model"],  # Modèle
                int(data["year"]),  # Année
                data["plate"],  # Immatriculation
                float(data["price_per_day"]),  # Prix par jour
                data.get("status", "available"),  # Statut (par défaut: disponible)
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Date de création
            ),
        )
        return cur.lastrowid  # Retourner l'ID de la voiture créée


def update_car(car_id: int, data: Dict[str, Any]) -> None:
    """
    Badal information mte3 voiture existante
    car_id: ID mte3 la voiture à modifier
    data: dictionnaire avec les nouvelles informations
    """
    with get_db_cursor(dictionary=True) as cur:
        cur.execute(
            """
            UPDATE cars
            SET brand = %s, model = %s, year = %s, plate = %s, price_per_day = %s, status = %s
            WHERE id = %s
            """,
            (
                data["brand"],
                data["model"],
                int(data["year"]),
                data["plate"],
                float(data["price_per_day"]),
                data.get("status", "available"),
                car_id,
            ),
        )


def delete_car(car_id: int) -> None:
    """
    S7ab voiture men la base de données
    car_id: ID mte3 la voiture à supprimer
    """
    with get_db_cursor(dictionary=True) as cur:
        cur.execute("DELETE FROM cars WHERE id = %s", (car_id,))


def has_active_rental(car_id: int) -> bool:
    """
    Chkoun si la voiture 3andha location active
    Utilise EXISTS pour meilleure performance (plus rapide que COUNT)
    car_id: ID mte3 la voiture
    Retourne: True si location active, False sinon
    """
    with get_db_cursor(dictionary=True) as cur:
        cur.execute(
            """
            SELECT EXISTS(
                SELECT 1 FROM rentals
                WHERE car_id = %s AND status = 'active'
            ) as has_active
            """,
            (car_id,),
        )
        result = cur.fetchone()
        return bool(result['has_active']) if result else False
