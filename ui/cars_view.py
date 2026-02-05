import tkinter as tk
from tkinter import ttk, messagebox

from services import cars_service
from utils import validators


class CarsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=16)
        self.configure(style="Content.TFrame")
        self.selected_id = None
        self._build()
        self.refresh()

    def _build(self):
        header = ttk.Label(self, text="Voitures", style="Title.TLabel")
        header.grid(row=0, column=0, sticky="w")

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)

        # search
        search_frame = ttk.Frame(self, style="Content.TFrame")
        search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 8))
        ttk.Label(search_frame, text="Recherche (marque / modèle / immatriculation):").pack(
            side="left"
        )
        self.var_search = tk.StringVar()
        entry_search = ttk.Entry(search_frame, textvariable=self.var_search, width=40)
        entry_search.pack(side="left", padx=6)
        ttk.Button(search_frame, text="Rechercher", command=self.on_search).pack(
            side="left"
        )
        ttk.Button(search_frame, text="Vider", command=self.on_clear_search).pack(
            side="left", padx=(6, 0)
        )

        # list
        list_frame = ttk.Frame(self, style="Content.TFrame")
        list_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 8))
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        columns = ("id", "brand", "model", "year", "plate", "price", "status")
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            style="Dark.Treeview",
        )
        headers = [
            ("id", "ID", 50),
            ("brand", "Marque", 100),
            ("model", "Modèle", 120),
            ("year", "Année", 70),
            ("plate", "Immatriculation", 120),
            ("price", "Prix/jour", 90),
            ("status", "Statut", 100),
        ]
        for col, text, width in headers:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # form
        form = ttk.LabelFrame(self, text="Détails voiture", padding=12)
        form.grid(row=2, column=1, sticky="nsew")
        for i in range(4):
            form.columnconfigure(i, weight=1)

        self.var_brand = tk.StringVar()
        self.var_model = tk.StringVar()
        self.var_year = tk.StringVar()
        self.var_plate = tk.StringVar()
        self.var_price = tk.StringVar()
        self.var_status = tk.StringVar(value="available")

        row = 0
        ttk.Label(form, text="Marque *").grid(row=row, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_brand).grid(
            row=row, column=1, sticky="ew", pady=2
        )
        ttk.Label(form, text="Modèle *").grid(row=row, column=2, sticky="w")
        ttk.Entry(form, textvariable=self.var_model).grid(
            row=row, column=3, sticky="ew", pady=2
        )

        row += 1
        ttk.Label(form, text="Année *").grid(row=row, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_year).grid(
            row=row, column=1, sticky="ew", pady=2
        )
        ttk.Label(form, text="Immatriculation *").grid(row=row, column=2, sticky="w")
        ttk.Entry(form, textvariable=self.var_plate).grid(
            row=row, column=3, sticky="ew", pady=2
        )

        row += 1
        ttk.Label(form, text="Prix par jour *").grid(row=row, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_price).grid(
            row=row, column=1, sticky="ew", pady=2
        )
        ttk.Label(form, text="Statut").grid(row=row, column=2, sticky="w")
        cb_status = ttk.Combobox(
            form,
            textvariable=self.var_status,
            values=["available", "rented", "maintenance"],
            state="readonly",
        )
        cb_status.grid(row=row, column=3, sticky="ew", pady=2)

        # buttons
        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=row + 1, column=0, columnspan=4, pady=(12, 0), sticky="ew")
        ttk.Button(btn_frame, text="Nouveau", command=self.on_new).pack(
            side="left", padx=(0, 4)
        )
        ttk.Button(btn_frame, text="Enregistrer", command=self.on_save).pack(
            side="left", padx=4
        )
        ttk.Button(btn_frame, text="Supprimer", command=self.on_delete).pack(
            side="left", padx=4
        )
        ttk.Button(btn_frame, text="Vider formulaire", command=self.clear_form).pack(
            side="left", padx=4
        )

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        cars = cars_service.list_cars(self.var_search.get() or None)
        for car in cars:
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
                    car["price_per_day"],
                    car["status"],
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
        _, brand, model, year, plate, price, status = values
        self.var_brand.set(brand)
        self.var_model.set(model)
        self.var_year.set(str(year))
        self.var_plate.set(plate)
        self.var_price.set(str(price))
        self.var_status.set(status)

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
            brand = validators.require(self.var_brand.get(), "Marque")
            model = validators.require(self.var_model.get(), "Modèle")
            year = validators.validate_int(self.var_year.get(), "Année")
            plate = validators.require(self.var_plate.get(), "Immatriculation")
            price = validators.validate_float(self.var_price.get(), "Prix par jour")
            if price <= 0:
                raise ValueError("Le prix par jour doit être supérieur à 0.")

            data = {
                "brand": brand,
                "model": model,
                "year": year,
                "plate": plate,
                "price_per_day": price,
                "status": self.var_status.get() or "available",
            }
            cars_service.save_car(self.selected_id, data)
            self.refresh()
            messagebox.showinfo("Succès", "Voiture enregistrée avec succès.")
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
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))

