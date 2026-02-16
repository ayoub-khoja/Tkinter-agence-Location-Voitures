import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

from db import setup_database
from ui.dashboard_view import DashboardView
from ui.cars_view import CarsView
from ui.customers_view import CustomersView
from ui.rentals_view import RentalsView


# Configure CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CarRentalApp:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("FASTAUTO - Location de Voiture")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
        
        # Yellow color palette for Tunisia theme
        self.colors = {
            "bg_primary": "#0F172A",      # Deep slate
            "bg_secondary": "#1E293B",    # Slate 800
            "bg_tertiary": "#334155",     # Slate 700
            "accent_primary": "#FCD34D",   # Yellow 300 - Primary yellow
            "accent_secondary": "#FDE047", # Yellow 200 - Light yellow
            "accent_gold": "#FBBF24",     # Amber 400 - Gold accent
            "yellow_dark": "#F59E0B",     # Amber 500 - Dark yellow
            "yellow_light": "#FEF3C7",   # Yellow 100 - Very light yellow
            "text_primary": "#F8FAFC",    # Slate 50
            "text_secondary": "#CBD5E1",  # Slate 300
            "text_muted": "#94A3B8",      # Slate 400
            "success": "#10B981",         # Green 500
            "warning": "#F59E0B",         # Amber 500
            "danger": "#EF4444",         # Red 500
        }

        setup_database()
        self._build_layout()

    def _build_layout(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Modern Sidebar
        self.sidebar = ctk.CTkFrame(
            self.root,
            width=280,
            corner_radius=0,
            fg_color=self.colors["bg_secondary"]
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo/Brand Section
        logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
            height=120
        )
        logo_frame.pack(fill="x", padx=20, pady=(30, 20))
        
        # Try to load logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo.png")
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
        
        # Brand name with Tunisia flag colors
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

        # Navigation Buttons
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

        # Footer
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

        # Content Area
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

        # Default view
        self.show_view("dashboard", DashboardView)

    def show_view(self, key, view_class):
        # Update button states
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(
                    fg_color=self.colors["accent_primary"],
                    text_color="#000000",  # Black text on yellow
                    hover_color=self.colors["yellow_dark"]
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=self.colors["text_secondary"],
                    hover_color=self.colors["bg_tertiary"]
                )

        # Hide current view
        if self.current_view is not None:
            self.current_view.grid_forget()

        # Show or create view
        if key not in self.views:
            frame = view_class(self.content, self.colors)
            self.views[key] = frame
        self.current_view = self.views[key]
        self.current_view_key = key
        self.current_view.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Refresh view if method exists
        if hasattr(self.current_view, "refresh"):
            try:
                self.current_view.refresh()
            except Exception as exc:
                messagebox.showerror("Erreur", str(exc))
