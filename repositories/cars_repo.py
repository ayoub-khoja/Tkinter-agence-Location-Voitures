from typing import List, Optional, Dict, Any

from db import get_connection


def list_cars(search: Optional[str] = None) -> List[dict]:
    conn = get_connection()
    cur = conn.cursor()
    if search:
        pattern = f"%{search}%"
        cur.execute(
            """
            SELECT * FROM cars
            WHERE brand LIKE ? OR model LIKE ? OR plate LIKE ?
            ORDER BY created_at DESC
            """,
            (pattern, pattern, pattern),
        )
    else:
        cur.execute("SELECT * FROM cars ORDER BY created_at DESC")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def list_available_cars() -> List[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM cars WHERE status = 'available' ORDER BY brand, model, year"
    )
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def get_car(car_id: int) -> Optional[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cars WHERE id = ?", (car_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def create_car(data: Dict[str, Any]) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO cars (brand, model, year, plate, price_per_day, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """,
        (
            data["brand"],
            data["model"],
            int(data["year"]),
            data["plate"],
            float(data["price_per_day"]),
            data.get("status", "available"),
        ),
    )
    conn.commit()
    car_id = cur.lastrowid
    conn.close()
    return car_id


def update_car(car_id: int, data: Dict[str, Any]) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE cars
        SET brand = ?, model = ?, year = ?, plate = ?, price_per_day = ?, status = ?
        WHERE id = ?
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
    conn.commit()
    conn.close()


def delete_car(car_id: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM cars WHERE id = ?", (car_id,))
    conn.commit()
    conn.close()


def has_active_rental(car_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT COUNT(*) FROM rentals
        WHERE car_id = ? AND status = 'active'
        """,
        (car_id,),
    )
    count = cur.fetchone()[0]
    conn.close()
    return count > 0

