import mysql.connector
from mysql.connector import Error
from mysql.connector.cursor import MySQLCursorDict
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import Iterator
from config import DB_CONFIG


def get_connection():
    """Get MySQL database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise


@contextmanager
def get_db_connection() -> Iterator[mysql.connector.MySQLConnection]:
    """Context manager for database connections - ensures proper cleanup"""
    conn = None
    try:
        conn = get_connection()
        yield conn
    except Error as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()


@contextmanager
def get_db_cursor(dictionary: bool = True) -> Iterator[mysql.connector.cursor.MySQLCursor]:
    """Context manager for database cursors - ensures proper cleanup"""
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=dictionary)
        try:
            yield cur
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cur.close()


def init_schema():
    """Initialize database schema for MySQL"""
    # First, connect without specifying database to create it if needed
    config_without_db = {k: v for k, v in DB_CONFIG.items() if k != 'database'}
    conn = None
    try:
        conn = mysql.connector.connect(**config_without_db)
        cur = conn.cursor()
        # Create database if not exists
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} "
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        conn.commit()
        cur.close()
    except Error as e:
        print(f"Error creating database: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()
    
    # Now connect with the database name and create tables
    with get_db_cursor(dictionary=False) as cur:
      

        print("Database schema initialized successfully!")


def seed_data():
    """Insert demo data on first launch (if tables are empty)."""
    with get_db_cursor(dictionary=True) as cur:
        # Optimize: Use EXISTS instead of COUNT for better performance
        cur.execute("SELECT EXISTS(SELECT 1 FROM cars LIMIT 1) as has_cars")
        has_cars = cur.fetchone()['has_cars']
        cur.execute("SELECT EXISTS(SELECT 1 FROM customers LIMIT 1) as has_customers")
        has_customers = cur.fetchone()['has_customers']
        cur.execute("SELECT EXISTS(SELECT 1 FROM rentals LIMIT 1) as has_rentals")
        has_rentals = cur.fetchone()['has_rentals']

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        now_dt = datetime.now()

        if not has_cars:
            cars = [
                ("Toyota", "Corolla", 2020, "AA-123-AA", 45.0, "available", now),
                ("Peugeot", "208", 2019, "BB-456-BB", 40.0, "available", now),
                ("Dacia", "Duster", 2021, "CC-789-CC", 55.0, "maintenance", now),
                ("Renault", "Clio", 2018, "DD-321-DD", 38.0, "available", now),
                ("Volkswagen", "Golf", 2022, "EE-654-EE", 60.0, "available", now),
            ]
            cur.executemany(
                """
                INSERT INTO cars (brand, model, year, plate, price_per_day, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                cars,
            )

        if not has_customers:
            customers = [
                ("Ali", "Ben Salah", "CIN001", "0600000001", "ali@example.com", now),
                ("Sara", "El Amrani", "CIN002", "0600000002", "sara@example.com", now),
                ("Youssef", "Haddad", "CIN003", "0600000003", "youssef@example.com", now),
            ]
            cur.executemany(
                """
                INSERT INTO customers (first_name, last_name, cin, phone, email, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                customers,
            )

        if not has_rentals:
            # Optimize: Fetch all needed data in a single query
            cur.execute("""
                SELECT id, price_per_day, plate FROM cars 
                WHERE plate IN ('AA-123-AA', 'BB-456-BB')
            """)
            cars_data = {row['plate']: row for row in cur.fetchall()}
            
            cur.execute("""
                SELECT id, cin FROM customers 
                WHERE cin IN ('CIN001', 'CIN002')
            """)
            customers_data = {row['cin']: row for row in cur.fetchall()}

            car1 = cars_data.get('AA-123-AA')
            car2 = cars_data.get('BB-456-BB')
            cust1 = customers_data.get('CIN001')
            cust2 = customers_data.get('CIN002')

            if car1 and car2 and cust1 and cust2:
                # Active rental
                start1 = (now_dt - timedelta(days=1)).strftime("%Y-%m-%d")
                end1 = (now_dt + timedelta(days=2)).strftime("%Y-%m-%d")
                days1 = 3
                total1 = days1 * float(car1["price_per_day"])

                # Returned rental
                start2 = (now_dt - timedelta(days=5)).strftime("%Y-%m-%d")
                end2 = (now_dt - timedelta(days=3)).strftime("%Y-%m-%d")
                days2 = 2
                total2 = days2 * float(car2["price_per_day"])
                returned_at2 = (now_dt - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")

                rentals = [
                    (
                        cust1["id"],
                        car1["id"],
                        start1,
                        end1,
                        days1,
                        car1["price_per_day"],
                        total1,
                        "active",
                        now,
                        None,
                    ),
                    (
                        cust2["id"],
                        car2["id"],
                        start2,
                        end2,
                        days2,
                        car2["price_per_day"],
                        total2,
                        "returned",
                        now,
                        returned_at2,
                    ),
                ]

                cur.executemany(
                    """
                    INSERT INTO rentals (
                        customer_id, car_id, start_date, end_date, days, daily_price, total,
                        status, created_at, returned_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    rentals,
                )

                # ensure car1 is rented
                cur.execute(
                    "UPDATE cars SET status = 'rented' WHERE id = %s", (car1["id"],)
                )

        print("Demo data seeded successfully!")


def setup_database():
    init_schema()
    seed_data()
