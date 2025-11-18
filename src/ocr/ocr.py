import io
import fitz  # PyMuPDF
from PIL import Image
import pytesseract


def pdf_first_page_to_pil(pdf_bytes, zoom=2.0):
    """Convert first page of PDF to PIL.Image (if PDF) - from notebook."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(0)
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    return img


def ocr_file(file_bytes: bytes, filename: str) -> str:
    """
    OCR helper (returns text) - extracted from notebook.
    
    Args:
        file_bytes: The file content as bytes
        filename: The filename (used to determine file type)
    
    Returns:
        Extracted text as a string
    """
    # detect pdf by extension
    if filename.lower().endswith(".pdf"):
        img = pdf_first_page_to_pil(file_bytes)
    else:
        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    # optional simple preprocessing could be added here
    text = pytesseract.image_to_string(img, lang='eng')
    return text

