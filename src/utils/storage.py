import uuid
from pathlib import Path
from typing import Dict


FORMS_DB_DIR = Path("data/forms_db")


def save_form(file_bytes: bytes, filename: str, ocr_text: str) -> str:
    """
    Save uploaded form file and OCR text to forms_db.
    
    Args:
        file_bytes: Original file content
        filename: Original filename
        ocr_text: Extracted OCR text
    
    Returns:
        form_id: Unique identifier for the saved form
    """
    # Generate unique form ID
    form_id = str(uuid.uuid4())
    
    # Create form directory
    form_dir = FORMS_DB_DIR / form_id
    form_dir.mkdir(parents=True, exist_ok=True)
    
    # Save original file
    file_path = form_dir / filename
    with open(file_path, 'wb') as f:
        f.write(file_bytes)
    
    # Save OCR text
    ocr_path = form_dir / "ocr_text.txt"
    with open(ocr_path, 'w', encoding='utf-8') as f:
        f.write(ocr_text)
    
    return form_id


def get_form_filename(form_id: str) -> str:
    """
    Get the original filename for a form_id.
    
    Args:
        form_id: The form ID
    
    Returns:
        Original filename or form_id if not found
    """
    form_dir = FORMS_DB_DIR / form_id
    if not form_dir.exists() or not form_dir.is_dir():
        return form_id
    
    # Find the original file (exclude ocr_text.txt)
    for file_path in form_dir.iterdir():
        if file_path.is_file() and file_path.name != "ocr_text.txt":
            return file_path.name
    
    return form_id


def load_all_forms_with_names() -> Dict[str, Dict[str, str]]:
    """
    Load all forms with their filenames.
    
    Returns:
        Dictionary mapping form_id to {'filename': str, 'ocr_text': str}
    """
    forms_dict = {}
    
    if not FORMS_DB_DIR.exists():
        return forms_dict
    
    # Iterate through all form directories
    for form_dir in FORMS_DB_DIR.iterdir():
        if form_dir.is_dir():
            form_id = form_dir.name
            ocr_path = form_dir / "ocr_text.txt"
            
            if ocr_path.exists():
                # Get filename
                filename = get_form_filename(form_id)
                
                # Read OCR text
                with open(ocr_path, 'r', encoding='utf-8') as f:
                    ocr_text = f.read()
                
                forms_dict[form_id] = {
                    'filename': filename,
                    'ocr_text': ocr_text
                }
    
    return forms_dict

