import tkinter as tk

from ui.app import CarRentalApp


def main():
    root = tk.Tk()
    app = CarRentalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

