"""
Text Extraction Module
Extracts text from PDF and text files for resume and job descriptions.
"""

import os
from typing import Optional

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    try:
        import fitz  # PyMuPDF
        PYMUPDF_AVAILABLE = True
    except ImportError:
        PYMUPDF_AVAILABLE = False


def extract_text(file_path: str) -> str:
    """
    Extract text from PDF or text file.
    
    Args:
        file_path: Path to the file (PDF or .txt)
        
    Returns:
        Extracted raw text as string
        
    Raises:
        ValueError: If file format is not supported or libraries are missing
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Handle text files
    if file_ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Handle PDF files
    elif file_ext == '.pdf':
        if PDFPLUMBER_AVAILABLE:
            return _extract_pdf_pdfplumber(file_path)
        elif PYMUPDF_AVAILABLE:
            return _extract_pdf_pymupdf(file_path)
        else:
            raise ImportError(
                "No PDF library available. Install pdfplumber or PyMuPDF: "
                "pip install pdfplumber OR pip install pymupdf"
            )
    else:
        raise ValueError(f"Unsupported file format: {file_ext}. Supported: .pdf, .txt")


def _extract_pdf_pdfplumber(file_path: str) -> str:
    """Extract text from PDF using pdfplumber."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def _extract_pdf_pymupdf(file_path: str) -> str:
    """Extract text from PDF using PyMuPDF."""
    text = ""
    doc = fitz.open(file_path)
    for page in doc:
        text += page.get_text() + "\n"
    doc.close()
    return text.strip()

