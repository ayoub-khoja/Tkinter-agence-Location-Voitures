import os
import sqlite3
from datetime import datetime, timedelta

DB_FILE = "car_rental.db"


def get_db_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, DB_FILE)


def get_connection():
    path = get_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_schema():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            plate TEXT NOT NULL UNIQUE,
            price_per_day REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'available',
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            cin TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            email TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS rentals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            car_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            days INTEGER NOT NULL,
            daily_price REAL NOT NULL,
            total REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            returned_at TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (car_id) REFERENCES cars(id)
        )
        """
    )

    # indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cars_status ON cars(status)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_rentals_status ON rentals(status)")
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_rentals_start_date ON rentals(start_date)"
    )

    conn.commit()
    conn.close()


def seed_data():
    """Insert demo data on first launch (if tables are empty)."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM cars")
    cars_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM customers")
    customers_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM rentals")
    rentals_count = cur.fetchone()[0]

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if cars_count == 0:
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
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            cars,
        )

    if customers_count == 0:
        customers = [
            ("Ali", "Ben Salah", "CIN001", "0600000001", "ali@example.com", now),
            ("Sara", "El Amrani", "CIN002", "0600000002", "sara@example.com", now),
            ("Youssef", "Haddad", "CIN003", "0600000003", "youssef@example.com", now),
        ]
        cur.executemany(
            """
            INSERT INTO customers (first_name, last_name, cin, phone, email, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            customers,
        )

    if rentals_count == 0:
        # Need some ids
        cur.execute("SELECT id, price_per_day FROM cars WHERE plate = 'AA-123-AA'")
        car1 = cur.fetchone()
        cur.execute("SELECT id, price_per_day FROM cars WHERE plate = 'BB-456-BB'")
        car2 = cur.fetchone()
        cur.execute("SELECT id FROM customers WHERE cin = 'CIN001'")
        cust1 = cur.fetchone()
        cur.execute("SELECT id FROM customers WHERE cin = 'CIN002'")
        cust2 = cur.fetchone()

        if car1 and car2 and cust1 and cust2:
            # Active rental
            start1 = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            end1 = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
            days1 = 3
            total1 = days1 * float(car1["price_per_day"])

            # Returned rental
            start2 = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
            end2 = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
            days2 = 2
            total2 = days2 * float(car2["price_per_day"])
            returned_at2 = (datetime.now() - timedelta(days=2)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

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
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rentals,
            )

            # ensure car1 is rented
            cur.execute(
                "UPDATE cars SET status = 'rented' WHERE id = ?", (car1["id"],)
            )

    conn.commit()
    conn.close()


def setup_database():
    init_schema()
    seed_data()

