import tkinter as tk
from tkinter import ttk

from repositories import cars_repo
from services import rentals_service
from utils.formatters import format_money


class DashboardView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=16)
        self.configure(style="Content.TFrame")
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Simple header text
        header = ttk.Label(self, text="Dashboard", style="Title.TLabel")
        header.grid(row=0, column=0, sticky="w", pady=(0, 4))

        # KPI frame
        kpi_frame = ttk.Frame(self, style="Content.TFrame")
        kpi_frame.grid(row=1, column=0, sticky="ew", pady=(8, 8))
        for i in range(4):
            kpi_frame.columnconfigure(i, weight=1)

        self.lbl_total_cars = self._kpi_card(kpi_frame, 0, "Total voitures")
        self.lbl_available = self._kpi_card(kpi_frame, 1, "Disponibles")
        self.lbl_rented = self._kpi_card(kpi_frame, 2, "En location")
        self.lbl_revenue = self._kpi_card(kpi_frame, 3, "Revenus total")

        # latest rentals
        latest_frame = ttk.LabelFrame(
            self,
            text="Dernières locations",
            padding=8,
        )
        latest_frame.grid(row=2, column=0, sticky="nsew", pady=(4, 0))
        latest_frame.rowconfigure(0, weight=1)
        latest_frame.columnconfigure(0, weight=1)

        columns = ("id", "client", "car", "period", "total", "status")
        self.tree = ttk.Treeview(
            latest_frame,
            columns=columns,
            show="headings",
            height=5,
            style="Dark.Treeview",
        )
        for col, text, width in [
            ("id", "ID", 60),
            ("client", "Client", 160),
            ("car", "Voiture", 160),
            ("period", "Période", 160),
            ("total", "Total", 100),
            ("status", "Statut", 100),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            latest_frame, orient="vertical", command=self.tree.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.refresh()

    def _kpi_card(self, parent, column, title):
        frame = ttk.Frame(parent, style="Content.TFrame", padding=12)
        frame.grid(row=0, column=column, sticky="ew", padx=4)
        lbl_title = ttk.Label(frame, text=title, style="Header.TLabel")
        lbl_title.pack(anchor="w")
        lbl_value = ttk.Label(
            frame,
            text="0",
            style="KPIValue.TLabel",
        )
        lbl_value.pack(anchor="w", pady=(4, 0))
        return lbl_value

    def refresh(self):
        # KPIs
        cars = cars_repo.list_cars()
        total_cars = len(cars)
        available = len([c for c in cars if c["status"] == "available"])
        rented = len([c for c in cars if c["status"] == "rented"])
        revenue = rentals_service.total_revenue()

        self.lbl_total_cars.config(text=str(total_cars))
        self.lbl_available.config(text=str(available))
        self.lbl_rented.config(text=str(rented))
        self.lbl_revenue.config(text=format_money(revenue))

        # latest rentals
        for item in self.tree.get_children():
            self.tree.delete(item)

        for rental in rentals_service.latest_rentals(5):
            client = f"{rental['first_name']} {rental['last_name']}"
            car = f"{rental['brand']} {rental['model']} ({rental['plate']})"
            period = f"{rental['start_date']} → {rental['end_date']}"
            total = format_money(rental["total"])
            self.tree.insert(
                "", "end", values=(rental["id"], client, car, period, total, rental["status"])
            )

