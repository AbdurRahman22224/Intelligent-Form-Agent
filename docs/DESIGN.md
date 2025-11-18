# Design Notes

## Architecture Overview

The Intelligent Form Agent follows a modular architecture:

1. **OCR Layer**: Extracts text from PDFs/images
2. **Storage Layer**: Persists forms and OCR text
3. **LLM Layer**: Interfaces with Gemini API
4. **QA Layer**: Orchestrates question answering
5. **UI Layer**: Streamlit interface (optional)

## Design Decisions

- **Local OCR**: Uses Tesseract (free, no API costs)
- **First page only**: PDFs are processed for first page to keep it simple
- **No vector DB**: Direct LLM calls, no embeddings/FAISS
- **Simple storage**: File-based storage in `data/forms_db/`
- **Minimal dependencies**: Only essential packages

## Future Enhancements (Not Implemented)

- Multi-page PDF support
- Vector database for semantic search
- Batch processing
- Form type detection
- Field extraction with structured output

