import re
import base64

def sanitize_base64(broken_b64):
    # Remove characters that are not part of the Base64 index table (including whitespace).
    sanitized_b64 = re.sub(r'[^A-Za-z0-9+/]', '', broken_b64)
    
    # Calculate the required padding. Base64 strings should be divisible by 4.
    padding_needed = len(sanitized_b64) % 4
    if padding_needed:  # If not 0, add the necessary '=' padding.
        sanitized_b64 += '=' * (4 - padding_needed)
    
    return sanitized_b64

def get_file_type_from_base64(base64_data):

    decoded_bytes = base64.b64decode(base64_data)
    
    # Define magic numbers for various file types
    file_signatures = {
        b'%PDF-': 'PDF',
        b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1': 'DOC',
        b'PK\x03\x04': 'DOCX',
    }
    
    for signature, file_type in file_signatures.items():
        if decoded_bytes.startswith(signature):
            return file_type

    return 'Unknown'