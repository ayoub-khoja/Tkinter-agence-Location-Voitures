# Importation de customtkinter pour l'interface graphique
import customtkinter as ctk
# Importation de la classe principale de l'application
from ui.app import CarRentalApp


def main():
    """Point d'entrée de l'application"""
    # Créer la fenêtre principale de l'application
    root = ctk.CTk()
    # Créer l'instance de l'application avec la fenêtre principale
    app = CarRentalApp(root)
    # Lancer la boucle principale pour afficher l'interface
    root.mainloop()


# Si le fichier est exécuté directement (pas importé)
if __name__ == "__main__":
    # Appeler la fonction principale
    main()

