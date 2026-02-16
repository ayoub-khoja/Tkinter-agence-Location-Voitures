import customtkinter as ctk

from ui.app import CarRentalApp


def main():
    root = ctk.CTk()
    app = CarRentalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

