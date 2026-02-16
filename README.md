# 🚗 Gestion de Location de Voitures

Application de bureau pour la gestion d'une agence de location de voitures.

## Fonctionnalités

- **Gestion des voitures** : Ajouter, modifier, supprimer des véhicules
- **Gestion des clients** : Enregistrer et gérer les informations clients
- **Gestion des locations** : Créer et suivre les locations
- **Tableau de bord** : Vue d'ensemble des statistiques

## Prérequis

- Python 3.8+
- XAMPP (MySQL)


1. **Lancer l'application**
   ```bash
   python main.py
   ```

## Configuration Base de Données

Par défaut, l'application se connecte à MySQL avec :
- Host : `localhost`
- User : `root`
- Password : `` (vide)
- Database : `car_rental`

Pour modifier, éditez `db.py`.

## Structure du Projet

```
voiture/
├── main.py              # Point d'entrée
├── db.py                # Configuration MySQL
├── repositories/        # Accès aux données
├── services/            # Logique métier
├── ui/                  # Interface graphique
└── utils/               # Utilitaires
```
