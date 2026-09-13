import re

def mask_identifier(val: str, field_type: str = "general") -> str:
    """Masks sensitive document identifiers according to regulatory standards."""
    if not val:
        return ""
    val_clean = str(val).strip()
    
    # Check if 12-digit Aadhaar number
    aadhaar_match = re.search(r'\b(\d{4})[\s-]?(\d{4})[\s-]?(\d{4})\b', val_clean)
    if aadhaar_match:
        return f"XXXX-XXXX-{aadhaar_match.group(3)}"
        
    # Check if 10-character PAN number (e.g. ABCDE1234F)
    pan_match = re.search(r'\b([A-Z]{5})(\d{4})([A-Z])\b', val_clean, re.IGNORECASE)
    if pan_match:
        return f"{pan_match.group(1)[:2]}***{pan_match.group(2)[-2:]}{pan_match.group(3)}"

    # Check if Passport number (usually 1 letter followed by 7 digits)
    passport_match = re.search(r'\b([A-Z])(\d{7})\b', val_clean, re.IGNORECASE)
    if passport_match:
        return f"{passport_match.group(1)}*****{passport_match.group(2)[-2:]}"

    # General number/string masking
    if len(val_clean) > 8:
        return f"{val_clean[:2]}{'*' * (len(val_clean) - 6)}{val_clean[-4:]}"
    elif len(val_clean) > 4:
        return f"{'*' * (len(val_clean) - 2)}{val_clean[-2:]}"
    return val_clean

def mask_dict(data: dict) -> dict:
    """Recursively masks dictionary fields that contain sensitive identifiers."""
    masked = {}
    sensitive_keys = {'uid', 'aadhaar', 'pan', 'passport', 'id_number', 'document_id', 'licence_number', 'ssn', 'tax_id'}
    
    for k, v in data.items():
        k_lower = k.lower()
        if any(s in k_lower for s in sensitive_keys) and isinstance(v, str):
            masked[k] = mask_identifier(v, k_lower)
        elif isinstance(v, dict):
            masked[k] = mask_dict(v)
        else:
            masked[k] = v
    return masked
