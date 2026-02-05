from datetime import datetime
from typing import Optional


def require(value: str, field_name: str) -> str:
    if value is None or str(value).strip() == "":
        raise ValueError(f"Le champ '{field_name}' est obligatoire.")
    return value.strip()


def validate_int(value: str, field_name: str) -> int:
    require(value, field_name)
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Le champ '{field_name}' doit être un entier.")


def validate_float(value: str, field_name: str) -> float:
    require(value, field_name)
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Le champ '{field_name}' doit être un nombre.")


def validate_date(value: str, field_name: str, fmt: str = "%Y-%m-%d") -> str:
    value = require(value, field_name)
    try:
        datetime.strptime(value, fmt)
    except ValueError:
        raise ValueError(
            f"Le champ '{field_name}' doit être une date valide au format YYYY-MM-DD."
        )
    return value


def optional(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = str(value).strip()
    return value or None

