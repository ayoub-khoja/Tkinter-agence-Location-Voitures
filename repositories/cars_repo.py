# Importation des types pour les annotations
from typing import List, Optional, Dict, Any
# Importation de datetime pour les dates
from datetime import datetime
# Importation de la fonction pour obtenir un curseur de base de données
from db import get_db_cursor


def list_cars(search: Optional[str] = None) -> List[dict]:
    """Liste des voitures avec recherche optionnelle"""
    # Obtenir un curseur de base de données (dictionary=True pour avoir des dictionnaires)
    with get_db_cursor(dictionary=True) as cur:
        # Si un terme de recherche est fourni
        if search:
            # Créer un pattern de recherche avec des wildcards (%)
            pattern = f"%{search}%"
            # Exécuter une requête SQL pour chercher dans marque, modèle ou immatriculation
            cur.execute(
                "SELECT * FROM cars WHERE brand LIKE %s OR model LIKE %s OR plate LIKE %s ORDER BY created_at DESC",
                (pattern, pattern, pattern),  # Passer le pattern trois fois pour les trois colonnes
            )
        else:
            # Sinon, récupérer toutes les voitures triées par date de création
            cur.execute("SELECT * FROM cars ORDER BY created_at DESC")
        # Retourner tous les résultats de la requête
        return cur.fetchall()


def list_available_cars() -> List[dict]:
    """Liste des voitures disponibles"""
    # Obtenir un curseur de base de données
    with get_db_cursor(dictionary=True) as cur:
        # Exécuter une requête SQL pour récupérer seulement les voitures disponibles
        cur.execute("SELECT * FROM cars WHERE status = 'available' ORDER BY brand, model, year")
        # Retourner tous les résultats
        return cur.fetchall()


def get_car(car_id: int) -> Optional[dict]:
    """Récupérer une voiture par ID"""
    # Obtenir un curseur de base de données
    with get_db_cursor(dictionary=True) as cur:
        # Exécuter une requête SQL pour récupérer une voiture par son ID
        cur.execute("SELECT * FROM cars WHERE id = %s", (car_id,))
        # Retourner le premier résultat (ou None si pas trouvé)
        return cur.fetchone()


def create_car(data: Dict[str, Any]) -> int:
    """Créer une nouvelle voiture"""
    # Obtenir un curseur de base de données
    with get_db_cursor(dictionary=True) as cur:
        # Exécuter une requête SQL INSERT pour créer une nouvelle voiture
        cur.execute(
            "INSERT INTO cars (brand, model, year, plate, price_per_day, status, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (
                data["brand"],  # Marque de la voiture
                data["model"],  # Modèle de la voiture
                int(data["year"]),  # Année (convertie en entier)
                data["plate"],  # Immatriculation
                float(data["price_per_day"]),  # Prix par jour (converti en float)
                data.get("status", "available"),  # Statut (par défaut: disponible)
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Date de création (format SQL)
            ),
        )
        # Retourner l'ID de la voiture créée
        return cur.lastrowid


def update_car(car_id: int, data: Dict[str, Any]) -> None:
    """Modifier une voiture"""
    # Obtenir un curseur de base de données
    with get_db_cursor(dictionary=True) as cur:
        # Exécuter une requête SQL UPDATE pour modifier une voiture existante
        cur.execute(
            "UPDATE cars SET brand = %s, model = %s, year = %s, plate = %s, price_per_day = %s, status = %s WHERE id = %s",
            (
                data["brand"],  # Nouvelle marque
                data["model"],  # Nouveau modèle
                int(data["year"]),  # Nouvelle année
                data["plate"],  # Nouvelle immatriculation
                float(data["price_per_day"]),  # Nouveau prix par jour
                data.get("status", "available"),  # Nouveau statut
                car_id,  # ID de la voiture à modifier
            ),
        )


def delete_car(car_id: int) -> None:
    """Supprimer une voiture"""
    # Obtenir un curseur de base de données
    with get_db_cursor(dictionary=True) as cur:
        # Exécuter une requête SQL DELETE pour supprimer une voiture
        cur.execute("DELETE FROM cars WHERE id = %s", (car_id,))


def has_active_rental(car_id: int) -> bool:
    """Vérifier si voiture a location active"""
    # Obtenir un curseur de base de données
    with get_db_cursor(dictionary=True) as cur:
        # Exécuter une requête SQL avec EXISTS pour vérifier s'il y a une location active
        cur.execute("SELECT EXISTS(SELECT 1 FROM rentals WHERE car_id = %s AND status = 'active') as has_active", (car_id,))
        # Récupérer le résultat
        result = cur.fetchone()
        # Retourner True si location active, False sinon
        return bool(result['has_active']) if result else False
