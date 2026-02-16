import customtkinter as ctk
from tkinter import ttk, messagebox

from repositories import customers_repo
from utils import validators


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

        # Header
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
            text="📋 Liste des Clients",
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

        self.var_first_name = ctk.StringVar()
        self.var_last_name = ctk.StringVar()
        self.var_cin = ctk.StringVar()
        self.var_phone = ctk.StringVar()
        self.var_email = ctk.StringVar()

        # First Name
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

        # Last Name
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

        # CIN and Phone in row
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

        # Email
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

