from typing import List, Optional, Dict, Any
from datetime import datetime

from db import get_db_cursor


def list_rentals(
    customer_id: Optional[int] = None,
    car_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[dict]:
    with get_db_cursor(dictionary=True) as cur:
        query = """
            SELECT r.*, c.first_name, c.last_name, car.brand, car.model, car.plate
            FROM rentals r
            JOIN customers c ON c.id = r.customer_id
            JOIN cars car ON car.id = r.car_id
            WHERE 1=1
        """
        params: list[Any] = []

        if customer_id:
            query += " AND r.customer_id = %s"
            params.append(customer_id)
        if car_id:
            query += " AND r.car_id = %s"
            params.append(car_id)
        if start_date:
            query += " AND r.start_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND r.end_date <= %s"
            params.append(end_date)

        query += " ORDER BY r.created_at DESC"

        cur.execute(query, params)
        return cur.fetchall()


def get_rental(rental_id: int) -> Optional[dict]:
    with get_db_cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM rentals WHERE id = %s", (rental_id,))
        return cur.fetchone()


def create_rental(data: Dict[str, Any]) -> int:
    with get_db_cursor(dictionary=True) as cur:
        cur.execute(
            """
            INSERT INTO rentals (
                customer_id, car_id, start_date, end_date, days,
                daily_price, total, status, created_at, returned_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NULL)
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
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        return cur.lastrowid


def update_rental(rental_id: int, data: Dict[str, Any]) -> None:
    with get_db_cursor(dictionary=True) as cur:
        cur.execute(
            """
            UPDATE rentals
            SET customer_id = %s, car_id = %s, start_date = %s, end_date = %s,
                days = %s, daily_price = %s, total = %s, status = %s, returned_at = %s
            WHERE id = %s
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


def set_rental_status(
    rental_id: int, status: str, returned_at: Optional[str] = None
) -> None:
    with get_db_cursor(dictionary=True) as cur:
        cur.execute(
            """
            UPDATE rentals
            SET status = %s, returned_at = %s
            WHERE id = %s
            """,
            (status, returned_at, rental_id),
        )


def total_revenue() -> float:
    with get_db_cursor(dictionary=True) as cur:
        cur.execute(
            "SELECT COALESCE(SUM(total), 0) as total FROM rentals WHERE status != 'canceled'"
        )
        result = cur.fetchone()
        return float(result['total']) if result and result['total'] else 0.0


def latest_rentals(limit: int = 5) -> List[dict]:
    with get_db_cursor(dictionary=True) as cur:
        cur.execute(
            """
            SELECT r.*, c.first_name, c.last_name, car.brand, car.model, car.plate
            FROM rentals r
            JOIN customers c ON c.id = r.customer_id
            JOIN cars car ON car.id = r.car_id
            ORDER BY r.created_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        return cur.fetchall()
