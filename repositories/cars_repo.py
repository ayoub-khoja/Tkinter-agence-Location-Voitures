from typing import List, Optional, Dict, Any
from datetime import datetime

from db import get_db_cursor


def list_cars(search: Optional[str] = None) -> List[dict]:
    with get_db_cursor(dictionary=True) as cur:
        if search:
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
            cur.execute("SELECT * FROM cars ORDER BY created_at DESC")
        return cur.fetchall()


def list_available_cars() -> List[dict]:
    with get_db_cursor(dictionary=True) as cur:
        cur.execute(
            "SELECT * FROM cars WHERE status = 'available' ORDER BY brand, model, year"
        )
        return cur.fetchall()


def get_car(car_id: int) -> Optional[dict]:
    with get_db_cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM cars WHERE id = %s", (car_id,))
        return cur.fetchone()


def create_car(data: Dict[str, Any]) -> int:
    with get_db_cursor(dictionary=True) as cur:
        cur.execute(
            """
            INSERT INTO cars (brand, model, year, plate, price_per_day, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data["brand"],
                data["model"],
                int(data["year"]),
                data["plate"],
                float(data["price_per_day"]),
                data.get("status", "available"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        return cur.lastrowid


def update_car(car_id: int, data: Dict[str, Any]) -> None:
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
    with get_db_cursor(dictionary=True) as cur:
        cur.execute("DELETE FROM cars WHERE id = %s", (car_id,))


def has_active_rental(car_id: int) -> bool:
    """Optimized: Use EXISTS instead of COUNT for better performance"""
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
