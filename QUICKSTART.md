# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Important**: Also install Tesseract OCR:
- **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

### Step 2: Configure API Key

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_api_key_here
```

Get your API key from: https://makersuite.google.com/app/apikey

### Step 3: Run the Application

**Option A: Streamlit UI (Recommended)**
```bash
streamlit run app.py
```

**Option B: Verify Setup**
```bash
python setup_check.py
```

**Option C: Test Gemini API**
```bash
python test_gemini.py
```
This will test the Gemini API with sample OCR text and a question.

## 📋 Usage Examples

### Using the Streamlit UI

1. Open http://localhost:8501 in your browser
2. Go to "Upload Forms" page
3. Upload a PDF or image (up to 3 files)
4. Click "Process" for each file
5. Go to "Ask Questions" page
6. Enter your question and click "Ask Question"
   - The system automatically handles single-form, multi-form, and summary queries
   - Results are displayed with evidence and confidence scores

### Using Python Code

```python
from src.ocr.ocr import ocr_file
from src.qa.unified import unified_form_query

# Read and process a form
with open('form.pdf', 'rb') as f:
    file_bytes = f.read()
    ocr_text = ocr_file(file_bytes, 'form.pdf')

# Ask a question using unified query
forms_dict = {"form.pdf": ocr_text}
result = unified_form_query(forms_dict, "What is the total amount?")
if result["success"]:
    print(result["result"])
```

## 🐛 Troubleshooting

**"Tesseract not found"**
- Install Tesseract and ensure it's in your PATH
- On Windows, you may need to restart your terminal

**"GOOGLE_API_KEY not found"**
- Create `.env` file with your API key
- Make sure `python-dotenv` is installed

**Import errors**
- Make sure you're in the project root directory
- Run `pip install -r requirements.txt` again

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [docs/DESIGN.md](docs/DESIGN.md) for architecture details

