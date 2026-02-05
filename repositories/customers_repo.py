from typing import List, Optional, Dict, Any

from db import get_connection


def list_customers(search: Optional[str] = None) -> List[dict]:
    conn = get_connection()
    cur = conn.cursor()
    if search:
        pattern = f"%{search}%"
        cur.execute(
            """
            SELECT * FROM customers
            WHERE first_name LIKE ? OR last_name LIKE ? OR cin LIKE ? OR phone LIKE ?
            ORDER BY created_at DESC
            """,
            (pattern, pattern, pattern, pattern),
        )
    else:
        cur.execute("SELECT * FROM customers ORDER BY created_at DESC")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def get_customer(customer_id: int) -> Optional[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def create_customer(data: Dict[str, Any]) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO customers (first_name, last_name, cin, phone, email, created_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
        """,
        (
            data["first_name"],
            data["last_name"],
            data["cin"],
            data["phone"],
            data.get("email"),
        ),
    )
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return cid


def update_customer(customer_id: int, data: Dict[str, Any]) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE customers
        SET first_name = ?, last_name = ?, cin = ?, phone = ?, email = ?
        WHERE id = ?
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
    conn.commit()
    conn.close()


def delete_customer(customer_id: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
    conn.commit()
    conn.close()

