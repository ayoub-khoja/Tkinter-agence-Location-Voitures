def format_money(value: float) -> str:
    return f"{value:,.2f} MAD".replace(",", " ").replace(".", ",")


def format_date(date_str: str) -> str:
    # already YYYY-MM-DD, keep simple for now
    return date_str or ""

