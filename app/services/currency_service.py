"""
Currency Service Boundary

Design Decision:
All transactions in PocketLedger are stored in the base currency (INR).
Multi-currency support is implemented as presentation-layer "display conversion"
so database queries remain fast, clean, and uncoupled from dynamic rates.
"""

from decimal import Decimal

SUPPORTED_CURRENCIES: dict[str, str] = {
    "INR": "₹",
    "USD": "$",
    "EUR": "€",
    "GBP": "£"
}

# Fixed conversion rates from base currency INR
CONVERSION_RATES_FROM_INR: dict[str, Decimal] = {
    "INR": Decimal("1.0"),
    "USD": Decimal("0.012"),
    "EUR": Decimal("0.011"),
    "GBP": Decimal("0.0095")
}

def is_supported_currency(currency_code: str) -> bool:
    """Validate if currency code is supported."""
    return currency_code.upper() in SUPPORTED_CURRENCIES

def get_currency_symbol(currency_code: str) -> str:
    """Get display formatting symbol for currency code."""
    return SUPPORTED_CURRENCIES.get(currency_code.upper(), "₹")

def convert_currency(amount_inr: Decimal, target_currency: str) -> Decimal:
    """
    Convert base INR Decimal amount to target currency for display.
    """
    code = target_currency.upper()
    rate = CONVERSION_RATES_FROM_INR.get(code, Decimal("1.0"))
    return round(amount_inr * rate, 2)
