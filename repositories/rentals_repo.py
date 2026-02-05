from typing import List, Optional, Dict, Any

from db import get_connection


def list_rentals(
    customer_id: Optional[int] = None,
    car_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[dict]:
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT r.*, c.first_name, c.last_name, car.brand, car.model, car.plate
        FROM rentals r
        JOIN customers c ON c.id = r.customer_id
        JOIN cars car ON car.id = r.car_id
        WHERE 1=1
    """
    params: list[Any] = []

    if customer_id:
        query += " AND r.customer_id = ?"
        params.append(customer_id)
    if car_id:
        query += " AND r.car_id = ?"
        params.append(car_id)
    if start_date:
        query += " AND r.start_date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND r.end_date <= ?"
        params.append(end_date)

    query += " ORDER BY r.created_at DESC"

    cur.execute(query, params)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def get_rental(rental_id: int) -> Optional[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM rentals WHERE id = ?", (rental_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def create_rental(data: Dict[str, Any]) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO rentals (
            customer_id, car_id, start_date, end_date, days,
            daily_price, total, status, created_at, returned_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), NULL)
        """,
        (
            data["customer_id"],
            data["car_id"],
            data["start_date"],
            data["end_date"],
            data["days"],
            data["daily_price"],
            data["total"],
            data["status"],
        ),
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def update_rental(rental_id: int, data: Dict[str, Any]) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE rentals
        SET customer_id = ?, car_id = ?, start_date = ?, end_date = ?,
            days = ?, daily_price = ?, total = ?, status = ?, returned_at = ?
        WHERE id = ?
        """,
        (
            data["customer_id"],
            data["car_id"],
            data["start_date"],
            data["end_date"],
            data["days"],
            data["daily_price"],
            data["total"],
            data["status"],
            data.get("returned_at"),
            rental_id,
        ),
    )
    conn.commit()
    conn.close()


def set_rental_status(
    rental_id: int, status: str, returned_at: Optional[str] = None
) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE rentals
        SET status = ?, returned_at = ?
        WHERE id = ?
        """,
        (status, returned_at, rental_id),
    )
    conn.commit()
    conn.close()


def total_revenue() -> float:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(total), 0) FROM rentals WHERE status != 'canceled'")
    value = cur.fetchone()[0] or 0.0
    conn.close()
    return float(value)


def latest_rentals(limit: int = 5) -> List[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT r.*, c.first_name, c.last_name, car.brand, car.model, car.plate
        FROM rentals r
        JOIN customers c ON c.id = r.customer_id
        JOIN cars car ON car.id = r.car_id
        ORDER BY r.created_at DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

