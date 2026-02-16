import customtkinter as ctk
from tkinter import ttk
from datetime import datetime

from repositories import cars_repo
from services import rentals_service
from utils.formatters import format_money


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, colors):
        super().__init__(parent, fg_color=colors["bg_primary"])
        self.colors = colors
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header Section with Welcome Message
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Welcome Section
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
        
        # Time-based greeting
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

        # KPI Cards with Enhanced Design
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.grid(row=1, column=0, sticky="nsew")
        kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        kpi_frame.grid_rowconfigure(0, weight=0)
        kpi_frame.grid_rowconfigure(1, weight=1)

        # Create enhanced KPI cards
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

        # Bottom Section: Latest Rentals
        bottom_frame = ctk.CTkFrame(kpi_frame, fg_color="transparent")
        bottom_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(25, 0))
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_rowconfigure(1, weight=1)

        # Table Header with Icon
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

        # Table Container with Modern Styling
        table_container = ctk.CTkFrame(
            bottom_frame,
            fg_color=self.colors["bg_secondary"],
            corner_radius=20
        )
        table_container.grid(row=1, column=0, sticky="nsew")
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(0, weight=1)

        # Inner table frame
        inner_table = ctk.CTkFrame(table_container, fg_color="transparent")
        inner_table.grid(row=0, column=0, sticky="nsew", padx=25, pady=25)
        inner_table.grid_columnconfigure(0, weight=1)
        inner_table.grid_rowconfigure(0, weight=1)

        # Create Treeview with enhanced styling
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure treeview style
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

        # Configure columns with better widths
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

        # Modern Scrollbar
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
        """Create an enhanced KPI card with gradient effect and better visual design"""
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

        # Top section with icon
        top_section = ctk.CTkFrame(card, fg_color="transparent")
        top_section.pack(fill="x", padx=25, pady=(25, 15))
        
        # Icon container with background
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
        
        # Title
        title_label = ctk.CTkLabel(
            top_section,
            text=title,
            font=ctk.CTkFont(size=13, weight="normal"),
            text_color=self.colors["text_muted"]
        )
        title_label.pack(side="left", padx=(15, 0), pady=15)

        # Value section
        value_section = ctk.CTkFrame(card, fg_color="transparent")
        value_section.pack(fill="x", padx=25, pady=(0, 25))
        
        value_label = ctk.CTkLabel(
            value_section,
            text="0",
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color=color
        )
        value_label.pack(anchor="w")

        # Decorative line
        line = ctk.CTkFrame(
            card,
            fg_color=color,
            height=3,
            corner_radius=2
        )
        line.pack(fill="x", padx=25, pady=(0, 0))

        return value_label

    def refresh(self):
        # KPIs
        cars = cars_repo.list_cars()
        total_cars = len(cars)
        available = len([c for c in cars if c["status"] == "available"])
        rented = len([c for c in cars if c["status"] == "rented"])
        revenue = rentals_service.total_revenue()

        self.lbl_total_cars.configure(text=str(total_cars))
        self.lbl_available.configure(text=str(available))
        self.lbl_rented.configure(text=str(rented))
        self.lbl_revenue.configure(text=format_money(revenue))

        # Latest rentals with enhanced formatting
        for item in self.tree.get_children():
            self.tree.delete(item)

        rentals = rentals_service.latest_rentals(5)
        
        if not rentals:
            # Show empty state
            self.tree.insert(
                "", "end",
                values=("", "Aucune location", "", "", "", "")
            )
        else:
            for rental in rentals:
                client = f"{rental['first_name']} {rental['last_name']}"
                car = f"{rental['brand']} {rental['model']}"
                plate = f"({rental['plate']})"
                period = f"{rental['start_date']} → {rental['end_date']}"
                total = format_money(rental["total"])
                status = rental["status"]
                
                # Enhanced status display with emojis
                status_display = {
                    "active": "🟢 Actif",
                    "returned": "✅ Retourné",
                    "cancelled": "❌ Annulé"
                }.get(status, f"📌 {status.capitalize()}")
                
                self.tree.insert(
                    "", "end",
                    values=(rental["id"], client, f"{car} {plate}", period, total, status_display)
                )
