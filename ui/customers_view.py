import tkinter as tk
from tkinter import ttk, messagebox

from repositories import customers_repo
from utils import validators


class CustomersView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=16)
        self.configure(style="Content.TFrame")
        self.selected_id = None
        self._build()
        self.refresh()

    def _build(self):
        header = ttk.Label(self, text="Clients", style="Title.TLabel")
        header.grid(row=0, column=0, sticky="w")

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)

        search_frame = ttk.Frame(self, style="Content.TFrame")
        search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 8))
        ttk.Label(search_frame, text="Recherche (nom / CIN / téléphone):").pack(
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

        list_frame = ttk.Frame(self, style="Content.TFrame")
        list_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 8))
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        columns = ("id", "first_name", "last_name", "cin", "phone", "email")
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            style="Dark.Treeview",
        )
        for col, text, width in [
            ("id", "ID", 50),
            ("first_name", "Prénom", 100),
            ("last_name", "Nom", 100),
            ("cin", "CIN", 100),
            ("phone", "Téléphone", 120),
            ("email", "Email", 160),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        form = ttk.LabelFrame(self, text="Détails client", padding=12)
        form.grid(row=2, column=1, sticky="nsew")
        for i in range(4):
            form.columnconfigure(i, weight=1)

        self.var_first_name = tk.StringVar()
        self.var_last_name = tk.StringVar()
        self.var_cin = tk.StringVar()
        self.var_phone = tk.StringVar()
        self.var_email = tk.StringVar()

        row = 0
        ttk.Label(form, text="Prénom *").grid(row=row, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_first_name).grid(
            row=row, column=1, sticky="ew", pady=2
        )
        ttk.Label(form, text="Nom *").grid(row=row, column=2, sticky="w")
        ttk.Entry(form, textvariable=self.var_last_name).grid(
            row=row, column=3, sticky="ew", pady=2
        )

        row += 1
        ttk.Label(form, text="CIN *").grid(row=row, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_cin).grid(
            row=row, column=1, sticky="ew", pady=2
        )
        ttk.Label(form, text="Téléphone *").grid(row=row, column=2, sticky="w")
        ttk.Entry(form, textvariable=self.var_phone).grid(
            row=row, column=3, sticky="ew", pady=2
        )

        row += 1
        ttk.Label(form, text="Email").grid(row=row, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_email).grid(
            row=row, column=1, columnspan=3, sticky="ew", pady=2
        )

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
        customers = customers_repo.list_customers(self.var_search.get() or None)
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
            first_name = validators.require(self.var_first_name.get(), "Prénom")
            last_name = validators.require(self.var_last_name.get(), "Nom")
            cin = validators.require(self.var_cin.get(), "CIN")
            phone = validators.require(self.var_phone.get(), "Téléphone")
            email = validators.optional(self.var_email.get())

            data = {
                "first_name": first_name,
                "last_name": last_name,
                "cin": cin,
                "phone": phone,
                "email": email,
            }
            if self.selected_id:
                customers_repo.update_customer(self.selected_id, data)
            else:
                self.selected_id = customers_repo.create_customer(data)
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
            customers_repo.delete_customer(self.selected_id)
            self.clear_form()
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))

