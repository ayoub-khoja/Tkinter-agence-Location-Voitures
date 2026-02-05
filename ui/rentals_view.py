import tkinter as tk
from tkinter import ttk, messagebox

from repositories import customers_repo
from services import rentals_service, cars_service
from utils import validators
from utils.formatters import format_money


class RentalsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=16)
        self.configure(style="Content.TFrame")
        self.selected_id = None
        self._build()
        self.refresh()

    def _build(self):
        header = ttk.Label(self, text="Locations", style="Title.TLabel")
        header.grid(row=0, column=0, sticky="w")

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)

        # filters
        filter_frame = ttk.Frame(self, style="Content.TFrame")
        filter_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 8))

        ttk.Label(filter_frame, text="Client:").grid(row=0, column=0, sticky="w")
        self.var_filter_customer = tk.StringVar()
        self.cb_filter_customer = ttk.Combobox(filter_frame, textvariable=self.var_filter_customer, width=30, state="readonly")
        self.cb_filter_customer.grid(row=0, column=1, padx=4)

        ttk.Label(filter_frame, text="Date début (YYYY-MM-DD):").grid(row=0, column=2, sticky="w")
        self.var_filter_start = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.var_filter_start, width=12).grid(row=0, column=3, padx=4)

        ttk.Label(filter_frame, text="Date fin (YYYY-MM-DD):").grid(row=0, column=4, sticky="w")
        self.var_filter_end = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.var_filter_end, width=12).grid(row=0, column=5, padx=4)

        ttk.Button(filter_frame, text="Filtrer", command=self.on_filter).grid(row=0, column=6, padx=(8, 4))
        ttk.Button(filter_frame, text="Réinitialiser", command=self.on_clear_filters).grid(row=0, column=7, padx=(4, 0))

        # list
        list_frame = ttk.Frame(self, style="Content.TFrame")
        list_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 8))
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        columns = ("id", "client", "car", "start_date", "end_date", "days", "total", "status")
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            style="Dark.Treeview",
        )
        for col, text, width in [
            ("id", "ID", 50),
            ("client", "Client", 150),
            ("car", "Voiture", 160),
            ("start_date", "Début", 90),
            ("end_date", "Fin", 90),
            ("days", "Jours", 60),
            ("total", "Total", 90),
            ("status", "Statut", 90),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # form
        form = ttk.LabelFrame(self, text="Nouvelle location / Détails", padding=12)
        form.grid(row=2, column=1, sticky="nsew")
        for i in range(4):
            form.columnconfigure(i, weight=1)

        self.var_customer = tk.StringVar()
        self.var_car = tk.StringVar()
        self.var_start_date = tk.StringVar()
        self.var_end_date = tk.StringVar()
        self.var_total = tk.StringVar()

        row = 0
        ttk.Label(form, text="Client *").grid(row=row, column=0, sticky="w")
        self.cb_customer = ttk.Combobox(form, textvariable=self.var_customer, state="readonly")
        self.cb_customer.grid(row=row, column=1, columnspan=3, sticky="ew", pady=2)

        row += 1
        ttk.Label(form, text="Voiture *").grid(row=row, column=0, sticky="w")
        self.cb_car = ttk.Combobox(form, textvariable=self.var_car, state="readonly")
        self.cb_car.grid(row=row, column=1, columnspan=3, sticky="ew", pady=2)

        row += 1
        ttk.Label(form, text="Date début * (YYYY-MM-DD)").grid(row=row, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_start_date).grid(row=row, column=1, sticky="ew", pady=2)
        ttk.Label(form, text="Date fin * (YYYY-MM-DD)").grid(row=row, column=2, sticky="w")
        ttk.Entry(form, textvariable=self.var_end_date).grid(row=row, column=3, sticky="ew", pady=2)

        row += 1
        ttk.Label(form, text="Total calculé").grid(row=row, column=0, sticky="w")
        entry_total = ttk.Entry(form, textvariable=self.var_total, state="readonly")
        entry_total.grid(row=row, column=1, sticky="ew", pady=2)

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=row + 1, column=0, columnspan=4, pady=(12, 0), sticky="ew")
        ttk.Button(btn_frame, text="Nouvelle location", command=self.on_new).pack(side="left", padx=(0, 4))
        ttk.Button(btn_frame, text="Calculer total", command=self.on_calculate).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Valider location", command=self.on_save).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Retour véhicule", command=self.on_return).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Annuler location", command=self.on_cancel).pack(side="left", padx=4)

        self._load_customers_and_cars()

    def _load_customers_and_cars(self):
        customers = customers_repo.list_customers()
        self.customers_map = {f"{c['first_name']} {c['last_name']} ({c['cin']})": c["id"] for c in customers}
        self.cb_customer["values"] = list(self.customers_map.keys())
        self.cb_filter_customer["values"] = [""] + list(self.customers_map.keys())

        cars = cars_service.list_available_cars()
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

        rentals = rentals_service.list_rentals(customer_id=customer_id, start_date=start, end_date=end)
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
        # validate dates if provided
        try:
            if self.var_filter_start.get():
                validators.validate_date(self.var_filter_start.get(), "Date début filtre")
            if self.var_filter_end.get():
                validators.validate_date(self.var_filter_end.get(), "Date fin filtre")
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))
            return
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
        start = validators.validate_date(self.var_start_date.get(), "Date début")
        end = validators.validate_date(self.var_end_date.get(), "Date fin")

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
            days = rentals_service.calculate_days(data["start_date"], data["end_date"])
            # need price from car
            # use list_available + fallback: we don't have direct car here, but service will recalc on save anyway
            # just display days
            self.var_total.set(f"{days} jours (total exact lors de la validation)")
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))

    def on_save(self):
        try:
            data = self._collect_form_data()
            rental_id = rentals_service.create_rental(data)
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
            rentals_service.return_rental(self.selected_id)
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
            rentals_service.cancel_rental(self.selected_id)
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))

