# Importation des types pour les annotations
from typing import List, Optional, Dict, Any
# Importation de datetime pour les dates
from datetime import datetime
# Importation de la fonction pour obtenir un curseur de base de données
from db import get_db_cursor


def list_customers(search: Optional[str] = None) -> List[dict]:
    """Liste des clients avec recherche optionnelle"""
    # Obtenir un curseur de base de données
    with get_db_cursor(dictionary=True) as cur:
        # Si un terme de recherche est fourni
        if search:
            # Créer un pattern de recherche avec des wildcards
            pattern = f"%{search}%"
            # Exécuter une requête SQL pour chercher dans prénom, nom, CIN ou téléphone
            cur.execute(
                "SELECT * FROM customers WHERE first_name LIKE %s OR last_name LIKE %s OR cin LIKE %s OR phone LIKE %s ORDER BY created_at DESC",
                (pattern, pattern, pattern, pattern),  # Passer le pattern quatre fois
            )
        else:
            # Sinon, récupérer tous les clients triés par date de création
            cur.execute("SELECT * FROM customers ORDER BY created_at DESC")
        # Retourner tous les résultats
        return cur.fetchall()


def get_customer(customer_id: int) -> Optional[dict]:
    """Récupérer un client par ID"""
    # Obtenir un curseur de base de données
    with get_db_cursor(dictionary=True) as cur:
        # Exécuter une requête SQL pour récupérer un client par son ID
        cur.execute("SELECT * FROM customers WHERE id = %s", (customer_id,))
        # Retourner le premier résultat (ou None si pas trouvé)
        return cur.fetchone()


def create_customer(data: Dict[str, Any]) -> int:
    """Créer un nouveau client"""
    # Obtenir un curseur de base de données
    with get_db_cursor(dictionary=True) as cur:
        # Exécuter une requête SQL INSERT pour créer un nouveau client
        cur.execute(
            "INSERT INTO customers (first_name, last_name, cin, phone, email, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                data["first_name"],  # Prénom du client
                data["last_name"],  # Nom du client
                data["cin"],  # CIN (Carte d'Identité Nationale)
                data["phone"],  # Téléphone
                data.get("email"),  # Email (optionnel)
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Date de création
            ),
        )
        # Retourner l'ID du client créé
        return cur.lastrowid


def update_customer(customer_id: int, data: Dict[str, Any]) -> None:
    """Modifier un client"""
    # Obtenir un curseur de base de données
    with get_db_cursor(dictionary=True) as cur:
        # Exécuter une requête SQL UPDATE pour modifier un client existant
        cur.execute(
            "UPDATE customers SET first_name = %s, last_name = %s, cin = %s, phone = %s, email = %s WHERE id = %s",
            (
                data["first_name"],  # Nouveau prénom
                data["last_name"],  # Nouveau nom
                data["cin"],  # Nouveau CIN
                data["phone"],  # Nouveau téléphone
                data.get("email"),  # Nouvel email
                customer_id,  # ID du client à modifier
            ),
        )


def delete_customer(customer_id: int) -> None:
    """Supprimer un client"""
    # Obtenir un curseur de base de données
    with get_db_cursor(dictionary=True) as cur:
        # Exécuter une requête SQL DELETE pour supprimer un client
        cur.execute("DELETE FROM customers WHERE id = %s", (customer_id,))
