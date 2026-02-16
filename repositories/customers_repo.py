# Repository pour la gestion des clients dans la base de données
from typing import List, Optional, Dict, Any
from datetime import datetime

from db import get_db_cursor


def list_customers(search: Optional[str] = None) -> List[dict]:
    """
    Jib liste mte3 tous les clients
    search: optionnel - recherche par nom, prénom, CIN ou téléphone
    Retourne: liste de dictionnaires avec les informations des clients
    """
    with get_db_cursor(dictionary=True) as cur:
        if search:
            # Recherche dans prénom, nom, CIN ou téléphone
            pattern = f"%{search}%"
            cur.execute(
                """
                SELECT * FROM customers
                WHERE first_name LIKE %s OR last_name LIKE %s OR cin LIKE %s OR phone LIKE %s
                ORDER BY created_at DESC
                """,
                (pattern, pattern, pattern, pattern),
            )
        else:
            # Jib tous les clients triés par date de création
            cur.execute("SELECT * FROM customers ORDER BY created_at DESC")
        return cur.fetchall()


def get_customer(customer_id: int) -> Optional[dict]:
    """
    Jib information mte3 client spécifique par ID
    customer_id: ID mte3 le client
    Retourne: dictionnaire avec les infos du client ou None si pas trouvé
    """
    with get_db_cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM customers WHERE id = %s", (customer_id,))
        return cur.fetchone()


def create_customer(data: Dict[str, Any]) -> int:
    """
    Zid client jdid fi la base de données
    data: dictionnaire contenant les informations du client
    Retourne: ID mte3 le client créé
    """
    with get_db_cursor(dictionary=True) as cur:
        cur.execute(
            """
            INSERT INTO customers (first_name, last_name, cin, phone, email, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                data["first_name"],  # Prénom
                data["last_name"],  # Nom
                data["cin"],  # CIN (Carte d'Identité Nationale)
                data["phone"],  # Téléphone
                data.get("email"),  # Email (optionnel)
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Date de création
            ),
        )
        return cur.lastrowid  # Retourner l'ID du client créé


def update_customer(customer_id: int, data: Dict[str, Any]) -> None:
    """
    Badal information mte3 client existant
    customer_id: ID mte3 le client à modifier
    data: dictionnaire avec les nouvelles informations
    """
    with get_db_cursor(dictionary=True) as cur:
        cur.execute(
            """
            UPDATE customers
            SET first_name = %s, last_name = %s, cin = %s, phone = %s, email = %s
            WHERE id = %s
            """,
            (
                data["first_name"],
                data["last_name"],
                data["cin"],
                data["phone"],
                data.get("email"),
                customer_id,
            ),
        )


def delete_customer(customer_id: int) -> None:
    """
    S7ab client men la base de données
    customer_id: ID mte3 le client à supprimer
    """
    with get_db_cursor(dictionary=True) as cur:
        cur.execute("DELETE FROM customers WHERE id = %s", (customer_id,))
