
import customtkinter as ctk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from typing import Iterator, List, Optional, Dict, Any
from datetime import datetime


DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "car_rental_db",
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci"
}

def get_connection():
    """Connexion à MySQL"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Erreur de connexion à MySQL: {e}")
        raise

@contextmanager
def get_db_connection() -> Iterator[mysql.connector.MySQLConnection]:
    
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
    """manager pour curseurs """
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

def setup_database():
    """Vérifier connexion à la base de données"""
    conn = get_connection()
    if conn.is_connected():
        print(f"Connexion réussie: {DB_CONFIG['database']}")
        conn.close()

# ============================================================================
# REPOSITORIES
# ============================================================================

class CarsRepo:
    @staticmethod
    def list_cars(search: Optional[str] = None) -> List[dict]:
        with get_db_cursor(dictionary=True) as cur:
            if search:
                pattern = f"%{search}%"
                cur.execute(
                    "SELECT * FROM cars WHERE brand LIKE %s OR model LIKE %s OR plate LIKE %s ORDER BY created_at DESC",
                    (pattern, pattern, pattern),
                )
            else:
                cur.execute("SELECT * FROM cars ORDER BY created_at DESC")
            return cur.fetchall()

    @staticmethod
    def list_available_cars() -> List[dict]:
        with get_db_cursor(dictionary=True) as cur:
            cur.execute("SELECT * FROM cars WHERE status = 'available' ORDER BY brand, model, year")
            return cur.fetchall()

    @staticmethod
    def get_car(car_id: int) -> Optional[dict]:
        with get_db_cursor(dictionary=True) as cur:
            cur.execute("SELECT * FROM cars WHERE id = %s", (car_id,))
            return cur.fetchone()

    @staticmethod
    def create_car(data: Dict[str, Any]) -> int:
        with get_db_cursor(dictionary=True) as cur:
            cur.execute(
                "INSERT INTO cars (brand, model, year, plate, price_per_day, status, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
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

    @staticmethod
    def update_car(car_id: int, data: Dict[str, Any]) -> None:
        with get_db_cursor(dictionary=True) as cur:
            cur.execute(
                "UPDATE cars SET brand = %s, model = %s, year = %s, plate = %s, price_per_day = %s, status = %s WHERE id = %s",
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

    @staticmethod
    def delete_car(car_id: int) -> None:
        with get_db_cursor(dictionary=True) as cur:
            cur.execute("DELETE FROM cars WHERE id = %s", (car_id,))

    @staticmethod
    def has_active_rental(car_id: int) -> bool:
        with get_db_cursor(dictionary=True) as cur:
            cur.execute("SELECT EXISTS(SELECT 1 FROM rentals WHERE car_id = %s AND status = 'active') as has_active", (car_id,))
            result = cur.fetchone()
            return bool(result['has_active']) if result else False

class CustomersRepo:
    @staticmethod
    def list_customers(search: Optional[str] = None) -> List[dict]:
        with get_db_cursor(dictionary=True) as cur:
            if search:
                pattern = f"%{search}%"
                cur.execute(
                    "SELECT * FROM customers WHERE first_name LIKE %s OR last_name LIKE %s OR cin LIKE %s OR phone LIKE %s ORDER BY created_at DESC",
                    (pattern, pattern, pattern, pattern),
                )
            else:
                cur.execute("SELECT * FROM customers ORDER BY created_at DESC")
            return cur.fetchall()

    @staticmethod
    def get_customer(customer_id: int) -> Optional[dict]:
        with get_db_cursor(dictionary=True) as cur:
            cur.execute("SELECT * FROM customers WHERE id = %s", (customer_id,))
            return cur.fetchone()

    @staticmethod
    def create_customer(data: Dict[str, Any]) -> int:
        with get_db_cursor(dictionary=True) as cur:
            cur.execute(
                "INSERT INTO customers (first_name, last_name, cin, phone, email, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
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

    @staticmethod
    def update_customer(customer_id: int, data: Dict[str, Any]) -> None:
        with get_db_cursor(dictionary=True) as cur:
            cur.execute(
                "UPDATE customers SET first_name = %s, last_name = %s, cin = %s, phone = %s, email = %s WHERE id = %s",
                (
                    data["first_name"],
                    data["last_name"],
                    data["cin"],
                    data["phone"],
                    data.get("email"),
                    customer_id,
                ),
            )

    @staticmethod
    def delete_customer(customer_id: int) -> None:
        with get_db_cursor(dictionary=True) as cur:
            cur.execute("DELETE FROM customers WHERE id = %s", (customer_id,))

class RentalsRepo:
    @staticmethod
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
            params = []
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

    @staticmethod
    def get_rental(rental_id: int) -> Optional[dict]:
        with get_db_cursor(dictionary=True) as cur:
            cur.execute("SELECT * FROM rentals WHERE id = %s", (rental_id,))
            return cur.fetchone()

    @staticmethod
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

    @staticmethod
    def set_rental_status(rental_id: int, status: str, returned_at: Optional[str] = None) -> None:
        with get_db_cursor(dictionary=True) as cur:
            cur.execute(
                "UPDATE rentals SET status = %s, returned_at = %s WHERE id = %s",
                (status, returned_at, rental_id),
            )

    @staticmethod
    def total_revenue() -> float:
        with get_db_cursor(dictionary=True) as cur:
            cur.execute("SELECT COALESCE(SUM(total), 0) as total FROM rentals WHERE status != 'canceled'")
            result = cur.fetchone()
            return float(result['total']) if result else 0.0

    @staticmethod
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

# ============================================================================
# SERVICES
# ============================================================================

class CarsService:
    @staticmethod
    def list_cars(search: Optional[str] = None) -> List[dict]:
        return CarsRepo.list_cars(search)

    @staticmethod
    def list_available_cars() -> List[dict]:
        return CarsRepo.list_available_cars()

    @staticmethod
    def save_car(car_id: Optional[int], data: Dict[str, Any]) -> int:
        if car_id:
            CarsRepo.update_car(car_id, data)
            return car_id
        return CarsRepo.create_car(data)

    @staticmethod
    def delete_car(car_id: int) -> None:
        if CarsRepo.has_active_rental(car_id):
            raise ValueError("Impossible de supprimer cette voiture : elle est liée à une location active.")
        CarsRepo.delete_car(car_id)

    @staticmethod
    def set_car_status(car_id: int, status: str) -> None:
        car = CarsRepo.get_car(car_id)
        if not car:
            raise ValueError("Voiture introuvable.")
        car["status"] = status
        CarsRepo.update_car(car_id, car)

class RentalsService:
    @staticmethod
    def calculate_days(start: str, end: str) -> int:
        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d")
        if end_dt < start_dt:
            raise ValueError("La date de fin doit être supérieure ou égale à la date de début.")
        days = (end_dt - start_dt).days + 1
        if days <= 0:
            raise ValueError("Le nombre de jours doit être supérieur à 0.")
        return days

    @staticmethod
    def list_rentals(
        customer_id: Optional[int] = None,
        car_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[dict]:
        return RentalsRepo.list_rentals(customer_id, car_id, start_date, end_date)

    @staticmethod
    def create_rental(data: Dict[str, Any]) -> int:
        customer = CustomersRepo.get_customer(data["customer_id"])
        if not customer:
            raise ValueError("Client introuvable.")

        car = CarsRepo.get_car(data["car_id"])
        if not car:
            raise ValueError("Voiture introuvable.")

        if car["status"] == "rented":
            raise ValueError("Cette voiture est déjà en location.")

        days = RentalsService.calculate_days(data["start_date"], data["end_date"])
        daily_price = float(car["price_per_day"])
        if daily_price <= 0:
            raise ValueError("Le prix par jour doit être supérieur à 0.")

        total = days * daily_price

        payload = {
            "customer_id": data["customer_id"],
            "car_id": data["car_id"],
            "start_date": data["start_date"],
            "end_date": data["end_date"],
            "days": days,
            "daily_price": daily_price,
            "total": total,
            "status": "active",
        }
        rental_id = RentalsRepo.create_rental(payload)
        CarsService.set_car_status(data["car_id"], "rented")
        return rental_id

    @staticmethod
    def return_rental(rental_id: int) -> None:
        rental = RentalsRepo.get_rental(rental_id)
        if not rental:
            raise ValueError("Location introuvable.")
        if rental["status"] != "active":
            raise ValueError("Seules les locations actives peuvent être retournées.")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        RentalsRepo.set_rental_status(rental_id, "returned", now)
        CarsService.set_car_status(rental["car_id"], "available")

    @staticmethod
    def cancel_rental(rental_id: int) -> None:
        rental = RentalsRepo.get_rental(rental_id)
        if not rental:
            raise ValueError("Location introuvable.")
        if rental["status"] != "active":
            raise ValueError("Seules les locations actives peuvent être annulées.")
        RentalsRepo.set_rental_status(rental_id, "canceled", rental.get("returned_at"))
        CarsService.set_car_status(rental["car_id"], "available")

    @staticmethod
    def total_revenue() -> float:
        return RentalsRepo.total_revenue()

    @staticmethod
    def latest_rentals(limit: int = 5) -> List[dict]:
        return RentalsRepo.latest_rentals(limit)

# ============================================================================
# UTILITIES
# ============================================================================

def format_money(value: float) -> str:
    """Formater valeur monétaire simplement"""
    return f"{value:.2f} TND"

# ============================================================================
# UI VIEWS
# ============================================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, colors):
        super().__init__(parent, fg_color=colors["bg_primary"])
        self.colors = colors
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        welcome_frame = ctk.CTkFrame(
            header_frame,
            fg_color=self.colors["bg_secondary"],
            corner_radius=20,
            height=90
        )
        welcome_frame.pack(fill="x", pady=(0, 15))
        welcome_frame.pack_propagate(False)
        
        welcome_inner = ctk.CTkFrame(welcome_frame, fg_color="transparent")
        welcome_inner.pack(fill="both", expand=True, padx=25, pady=15)
        
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Bonjour"
        elif hour < 18:
            greeting = "Bon après-midi"
        else:
            greeting = "Bonsoir"
        
        greeting_label = ctk.CTkLabel(
            welcome_inner,
            text=f"{greeting}! 👋",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        greeting_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            welcome_inner,
            text="Bienvenue sur votre tableau de bord - Gérez vos locations efficacement",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_muted"]
        )
        subtitle_label.pack(anchor="w", pady=(3, 0))

        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.grid(row=1, column=0, sticky="nsew")
        kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        kpi_frame.grid_rowconfigure(0, weight=0)
        kpi_frame.grid_rowconfigure(1, weight=1)

        self.lbl_total_cars = self._create_enhanced_kpi_card(
            kpi_frame, 0, 0, "Total Voitures", "🚗", self.colors["accent_primary"], "#1E40AF"
        )
        self.lbl_available = self._create_enhanced_kpi_card(
            kpi_frame, 0, 1, "Disponibles", "✅", self.colors["success"], "#047857"
        )
        self.lbl_rented = self._create_enhanced_kpi_card(
            kpi_frame, 0, 2, "En Location", "🔑", self.colors["warning"], "#B45309"
        )
        self.lbl_revenue = self._create_enhanced_kpi_card(
            kpi_frame, 0, 3, "Revenus Total", "💰", self.colors["accent_gold"], "#D97706"
        )

        bottom_frame = ctk.CTkFrame(kpi_frame, fg_color="transparent")
        bottom_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(25, 0))
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_rowconfigure(1, weight=1)

        table_header = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        table_header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        
        header_left = ctk.CTkFrame(table_header, fg_color="transparent")
        header_left.pack(side="left")
        
        table_title = ctk.CTkLabel(
            header_left,
            text="📋 Dernières Locations",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        table_title.pack(side="left", padx=(0, 10))
        
        table_subtitle = ctk.CTkLabel(
            header_left,
            text="Aperçu des 5 dernières transactions",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_muted"]
        )
        table_subtitle.pack(side="left")

        table_container = ctk.CTkFrame(
            bottom_frame,
            fg_color=self.colors["bg_secondary"],
            corner_radius=20
        )
        table_container.grid(row=1, column=0, sticky="nsew")
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(0, weight=1)

        inner_table = ctk.CTkFrame(table_container, fg_color="transparent")
        inner_table.grid(row=0, column=0, sticky="nsew", padx=25, pady=25)
        inner_table.grid_columnconfigure(0, weight=1)
        inner_table.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure(
            "Modern.Treeview",
            background=self.colors["bg_tertiary"],
            foreground=self.colors["text_primary"],
            fieldbackground=self.colors["bg_tertiary"],
            rowheight=45,
            borderwidth=0,
            font=("Segoe UI", 12),
            padding=10
        )
        style.configure(
            "Modern.Treeview.Heading",
            background=self.colors["bg_secondary"],
            foreground=self.colors["text_secondary"],
            font=("Segoe UI", 13, "bold"),
            borderwidth=0,
            padding=15,
            relief="flat"
        )
        style.map(
            "Modern.Treeview",
            background=[("selected", self.colors["accent_primary"])],
            foreground=[("selected", self.colors["text_primary"])]
        )

        columns = ("id", "client", "car", "period", "total", "status")
        self.tree = ttk.Treeview(
            inner_table,
            columns=columns,
            show="headings",
            height=6,
            style="Modern.Treeview"
        )

        for col, text, width in [
            ("id", "ID", 70),
            ("client", "👤 Client", 200),
            ("car", "🚗 Voiture", 250),
            ("period", "📅 Période", 220),
            ("total", "💵 Total", 150),
            ("status", "📊 Statut", 150),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ctk.CTkScrollbar(
            inner_table,
            orientation="vertical",
            command=self.tree.yview,
            button_color=self.colors["bg_tertiary"],
            button_hover_color=self.colors["accent_primary"]
        )
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(10, 0))
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.refresh()

    def _create_enhanced_kpi_card(self, parent, row, column, title, icon, color, gradient_color):
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors["bg_secondary"],
            corner_radius=20,
            height=180,
            border_width=1,
            border_color=self.colors["bg_tertiary"]
        )
        card.grid(row=row, column=column, sticky="ew", padx=12)
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)

        top_section = ctk.CTkFrame(card, fg_color="transparent")
        top_section.pack(fill="x", padx=25, pady=(25, 15))
        
        icon_container = ctk.CTkFrame(
            top_section,
            fg_color=color,
            corner_radius=12,
            width=50,
            height=50
        )
        icon_container.pack(side="left")
        icon_container.pack_propagate(False)
        
        icon_label = ctk.CTkLabel(
            icon_container,
            text=icon,
            font=ctk.CTkFont(size=24),
            text_color="#FFFFFF"
        )
        icon_label.pack(expand=True)
        
        title_label = ctk.CTkLabel(
            top_section,
            text=title,
            font=ctk.CTkFont(size=13, weight="normal"),
            text_color=self.colors["text_muted"]
        )
        title_label.pack(side="left", padx=(15, 0), pady=15)

        value_section = ctk.CTkFrame(card, fg_color="transparent")
        value_section.pack(fill="x", padx=25, pady=(0, 25))
        
        value_label = ctk.CTkLabel(
            value_section,
            text="0",
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color=color
        )
        value_label.pack(anchor="w")

        line = ctk.CTkFrame(
            card,
            fg_color=color,
            height=3,
            corner_radius=2
        )
        line.pack(fill="x", padx=25, pady=(0, 0))

        return value_label

    def refresh(self):
        cars = CarsRepo.list_cars()
        total_cars = len(cars)
        available = len([c for c in cars if c["status"] == "available"])
        rented = len([c for c in cars if c["status"] == "rented"])
        revenue = RentalsService.total_revenue()

        self.lbl_total_cars.configure(text=str(total_cars))
        self.lbl_available.configure(text=str(available))
        self.lbl_rented.configure(text=str(rented))
        self.lbl_revenue.configure(text=format_money(revenue))

        for item in self.tree.get_children():
            self.tree.delete(item)

        rentals = RentalsService.latest_rentals(5)
        
        if not rentals:
            self.tree.insert("", "end", values=("", "Aucune location", "", "", "", ""))
        else:
            status_map = {
                "active": "🟢 Actif",
                "returned": "✅ Retourné",
                "cancelled": "❌ Annulé"
            }
            for rental in rentals:
                client = f"{rental['first_name']} {rental['last_name']}"
                car = f"{rental['brand']} {rental['model']} ({rental['plate']})"
                period = f"{rental['start_date']} → {rental['end_date']}"
                total = format_money(rental["total"])
                status_display = status_map.get(rental["status"], f"📌 {rental['status'].capitalize()}")
                
                self.tree.insert(
                    "", "end",
                    values=(rental["id"], client, car, period, total, status_display)
                )


class CarsView(ctk.CTkFrame):
    def __init__(self, parent, colors):
        super().__init__(parent, fg_color=colors["bg_primary"])
        self.colors = colors
        self.selected_id = None
        self._build()
        self.refresh()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🚗 Gestion des Voitures",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.colors["accent_primary"]
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Créez, modifiez et gérez votre flotte de véhicules",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_muted"]
        )
        subtitle_label.pack(anchor="w", pady=(3, 0))

        search_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors["bg_secondary"],
            corner_radius=15
        )
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        search_frame.grid_columnconfigure(1, weight=1)

        search_label = ctk.CTkLabel(
            search_frame,
            text="🔍 Recherche:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        search_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        self.var_search = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.var_search,
            placeholder_text="Marque, modèle ou immatriculation...",
            font=ctk.CTkFont(size=13),
            height=40,
            fg_color=self.colors["bg_tertiary"],
            border_color=self.colors["accent_primary"],
            border_width=2
        )
        search_entry.grid(row=0, column=1, padx=(0, 10), pady=15, sticky="ew")

        search_btn = ctk.CTkButton(
            search_frame,
            text="Rechercher",
            command=self.on_search,
            fg_color=self.colors["accent_primary"],
            text_color="#000000",
            hover_color=self.colors["yellow_dark"],
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            width=120
        )
        search_btn.grid(row=0, column=2, padx=(0, 10), pady=15)

        clear_btn = ctk.CTkButton(
            search_frame,
            text="Effacer",
            command=self.on_clear_search,
            fg_color=self.colors["bg_tertiary"],
            text_color=self.colors["text_primary"],
            hover_color=self.colors["accent_primary"],
            font=ctk.CTkFont(size=13),
            height=40,
            width=100
        )
        clear_btn.grid(row=0, column=3, padx=(0, 20), pady=15)

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=2, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=3)
        content_frame.grid_columnconfigure(1, weight=2)
        content_frame.grid_rowconfigure(0, weight=1)

        list_container = ctk.CTkFrame(
            content_frame,
            fg_color=self.colors["bg_secondary"],
            corner_radius=20
        )
        list_container.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(1, weight=1)

        list_header = ctk.CTkFrame(list_container, fg_color="transparent")
        list_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 8))
        
        list_title = ctk.CTkLabel(
            list_header,
            text="📋 Liste des Voitures",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        list_title.pack(side="left")

        tree_container = ctk.CTkFrame(list_container, fg_color="transparent")
        tree_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Yellow.Treeview",
            background=self.colors["bg_tertiary"],
            foreground=self.colors["text_primary"],
            fieldbackground=self.colors["bg_tertiary"],
            rowheight=40,
            borderwidth=0,
            font=("Segoe UI", 11)
        )
        style.configure(
            "Yellow.Treeview.Heading",
            background=self.colors["accent_primary"],
            foreground="#000000",
            font=("Segoe UI", 12, "bold"),
            borderwidth=0,
            padding=12
        )
        style.map(
            "Yellow.Treeview",
            background=[("selected", self.colors["accent_primary"])],
            foreground=[("selected", "#000000")]
        )

        columns = ("id", "brand", "model", "year", "plate", "price", "status")
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            style="Yellow.Treeview"
        )

        headers = [
            ("id", "ID", 60),
            ("brand", "Marque", 120),
            ("model", "Modèle", 140),
            ("year", "Année", 80),
            ("plate", "Immatriculation", 140),
            ("price", "Prix/jour (TND)", 130),
            ("status", "Statut", 120),
        ]
        for col, text, width in headers:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ctk.CTkScrollbar(
            tree_container,
            orientation="vertical",
            command=self.tree.yview,
            button_color=self.colors["bg_tertiary"],
            button_hover_color=self.colors["accent_primary"]
        )
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(10, 0))
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        form_container = ctk.CTkFrame(
            content_frame,
            fg_color=self.colors["bg_secondary"],
            corner_radius=20
        )
        form_container.grid(row=0, column=1, sticky="nsew")
        form_container.grid_columnconfigure(0, weight=1)

        form_header = ctk.CTkFrame(form_container, fg_color="transparent")
        form_header.pack(fill="x", padx=20, pady=(15, 12))
        
        form_title = ctk.CTkLabel(
            form_header,
            text="✏️ Formulaire",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        form_title.pack(anchor="w")

        form_inner = ctk.CTkFrame(form_container, fg_color="transparent")
        form_inner.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.var_brand = ctk.StringVar()
        self.var_model = ctk.StringVar()
        self.var_year = ctk.StringVar()
        self.var_plate = ctk.StringVar()
        self.var_price = ctk.StringVar()
        self.var_status = ctk.StringVar(value="available")

        ctk.CTkLabel(
            form_inner,
            text="Marque *",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w", pady=(0, 5))
        brand_entry = ctk.CTkEntry(
            form_inner,
            textvariable=self.var_brand,
            placeholder_text="Ex: Toyota, Peugeot...",
            height=40,
            fg_color=self.colors["bg_tertiary"],
            border_color=self.colors["accent_primary"],
            border_width=2
        )
        brand_entry.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            form_inner,
            text="Modèle *",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w", pady=(0, 5))
        model_entry = ctk.CTkEntry(
            form_inner,
            textvariable=self.var_model,
            placeholder_text="Ex: Corolla, 208...",
            height=40,
            fg_color=self.colors["bg_tertiary"],
            border_color=self.colors["accent_primary"],
            border_width=2
        )
        model_entry.pack(fill="x", pady=(0, 15))

        row_frame = ctk.CTkFrame(form_inner, fg_color="transparent")
        row_frame.pack(fill="x", pady=(0, 15))
        row_frame.grid_columnconfigure(0, weight=1)
        row_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            row_frame,
            text="Année *",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))
        year_entry = ctk.CTkEntry(
            row_frame,
            textvariable=self.var_year,
            placeholder_text="2024",
            height=40,
            fg_color=self.colors["bg_tertiary"],
            border_color=self.colors["accent_primary"],
            border_width=2
        )
        year_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkLabel(
            row_frame,
            text="Immatriculation *",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).grid(row=0, column=1, sticky="w", pady=(0, 5))
        plate_entry = ctk.CTkEntry(
            row_frame,
            textvariable=self.var_plate,
            placeholder_text="AA-123-AA",
            height=40,
            fg_color=self.colors["bg_tertiary"],
            border_color=self.colors["accent_primary"],
            border_width=2
        )
        plate_entry.grid(row=1, column=1, sticky="ew")

        row_frame2 = ctk.CTkFrame(form_inner, fg_color="transparent")
        row_frame2.pack(fill="x", pady=(0, 20))
        row_frame2.grid_columnconfigure(0, weight=1)
        row_frame2.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            row_frame2,
            text="Prix/jour (TND) *",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))
        price_entry = ctk.CTkEntry(
            row_frame2,
            textvariable=self.var_price,
            placeholder_text="50.00",
            height=40,
            fg_color=self.colors["bg_tertiary"],
            border_color=self.colors["accent_primary"],
            border_width=2
        )
        price_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkLabel(
            row_frame2,
            text="Statut",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).grid(row=0, column=1, sticky="w", pady=(0, 5))
        status_combo = ctk.CTkComboBox(
            row_frame2,
            values=["available", "rented", "maintenance"],
            variable=self.var_status,
            height=40,
            fg_color=self.colors["bg_tertiary"],
            border_color=self.colors["accent_primary"],
            border_width=2,
            button_color=self.colors["accent_primary"],
            button_hover_color=self.colors["yellow_dark"],
            dropdown_fg_color=self.colors["bg_secondary"],
            dropdown_hover_color=self.colors["accent_primary"]
        )
        status_combo.grid(row=1, column=1, sticky="ew")

        btn_frame = ctk.CTkFrame(form_inner, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 0))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Enregistrer",
            command=self.on_save,
            fg_color=self.colors["accent_primary"],
            text_color="#000000",
            hover_color=self.colors["yellow_dark"],
            font=ctk.CTkFont(size=14, weight="bold"),
            height=50
        )
        save_btn.pack(fill="x", pady=(0, 10))

        delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Supprimer",
            command=self.on_delete,
            fg_color=self.colors["danger"],
            text_color="#FFFFFF",
            hover_color="#DC2626",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=45,
            corner_radius=10
        )
        delete_btn.pack(fill="x", pady=(0, 10))

        clear_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Vider formulaire",
            command=self.clear_form,
            fg_color=self.colors["bg_tertiary"],
            text_color=self.colors["text_primary"],
            hover_color=self.colors["accent_primary"],
            font=ctk.CTkFont(size=13),
            height=40
        )
        clear_btn.pack(fill="x")

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        cars = CarsService.list_cars(self.var_search.get() or None)
        for car in cars:
            status_display = {
                "available": "✅ Disponible",
                "rented": "🔑 En location",
                "maintenance": "🔧 Maintenance"
            }.get(car["status"], car["status"])
            
            self.tree.insert(
                "",
                "end",
                iid=str(car["id"]),
                values=(
                    car["id"],
                    car["brand"],
                    car["model"],
                    car["year"],
                    car["plate"],
                    f"{car['price_per_day']:.2f} TND",
                    status_display,
                ),
            )

    def on_search(self):
        self.refresh()

    def on_clear_search(self):
        self.var_search.set("")
        self.refresh()

    def on_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        item_id = sel[0]
        self.selected_id = int(item_id)
        values = self.tree.item(item_id, "values")
        _, brand, model, year, plate, price_str, status_display = values
        self.var_brand.set(brand)
        self.var_model.set(model)
        self.var_year.set(str(year))
        self.var_plate.set(plate)
        price = price_str.replace(" TND", "").strip()
        self.var_price.set(price)
        status_map = {
            "Disponible": "available",
            "location": "rented",
            "Maintenance": "maintenance"
        }
        for key, value in status_map.items():
            if key in status_display:
                self.var_status.set(value)
                break

    def clear_form(self):
        self.selected_id = None
        self.var_brand.set("")
        self.var_model.set("")
        self.var_year.set("")
        self.var_plate.set("")
        self.var_price.set("")
        self.var_status.set("available")

    def on_new(self):
        self.clear_form()

    def on_save(self):
        try:
            data = {
                "brand": self.var_brand.get().strip(),
                "model": self.var_model.get().strip(),
                "year": int(self.var_year.get()),
                "plate": self.var_plate.get().strip(),
                "price_per_day": float(self.var_price.get()),
                "status": self.var_status.get() or "available",
            }
            CarsService.save_car(self.selected_id, data)
            self.refresh()
            messagebox.showinfo("Succès", "Voiture enregistrée avec succès.")
            self.clear_form()
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))

    def on_delete(self):
        if not self.selected_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner une voiture.")
            return
        if (
            messagebox.askyesno(
                "Confirmation", "Supprimer cette voiture ? Cette action est définitive."
            )
            is False
        ):
            return
        try:
            CarsService.delete_car(self.selected_id)
            self.clear_form()
            self.refresh()
            messagebox.showinfo("Succès", "Voiture supprimée avec succès.")
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))


class CustomersView(ctk.CTkFrame):
    def __init__(self, parent, colors):
        super().__init__(parent, fg_color=colors["bg_primary"])
        self.colors = colors
        self.selected_id = None
        self._build()
        self.refresh()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="👥 Gestion des Clients",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.colors["accent_primary"]
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Créez, modifiez et gérez vos clients",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_muted"]
        )
        subtitle_label.pack(anchor="w", pady=(3, 0))

        search_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors["bg_secondary"],
            corner_radius=15
        )
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        search_frame.grid_columnconfigure(1, weight=1)

        search_label = ctk.CTkLabel(
            search_frame,
            text="🔍 Recherche:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        search_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        self.var_search = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.var_search,
            placeholder_text="Nom, CIN ou téléphone...",
            font=ctk.CTkFont(size=13),
            height=40,
            fg_color=self.colors["bg_tertiary"],
            border_color=self.colors["accent_primary"],
            border_width=2
        )
        search_entry.grid(row=0, column=1, padx=(0, 10), pady=15, sticky="ew")

        search_btn = ctk.CTkButton(
            search_frame,
            text="Rechercher",
            command=self.on_search,
            fg_color=self.colors["accent_primary"],
            text_color="#000000",
            hover_color=self.colors["yellow_dark"],
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            width=120
        )
        search_btn.grid(row=0, column=2, padx=(0, 10), pady=15)

        clear_btn = ctk.CTkButton(
            search_frame,
            text="Effacer",
            command=self.on_clear_search,
            fg_color=self.colors["bg_tertiary"],
            text_color=self.colors["text_primary"],
            hover_color=self.colors["accent_primary"],
            font=ctk.CTkFont(size=13),
            height=40,
            width=100
        )
        clear_btn.grid(row=0, column=3, padx=(0, 20), pady=15)

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=2, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=3)
        content_frame.grid_columnconfigure(1, weight=2)
        content_frame.grid_rowconfigure(0, weight=1)

        list_frame = ctk.CTkFrame(
            content_frame,
            fg_color=self.colors["bg_secondary"],
            corner_radius=20
        )
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)
        
        list_header = ctk.CTkFrame(list_frame, fg_color="transparent")
        list_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 8))
        
        list_title = ctk.CTkLabel(
            list_header,
            text="📋 Liste des Clients",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        list_title.pack(side="left")

        tree_container = ctk.CTkFrame(list_frame, fg_color="transparent")
        tree_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Yellow.Treeview",
            background=self.colors["bg_tertiary"],
            foreground=self.colors["text_primary"],
            fieldbackground=self.colors["bg_tertiary"],
            rowheight=40,
            borderwidth=0,
            font=("Segoe UI", 11)
        )
        style.configure(
            "Yellow.Treeview.Heading",
            background=self.colors["accent_primary"],
            foreground="#000000",
            font=("Segoe UI", 12, "bold"),
            borderwidth=0,
            padding=12
        )
        style.map(
            "Yellow.Treeview",
            background=[("selected", self.colors["accent_primary"])],
            foreground=[("selected", "#000000")]
        )

        columns = ("id", "first_name", "last_name", "cin", "phone", "email")
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            style="Yellow.Treeview"
        )
        for col, text, width in [
            ("id", "ID", 60),
            ("first_name", "Prénom", 120),
            ("last_name", "Nom", 120),
            ("cin", "CIN", 120),
            ("phone", "Téléphone", 140),
            ("email", "Email", 180),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ctk.CTkScrollbar(
            tree_container,
            orientation="vertical",
            command=self.tree.yview,
            button_color=self.colors["bg_tertiary"],
            button_hover_color=self.colors["accent_primary"]
        )
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(10, 0))
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        form = ctk.CTkFrame(
            content_frame,
            fg_color=self.colors["bg_secondary"],
            corner_radius=20
        )
        form.grid(row=0, column=1, sticky="nsew")
        form.grid_columnconfigure(0, weight=1)

        form_header = ctk.CTkFrame(form, fg_color="transparent")
        form_header.pack(fill="x", padx=20, pady=(15, 12))
        
        form_title = ctk.CTkLabel(
            form_header,
            text="✏️ Formulaire",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        form_title.pack(anchor="w")

        form_inner = ctk.CTkFrame(form, fg_color="transparent")
        form_inner.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.var_first_name = ctk.StringVar()
        self.var_last_name = ctk.StringVar()
        self.var_cin = ctk.StringVar()
        self.var_phone = ctk.StringVar()
        self.var_email = ctk.StringVar()

        ctk.CTkLabel(
            form_inner,
            text="Prénom *",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w", pady=(0, 5))
        first_name_entry = ctk.CTkEntry(
            form_inner,
            textvariable=self.var_first_name,
            placeholder_text="Ex: Ali",
            height=40,
            fg_color=self.colors["bg_tertiary"],
            border_color=self.colors["accent_primary"],
            border_width=2
        )
        first_name_entry.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            form_inner,
            text="Nom *",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w", pady=(0, 5))
        last_name_entry = ctk.CTkEntry(
            form_inner,
            textvariable=self.var_last_name,
            placeholder_text="Ex: Ben Salah",
            height=40,
            fg_color=self.colors["bg_tertiary"],
            border_color=self.colors["accent_primary"],
            border_width=2
        )
        last_name_entry.pack(fill="x", pady=(0, 15))

        row_frame = ctk.CTkFrame(form_inner, fg_color="transparent")
        row_frame.pack(fill="x", pady=(0, 15))
        row_frame.grid_columnconfigure(0, weight=1)
        row_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            row_frame,
            text="CIN *",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))
        cin_entry = ctk.CTkEntry(
            row_frame,
            textvariable=self.var_cin,
            placeholder_text="CIN001",
            height=40,
            fg_color=self.colors["bg_tertiary"],
            border_color=self.colors["accent_primary"],
            border_width=2
        )
        cin_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkLabel(
            row_frame,
            text="Téléphone *",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).grid(row=0, column=1, sticky="w", pady=(0, 5))
        phone_entry = ctk.CTkEntry(
            row_frame,
            textvariable=self.var_phone,
            placeholder_text="0600000001",
            height=40,
            fg_color=self.colors["bg_tertiary"],
            border_color=self.colors["accent_primary"],
            border_width=2
        )
        phone_entry.grid(row=1, column=1, sticky="ew")

        ctk.CTkLabel(
            form_inner,
            text="Email",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w", pady=(0, 5))
        email_entry = ctk.CTkEntry(
            form_inner,
            textvariable=self.var_email,
            placeholder_text="email@example.com",
            height=40,
            fg_color=self.colors["bg_tertiary"],
            border_color=self.colors["accent_primary"],
            border_width=2
        )
        email_entry.pack(fill="x", pady=(0, 20))

        btn_frame = ctk.CTkFrame(form_inner, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 0))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Enregistrer",
            command=self.on_save,
            fg_color=self.colors["accent_primary"],
            text_color="#000000",
            hover_color=self.colors["yellow_dark"],
            font=ctk.CTkFont(size=14, weight="bold"),
            height=50
        )
        save_btn.pack(fill="x", pady=(0, 10))

        delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Supprimer",
            command=self.on_delete,
            fg_color=self.colors["danger"],
            text_color="#FFFFFF",
            hover_color="#DC2626",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=45,
            corner_radius=10
        )
        delete_btn.pack(fill="x", pady=(0, 10))

        clear_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Vider formulaire",
            command=self.clear_form,
            fg_color=self.colors["bg_tertiary"],
            text_color=self.colors["text_primary"],
            hover_color=self.colors["accent_primary"],
            font=ctk.CTkFont(size=13),
            height=40
        )
        clear_btn.pack(fill="x")

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        customers = CustomersRepo.list_customers(self.var_search.get() or None)
        for c in customers:
            self.tree.insert(
                "",
                "end",
                iid=str(c["id"]),
                values=(
                    c["id"],
                    c["first_name"],
                    c["last_name"],
                    c["cin"],
                    c["phone"],
                    c["email"],
                ),
            )

    def on_search(self):
        self.refresh()

    def on_clear_search(self):
        self.var_search.set("")
        self.refresh()

    def on_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        item_id = sel[0]
        self.selected_id = int(item_id)
        values = self.tree.item(item_id, "values")
        _, first_name, last_name, cin, phone, email = values
        self.var_first_name.set(first_name)
        self.var_last_name.set(last_name)
        self.var_cin.set(cin)
        self.var_phone.set(phone)
        self.var_email.set(email)

    def clear_form(self):
        self.selected_id = None
        self.var_first_name.set("")
        self.var_last_name.set("")
        self.var_cin.set("")
        self.var_phone.set("")
        self.var_email.set("")

    def on_new(self):
        self.clear_form()

    def on_save(self):
        try:
            data = {
                "first_name": self.var_first_name.get().strip(),
                "last_name": self.var_last_name.get().strip(),
                "cin": self.var_cin.get().strip(),
                "phone": self.var_phone.get().strip(),
                "email": self.var_email.get().strip() or None,
            }
            if self.selected_id:
                CustomersRepo.update_customer(self.selected_id, data)
            else:
                self.selected_id = CustomersRepo.create_customer(data)
            self.refresh()
            messagebox.showinfo("Succès", "Client enregistré avec succès.")
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))

    def on_delete(self):
        if not self.selected_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner un client.")
            return
        if (
            messagebox.askyesno(
                "Confirmation", "Supprimer ce client ? Cette action est définitive."
            )
            is False
        ):
            return
        try:
            CustomersRepo.delete_customer(self.selected_id)
            self.clear_form()
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))


class RentalsView(ctk.CTkFrame):
    def __init__(self, parent, colors):
        super().__init__(parent, fg_color=colors["bg_primary"])
        self.colors = colors
        self.selected_id = None
        self._build()
        self.refresh()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📋 Gestion des Locations",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.colors["accent_primary"]
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Créez et gérez les locations de véhicules",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_muted"]
        )
        subtitle_label.pack(anchor="w", pady=(3, 0))

        filter_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors["bg_secondary"],
            corner_radius=15
        )
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        filter_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(filter_frame, text="Client:", font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.var_filter_customer = ctk.StringVar()
        self.cb_filter_customer = ttk.Combobox(filter_frame, textvariable=self.var_filter_customer, width=30, state="readonly")
        self.cb_filter_customer.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        ctk.CTkLabel(filter_frame, text="Date début:", font=ctk.CTkFont(size=13)).grid(row=0, column=2, padx=5, pady=10, sticky="w")
        self.var_filter_start = ctk.StringVar()
        filter_start_entry = ctk.CTkEntry(filter_frame, textvariable=self.var_filter_start, width=120, placeholder_text="YYYY-MM-DD")
        filter_start_entry.grid(row=0, column=3, padx=5, pady=10)

        ctk.CTkLabel(filter_frame, text="Date fin:", font=ctk.CTkFont(size=13)).grid(row=0, column=4, padx=5, pady=10, sticky="w")
        self.var_filter_end = ctk.StringVar()
        filter_end_entry = ctk.CTkEntry(filter_frame, textvariable=self.var_filter_end, width=120, placeholder_text="YYYY-MM-DD")
        filter_end_entry.grid(row=0, column=5, padx=5, pady=10)

        filter_btn = ctk.CTkButton(
            filter_frame,
            text="Filtrer",
            command=self.on_filter,
            fg_color=self.colors["accent_primary"],
            text_color="#000000",
            width=100
        )
        filter_btn.grid(row=0, column=6, padx=5, pady=10)

        clear_filter_btn = ctk.CTkButton(
            filter_frame,
            text="Réinitialiser",
            command=self.on_clear_filters,
            fg_color=self.colors["bg_tertiary"],
            text_color=self.colors["text_primary"],
            width=100
        )
        clear_filter_btn.grid(row=0, column=7, padx=10, pady=10)

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=2, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=3)
        content_frame.grid_columnconfigure(1, weight=2)
        content_frame.grid_rowconfigure(0, weight=1)

        list_frame = ctk.CTkFrame(
            content_frame,
            fg_color=self.colors["bg_secondary"],
            corner_radius=20
        )
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)
        
        list_header = ctk.CTkFrame(list_frame, fg_color="transparent")
        list_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 8))
        
        list_title = ctk.CTkLabel(
            list_header,
            text="📋 Liste des Locations",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        list_title.pack(side="left")

        tree_container = ctk.CTkFrame(list_frame, fg_color="transparent")
        tree_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Yellow.Treeview",
            background=self.colors["bg_tertiary"],
            foreground=self.colors["text_primary"],
            fieldbackground=self.colors["bg_tertiary"],
            rowheight=40,
            borderwidth=0,
            font=("Segoe UI", 11)
        )
        style.configure(
            "Yellow.Treeview.Heading",
            background=self.colors["accent_primary"],
            foreground="#000000",
            font=("Segoe UI", 12, "bold"),
            borderwidth=0,
            padding=12
        )
        style.map(
            "Yellow.Treeview",
            background=[("selected", self.colors["accent_primary"])],
            foreground=[("selected", "#000000")]
        )

        columns = ("id", "client", "car", "start_date", "end_date", "days", "total", "status")
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            style="Yellow.Treeview"
        )
        for col, text, width in [
            ("id", "ID", 60),
            ("client", "Client", 150),
            ("car", "Voiture", 180),
            ("start_date", "Début", 100),
            ("end_date", "Fin", 100),
            ("days", "Jours", 70),
            ("total", "Total", 120),
            ("status", "Statut", 120),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ctk.CTkScrollbar(
            tree_container,
            orientation="vertical",
            command=self.tree.yview,
            button_color=self.colors["bg_tertiary"],
            button_hover_color=self.colors["accent_primary"]
        )
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(10, 0))
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        form = ctk.CTkFrame(
            content_frame,
            fg_color=self.colors["bg_secondary"],
            corner_radius=20
        )
        form.grid(row=0, column=1, sticky="nsew")
        form.grid_columnconfigure(0, weight=1)

        form_header = ctk.CTkFrame(form, fg_color="transparent")
        form_header.pack(fill="x", padx=20, pady=(15, 12))
        
        form_title = ctk.CTkLabel(
            form_header,
            text="✏️ Formulaire",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        form_title.pack(anchor="w")

        form_inner = ctk.CTkFrame(form, fg_color="transparent")
        form_inner.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.var_customer = ctk.StringVar()
        self.var_car = ctk.StringVar()
        self.var_start_date = ctk.StringVar()
        self.var_end_date = ctk.StringVar()
        self.var_total = ctk.StringVar()

        ctk.CTkLabel(
            form_inner,
            text="Client *",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w", pady=(0, 5))
        self.cb_customer = ttk.Combobox(form_inner, textvariable=self.var_customer, state="readonly")
        self.cb_customer.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            form_inner,
            text="Voiture *",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w", pady=(0, 5))
        self.cb_car = ttk.Combobox(form_inner, textvariable=self.var_car, state="readonly")
        self.cb_car.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            form_inner,
            text="Date début * (YYYY-MM-DD)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w", pady=(0, 5))
        start_date_entry = ctk.CTkEntry(
            form_inner,
            textvariable=self.var_start_date,
            placeholder_text="2024-12-25",
            height=40,
            fg_color=self.colors["bg_tertiary"],
            border_color=self.colors["accent_primary"],
            border_width=2
        )
        start_date_entry.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            form_inner,
            text="Date fin * (YYYY-MM-DD)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w", pady=(0, 5))
        end_date_entry = ctk.CTkEntry(
            form_inner,
            textvariable=self.var_end_date,
            placeholder_text="2024-12-30",
            height=40,
            fg_color=self.colors["bg_tertiary"],
            border_color=self.colors["accent_primary"],
            border_width=2
        )
        end_date_entry.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            form_inner,
            text="Total calculé",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w", pady=(0, 5))
        entry_total = ctk.CTkEntry(
            form_inner,
            textvariable=self.var_total,
            state="readonly",
            height=40,
            fg_color=self.colors["bg_tertiary"]
        )
        entry_total.pack(fill="x", pady=(0, 20))

        btn_frame = ctk.CTkFrame(form_inner, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 0))

        calculate_btn = ctk.CTkButton(
            btn_frame,
            text="🧮 Calculer total",
            command=self.on_calculate,
            fg_color=self.colors["bg_tertiary"],
            text_color=self.colors["text_primary"],
            hover_color=self.colors["accent_primary"],
            font=ctk.CTkFont(size=13),
            height=40
        )
        calculate_btn.pack(fill="x", pady=(0, 8))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="✅ Valider location",
            command=self.on_save,
            fg_color=self.colors["accent_primary"],
            text_color="#000000",
            hover_color=self.colors["yellow_dark"],
            font=ctk.CTkFont(size=14, weight="bold"),
            height=50
        )
        save_btn.pack(fill="x", pady=(0, 8))

        return_btn = ctk.CTkButton(
            btn_frame,
            text="🔙 Retour véhicule",
            command=self.on_return,
            fg_color=self.colors["success"],
            text_color="#FFFFFF",
            hover_color="#059669",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=45
        )
        return_btn.pack(fill="x", pady=(0, 8))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Annuler location",
            command=self.on_cancel,
            fg_color=self.colors["danger"],
            text_color="#FFFFFF",
            hover_color="#DC2626",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=45
        )
        cancel_btn.pack(fill="x")

        self._load_customers_and_cars()

    def _load_customers_and_cars(self):
        customers = CustomersRepo.list_customers()
        self.customers_map = {f"{c['first_name']} {c['last_name']} ({c['cin']})": c["id"] for c in customers}
        self.cb_customer["values"] = list(self.customers_map.keys())
        self.cb_filter_customer["values"] = [""] + list(self.customers_map.keys())

        cars = CarsService.list_available_cars()
        self.cars_map = {f"{car['brand']} {car['model']} ({car['plate']}) - {car['price_per_day']}": car["id"] for car in cars}
        self.cb_car["values"] = list(self.cars_map.keys())

    def refresh(self):
        self._load_customers_and_cars()
        for item in self.tree.get_children():
            self.tree.delete(item)

        customer_id = None
        if self.var_filter_customer.get():
            customer_id = self.customers_map.get(self.var_filter_customer.get())
        start = self.var_filter_start.get() or None
        end = self.var_filter_end.get() or None

        rentals = RentalsService.list_rentals(customer_id=customer_id, start_date=start, end_date=end)
        for r in rentals:
            client = f"{r['first_name']} {r['last_name']}"
            car = f"{r['brand']} {r['model']} ({r['plate']})"
            total = format_money(r["total"])
            self.tree.insert(
                "",
                "end",
                iid=str(r["id"]),
                values=(r["id"], client, car, r["start_date"], r["end_date"], r["days"], total, r["status"]),
            )

    def on_filter(self):
        self.refresh()

    def on_clear_filters(self):
        self.var_filter_customer.set("")
        self.var_filter_start.set("")
        self.var_filter_end.set("")
        self.refresh()

    def on_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        item_id = sel[0]
        self.selected_id = int(item_id)
        values = self.tree.item(item_id, "values")
        _, client, car, start, end, days, total, status = values
        self.var_customer.set(next((k for k in self.customers_map.keys() if k.startswith(client)), ""))
        self.var_car.set(next((k for k in self.cars_map.keys() if k.startswith(car.split("(")[0].strip())), ""))
        self.var_start_date.set(start)
        self.var_end_date.set(end)
        self.var_total.set(total)

    def clear_form(self):
        self.selected_id = None
        self.var_customer.set("")
        self.var_car.set("")
        self.var_start_date.set("")
        self.var_end_date.set("")
        self.var_total.set("")

    def on_new(self):
        self.clear_form()

    def _collect_form_data(self, for_calculation_only=False):
        customer_label = self.var_customer.get()
        car_label = self.var_car.get()
        start = self.var_start_date.get().strip()
        end = self.var_end_date.get().strip()

        customer_id = self.customers_map.get(customer_label)
        car_id = self.cars_map.get(car_label)
        if not customer_id:
            raise ValueError("Veuillez sélectionner un client.")
        if not car_id:
            raise ValueError("Veuillez sélectionner une voiture.")

        data = {
            "customer_id": customer_id,
            "car_id": car_id,
            "start_date": start,
            "end_date": end,
        }
        if for_calculation_only:
            return data
        return data

    def on_calculate(self):
        try:
            data = self._collect_form_data(for_calculation_only=True)
            days = RentalsService.calculate_days(data["start_date"], data["end_date"])
            self.var_total.set(f"{days} jours (total exact lors de la validation)")
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))

    def on_save(self):
        try:
            data = self._collect_form_data()
            rental_id = RentalsService.create_rental(data)
            self.selected_id = rental_id
            self.refresh()
            messagebox.showinfo("Succès", "Location créée avec succès.")
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))

    def on_return(self):
        if not self.selected_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner une location.")
            return
        if messagebox.askyesno("Confirmation", "Marquer ce véhicule comme 'retourné' ?") is False:
            return
        try:
            RentalsService.return_rental(self.selected_id)
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))

    def on_cancel(self):
        if not self.selected_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner une location.")
            return
        if messagebox.askyesno("Confirmation", "Annuler cette location ?") is False:
            return
        try:
            RentalsService.cancel_rental(self.selected_id)
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class CarRentalApp:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("FASTAUTO - Location de Voiture")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
        
        self.colors = {
            "bg_primary": "#0F172A",
            "bg_secondary": "#1E293B",
            "bg_tertiary": "#334155",
            "accent_primary": "#FCD34D",
            "accent_secondary": "#FDE047",
            "accent_gold": "#FBBF24",
            "yellow_dark": "#F59E0B",
            "yellow_light": "#FEF3C7",
            "text_primary": "#F8FAFC",
            "text_secondary": "#CBD5E1",
            "text_muted": "#94A3B8",
            "success": "#10B981",
            "warning": "#F59E0B",
            "danger": "#EF4444",
        }

        try:
            setup_database()
        except Exception as e:
            messagebox.showwarning(
                "Database Connection Warning",
                f"Could not connect to MySQL database:\n{str(e)}\n\n"
                "Please make sure:\n"
                "1. XAMPP MySQL is running\n"
                "2. Database 'car_rental_db' exists\n\n"
                "The application will continue, but database features may not work."
            )
        
        self._build_layout()

    def _build_layout(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(
            self.root,
            width=280,
            corner_radius=0,
            fg_color=self.colors["bg_secondary"]
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
            height=120
        )
        logo_frame.pack(fill="x", padx=20, pady=(30, 20))
        
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        if os.path.exists(logo_path):
            try:
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((60, 60), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = ctk.CTkLabel(
                    logo_frame,
                    image=self.logo_photo,
                    text=""
                )
                logo_label.pack(anchor="w", pady=(0, 10))
            except:
                pass
        
        brand_label = ctk.CTkLabel(
            logo_frame,
            text="FASTAUTO 🇹🇳",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.colors["accent_primary"]
        )
        brand_label.pack(anchor="w", pady=(0, 5))
        
        subtitle_label = ctk.CTkLabel(
            logo_frame,
            text="Location & Dépannage - Tunisie",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_muted"]
        )
        subtitle_label.pack(anchor="w")

        nav_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        nav_frame.pack(fill="x", padx=15, pady=10)

        self.nav_buttons = {}
        nav_items = [
            ("📊 Dashboard", "dashboard", DashboardView),
            ("🚗 Voitures", "cars", CarsView),
            ("👥 Clients", "customers", CustomersView),
            ("📋 Locations", "rentals", RentalsView),
        ]

        for text, key, view_class in nav_items:
            btn = ctk.CTkButton(
                nav_frame,
                text=text,
                font=ctk.CTkFont(size=16, weight="normal"),
                height=50,
                corner_radius=12,
                fg_color="transparent",
                text_color=self.colors["text_secondary"],
                hover_color=self.colors["bg_tertiary"],
                anchor="w",
                command=lambda k=key, vc=view_class: self.show_view(k, vc)
            )
            btn.pack(fill="x", pady=5, padx=5)
            self.nav_buttons[key] = btn

        footer_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        footer_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        footer_label = ctk.CTkLabel(
            footer_frame,
            text="v2.0 - Tunisie 🇹🇳 | CustomTkinter",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_muted"]
        )
        footer_label.pack()

        self.content = ctk.CTkFrame(
            self.root,
            fg_color=self.colors["bg_primary"],
            corner_radius=0
        )
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.views = {}
        self.current_view = None
        self.current_view_key = None

        self.show_view("dashboard", DashboardView)

    def show_view(self, key, view_class):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(
                    fg_color=self.colors["accent_primary"],
                    text_color="#000000",
                    hover_color=self.colors["yellow_dark"]
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=self.colors["text_secondary"],
                    hover_color=self.colors["bg_tertiary"]
                )

        if self.current_view is not None:
            self.current_view.grid_forget()

        if key not in self.views:
            frame = view_class(self.content, self.colors)
            self.views[key] = frame
        self.current_view = self.views[key]
        self.current_view_key = key
        self.current_view.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        if hasattr(self.current_view, "refresh"):
            try:
                self.current_view.refresh()
            except Exception as exc:
                messagebox.showerror("Erreur", str(exc))


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Point d'entrée de l'application"""
    root = ctk.CTk()
    app = CarRentalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

