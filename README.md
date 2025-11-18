# Intelligent Form Agent

An AI-powered system that processes and understands a wide variety of forms, automatically extracts information from structured and unstructured fields, and provides intelligent answers to questions about individual or multiple forms.

--

Video Demo: [Drive Link](https://drive.google.com/file/d/1ROvQi84aFawzthiMV1nm4AgvXkIxQY40/view?usp=sharing)

--
## 🎯 Purpose

The Intelligent Form Agent can:
- **Process forms**: Extract text from PDFs and images using OCR
- **Answer questions**: Provide direct answers about individual forms
- **Holistic analysis**: Analyze multiple forms together to provide comprehensive insights
- **Generate summaries**: Create concise summaries highlighting important details
- **Interactive UI**: Streamlit-based interface for easy interaction (creative extension)

## 📦 Project Structure

```
project_root/
│
├── src/             # Main agent code
│   ├── llm/         # OCR module (PyMuPDF + Tesseract)
│   ├── ocr/         # Question answering module
│   ├── qa/          # Gemini LLM integration
│   └── utils/       # Storage utilities
│
├── data/            # Sample forms or test files
│   └── forms_db/    # Saved forms database
│
├── notebooks/       # Colab or dev experiments
├── docs/            # Documentation files 
│   └── DESIGN.md
│ 
├── app.py           # Streamlit UI 
├── test_gemini.py   # Gemini API smoke test
├── setup_check.py   # Environment & structure verifier
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

All installation, configuration, and execution steps (Streamlit UI, environment checks, and Gemini smoke tests) are documented in **[QUICKSTART.md](QUICKSTART.md)**. Follow that guide to:

- Install prerequisites (Python, Tesseract, pip dependencies).
- Configure your `GOOGLE_API_KEY` via `.env`.
- Launch the Streamlit app.
- Run `setup_check.py` and `test_gemini.py` for quick validation.

## 🎨 Creative Extensions

### Streamlit UI

The project includes a fully functional Streamlit web interface that enhances usability:

- **Upload Page**: Drag-and-drop file upload with real-time OCR preview
- **Question Page**: Unified query interface that automatically handles:
  - Single form questions
  - Multi-form holistic analysis
  - Form summarization
  - Field extraction across forms

**To run the UI**:
```bash
streamlit run app.py
```

**Key Features:**
- Uses `unified_form_query()` - no need to choose query type
- Displays structured JSON responses with evidence
- Shows confidence scores and provenance snippets
- Handles both single-object and array responses
- Automatic error handling and retry logic

The UI automatically handles:
- File processing and OCR
- Form storage and retrieval
- Unified query processing (single/multi/summary)
- JSON-formatted responses with evidence

## 🔧 Technical Details

### Architecture Overview

```
┌─────────────┐
│  User Query │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ unified_form_   │ ◄─── Handles single/multi/summary automatically
│ query()         │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  UNIFIED_SYSTEM │ ◄─── Generic prompt for all scenarios
│  Prompt         │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  call_gemini()  │ ◄─── Robust wrapper with retries & fallbacks
│  (Robust)       │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Gemini API     │
└─────────────────┘
```

## 📋 Requirements

All dependencies are listed in `requirements.txt`:
- `streamlit`: Web UI framework
- `pytesseract`: Tesseract OCR Python wrapper
- `pillow`: Image processing
- `pymupdf`: PDF processing
- `google-generativeai`: Gemini API client
- `python-dotenv`: Environment variable management

## 🔐 Environment Variables

Create a `.env` file with:
```
GOOGLE_API_KEY=your_api_key_here
```

## 📚 Notes

- The system uses local OCR (Tesseract) - no paid OCR services required
- Gemini API requires internet connection
- Forms are stored locally in `data/forms_db/`
- The UI is an optional creative extension - core functionality works without it

## 🐛 Troubleshooting

**Tesseract not found**:
- Ensure Tesseract is installed and in your PATH
- On Windows, you may need to specify the path in code

**Gemini API errors**:
- Verify your API key is correct in `.env`
- Check your internet connection
- Ensure you have API quota remaining

**Import errors**:
- Make sure you're running from the project root
- Verify all dependencies are installed: `pip install -r requirements.txt`

## 📄 License

This project is created for educational/assignment purposes.

---

**Built with**: Python, Streamlit, Tesseract OCR, Google Gemini AI

