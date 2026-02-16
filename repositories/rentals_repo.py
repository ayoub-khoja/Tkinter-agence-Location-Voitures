# Importation des types pour les annotations
from typing import List, Optional, Dict, Any
# Importation de datetime pour les dates
from datetime import datetime
# Importation de la fonction pour obtenir un curseur de base de données
from db import get_db_cursor


def list_rentals(
    customer_id: Optional[int] = None,
    car_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[dict]:
    """Liste des locations avec filtres optionnels"""
    # Obtenir un curseur de base de données
    with get_db_cursor(dictionary=True) as cur:
        # Requête SQL de base avec JOIN pour récupérer infos client et voiture
        query = """
            SELECT r.*, c.first_name, c.last_name, car.brand, car.model, car.plate
            FROM rentals r
            JOIN customers c ON c.id = r.customer_id
            JOIN cars car ON car.id = r.car_id
            WHERE 1=1
        """
        # Liste pour stocker les paramètres de la requête
        params = []
        # Si un ID client est fourni, ajouter le filtre
        if customer_id:
            query += " AND r.customer_id = %s"
            params.append(customer_id)
        # Si un ID voiture est fourni, ajouter le filtre
        if car_id:
            query += " AND r.car_id = %s"
            params.append(car_id)
        # Si une date de début est fournie, ajouter le filtre
        if start_date:
            query += " AND r.start_date >= %s"
            params.append(start_date)
        # Si une date de fin est fournie, ajouter le filtre
        if end_date:
            query += " AND r.end_date <= %s"
            params.append(end_date)
        # Ajouter le tri par date de création (plus récent en premier)
        query += " ORDER BY r.created_at DESC"
        # Exécuter la requête avec les paramètres
        cur.execute(query, params)
        # Retourner tous les résultats
        return cur.fetchall()


def get_rental(rental_id: int) -> Optional[dict]:
    """Récupérer une location par ID"""
    # Obtenir un curseur de base de données
    with get_db_cursor(dictionary=True) as cur:
        # Exécuter une requête SQL pour récupérer une location par son ID
        cur.execute("SELECT * FROM rentals WHERE id = %s", (rental_id,))
        # Retourner le premier résultat (ou None si pas trouvé)
        return cur.fetchone()


def create_rental(data: Dict[str, Any]) -> int:
    """Créer une nouvelle location"""
    # Obtenir un curseur de base de données
    with get_db_cursor(dictionary=True) as cur:
        # Exécuter une requête SQL INSERT pour créer une nouvelle location
        cur.execute(
            """
            INSERT INTO rentals (
                customer_id, car_id, start_date, end_date, days,
                daily_price, total, status, created_at, returned_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NULL)
            """,
            (
                data["customer_id"],  # ID du client
                data["car_id"],  # ID de la voiture
                data["start_date"],  # Date de début de location
                data["end_date"],  # Date de fin de location
                data["days"],  # Nombre de jours
                data["daily_price"],  # Prix par jour
                data["total"],  # Total à payer
                data["status"],  # Statut (active, returned, canceled)
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Date de création
            ),
        )
        # Retourner l'ID de la location créée
        return cur.lastrowid


def set_rental_status(rental_id: int, status: str, returned_at: Optional[str] = None) -> None:
    """Modifier le statut d'une location"""
    # Obtenir un curseur de base de données
    with get_db_cursor(dictionary=True) as cur:
        # Exécuter une requête SQL UPDATE pour modifier le statut
        cur.execute(
            "UPDATE rentals SET status = %s, returned_at = %s WHERE id = %s",
            (status, returned_at, rental_id),  # Nouveau statut, date de retour, ID de la location
        )


def total_revenue() -> float:
    """Calculer le total des revenus (locations non annulées)"""
    # Obtenir un curseur de base de données
    with get_db_cursor(dictionary=True) as cur:
        # Exécuter une requête SQL pour calculer la somme des totaux (exclure les annulées)
        cur.execute("SELECT COALESCE(SUM(total), 0) as total FROM rentals WHERE status != 'canceled'")
        # Récupérer le résultat
        result = cur.fetchone()
        # Retourner le total (0.0 si aucun résultat)
        return float(result['total']) if result else 0.0


def latest_rentals(limit: int = 5) -> List[dict]:
    """Récupérer les dernières locations"""
    # Obtenir un curseur de base de données
    with get_db_cursor(dictionary=True) as cur:
        # Exécuter une requête SQL avec JOIN pour récupérer les dernières locations
        cur.execute(
            """
            SELECT r.*, c.first_name, c.last_name, car.brand, car.model, car.plate
            FROM rentals r
            JOIN customers c ON c.id = r.customer_id
            JOIN cars car ON car.id = r.car_id
            ORDER BY r.created_at DESC
            LIMIT %s
            """,
            (limit,),  # Limite du nombre de résultats
        )
        # Retourner tous les résultats
        return cur.fetchall()
