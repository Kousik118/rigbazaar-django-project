from django import template
from decimal import Decimal, InvalidOperation # Use decimal for precision

register = template.Library()

@register.filter(name='mul')
def multiply(value, arg):
    """Multiplies two values. Handles potential type errors."""
    try:
        # Convert both to Decimal for accurate multiplication
        return Decimal(value) * Decimal(arg)
    except (TypeError, ValueError, InvalidOperation):
        # Handle cases where conversion fails (e.g., None, empty string)
        return 0 # Or None, or '', depending on desired fallback
    except Exception:
        # Catch any other unexpected errors
        return 0 # Fallback value

# Example: Add a currency formatting filter
@register.filter(name='currency')
def format_currency(value):
    """Formats a value as INR currency."""
    try:
        # Ensure value is Decimal for formatting
        val = Decimal(value)
        # Format as ₹ with 2 decimal places and commas
        return f"₹{val:,.2f}"
    except (TypeError, ValueError, InvalidOperation):
        return "₹0.00" # Fallback for invalid input
    except Exception:
        return "₹0.00" # Fallback for other errors