import customtkinter as ctk
from tkinter import ttk, messagebox

from repositories import customers_repo
from services import rentals_service, cars_service
from utils.formatters import format_money


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

        # Header
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

        # Filters
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

        # Main Content Area
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=2, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=3)
        content_frame.grid_columnconfigure(1, weight=2)
        content_frame.grid_rowconfigure(0, weight=1)

        # List Section
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

        # Style Treeview
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

        # Form Section
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

        # Customer
        ctk.CTkLabel(
            form_inner,
            text="Client *",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w", pady=(0, 5))
        self.cb_customer = ttk.Combobox(form_inner, textvariable=self.var_customer, state="readonly")
        self.cb_customer.pack(fill="x", pady=(0, 15))

        # Car
        ctk.CTkLabel(
            form_inner,
            text="Voiture *",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w", pady=(0, 5))
        self.cb_car = ttk.Combobox(form_inner, textvariable=self.var_car, state="readonly")
        self.cb_car.pack(fill="x", pady=(0, 15))

        # Dates
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

        # Total
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

        # Buttons
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
        """Calculate rental days and display total."""
        try:
            data = self._collect_form_data(for_calculation_only=True)
            days = rentals_service.calculate_days(data["start_date"], data["end_date"])
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

