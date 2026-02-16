# Fonctions de validation pour les champs de formulaire
from datetime import datetime
from typing import Optional


def require(value: str, field_name: str) -> str:
    """
    Vérifier que le champ est obligatoire et pas vide
    Lever exception si vide ou None
    """
    if value is None or str(value).strip() == "":
        raise ValueError(f"Le champ '{field_name}' est obligatoire.")
    return value.strip()


def validate_int(value: str, field_name: str) -> int:
    """
    Valider que la valeur est un nombre entier
    Retourne l'entier ou lève exception si invalide
    """
    require(value, field_name)  # Vérifier d'abord que c'est pas vide
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Le champ '{field_name}' doit être un entier.")


def validate_float(value: str, field_name: str) -> float:
    """
    Valider que la valeur est un nombre décimal
    Retourne le float ou lève exception si invalide
    """
    require(value, field_name)
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Le champ '{field_name}' doit être un nombre.")


def validate_date(value: str, field_name: str, fmt: str = "%Y-%m-%d") -> str:
    """
    Valider que la valeur est une date valide au format YYYY-MM-DD
    Retourne la date ou lève exception si invalide
    """
    value = require(value, field_name)
    try:
        datetime.strptime(value, fmt)
    except ValueError:
        raise ValueError(
            f"Le champ '{field_name}' doit être une date valide au format YYYY-MM-DD."
        )
    return value


def optional(value: Optional[str]) -> Optional[str]:
    """
    Traiter une valeur optionnelle (peut être vide)
    Retourne None si vide, sinon la valeur nettoyée
    """
    if value is None:
        return None
    value = str(value).strip()
    return value or None

