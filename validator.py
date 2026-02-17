# validator.py
REQUIRED_COLUMNS = [
    "Reseller name",
    "Subscription name",
    "Status",
    "Expiration date",
    "EndCustomerName",
    "Quantity",
    "Client Contact"
]

def validate_excel(df):
    actual_columns = list(df.columns)
    missing = [col for col in REQUIRED_COLUMNS if col not in actual_columns]
    
    if missing:
        return False, f"Missing: {', '.join(missing)}"
    return True, "Valid"