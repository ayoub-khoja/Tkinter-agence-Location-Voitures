import customtkinter as ctk
from tkinter import ttk, messagebox

from services import cars_service


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

        # Header
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

        # Search Section
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

        # Main Content Area
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=2, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=3)
        content_frame.grid_columnconfigure(1, weight=2)
        content_frame.grid_rowconfigure(0, weight=1)

        # List Section
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

        # Treeview Container
        tree_container = ctk.CTkFrame(list_container, fg_color="transparent")
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

        # Form Section
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

        # Form Fields
        self.var_brand = ctk.StringVar()
        self.var_model = ctk.StringVar()
        self.var_year = ctk.StringVar()
        self.var_plate = ctk.StringVar()
        self.var_price = ctk.StringVar()
        self.var_status = ctk.StringVar(value="available")

        # Brand
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

        # Model
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

        # Year and Plate in row
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

        # Price and Status in row
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

        # Buttons
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
        cars = cars_service.list_cars(self.var_search.get() or None)
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
        # Extract price number from "XX.XX TND"
        price = price_str.replace(" TND", "").strip()
        self.var_price.set(price)
        # Extract status from display
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
            cars_service.save_car(self.selected_id, data)
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
            cars_service.delete_car(self.selected_id)
            self.clear_form()
            self.refresh()
            messagebox.showinfo("Succès", "Voiture supprimée avec succès.")
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))
