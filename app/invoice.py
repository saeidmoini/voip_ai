# app/utils/invoice.py

import random

def generate_invoice_number(phone: str) -> str:
    """
    Generate a 4-digit invoice number based on the user's phone number.
    """
    # Extract digits only
    digits = ''.join(filter(str.isdigit, phone))

    # Use last 4 digits (pad with zeros if needed)
    last_four = digits[-4:] if len(digits) >= 4 else digits.zfill(4)

    # Convert to int and apply transformation
    num = int(last_four)

    # Multiply by a random prime and mod 10000 to keep it 4-digit
    prime_factor = random.choice([13, 17, 19, 23, 29])
    transformed = (num * prime_factor) % 10000

    return f"{transformed:04d}"