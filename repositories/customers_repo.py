from typing import List, Optional, Dict, Any
from datetime import datetime

from db import get_db_cursor


def list_customers(search: Optional[str] = None) -> List[dict]:
    with get_db_cursor(dictionary=True) as cur:
        if search:
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
            cur.execute("SELECT * FROM customers ORDER BY created_at DESC")
        return cur.fetchall()


def get_customer(customer_id: int) -> Optional[dict]:
    with get_db_cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM customers WHERE id = %s", (customer_id,))
        return cur.fetchone()


def create_customer(data: Dict[str, Any]) -> int:
    with get_db_cursor(dictionary=True) as cur:
        cur.execute(
            """
            INSERT INTO customers (first_name, last_name, cin, phone, email, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                data["first_name"],
                data["last_name"],
                data["cin"],
                data["phone"],
                data.get("email"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        return cur.lastrowid


def update_customer(customer_id: int, data: Dict[str, Any]) -> None:
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
    with get_db_cursor(dictionary=True) as cur:
        cur.execute("DELETE FROM customers WHERE id = %s", (customer_id,))
