# Importation des bibliothèques nécessaires
import customtkinter as ctk

from ui.app import CarRentalApp


def main():
    """
    Fonction principale - t7awel l'application
    Crée la fenêtre principale et lance l'application de location de voitures
    """
    # Créer la fenêtre principale (root window)
    root = ctk.CTk()
    # Créer l'application de location de voitures
    app = CarRentalApp(root)
    # Lancer la boucle principale de l'interface graphique
    root.mainloop()


if __name__ == "__main__":
    # Lancer l'application quand le script est exécuté directement
    main()

