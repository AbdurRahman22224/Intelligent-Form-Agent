"""Quick setup verification script."""

import sys
from pathlib import Path


def check_dependencies():
    """Check if all required packages are installed."""
    print("Checking dependencies...")
    
    required_packages = [
        'streamlit',
        'pytesseract',
        'PIL',  # pillow
        'fitz',  # pymupdf
        'google.generativeai',
        'dotenv'  # python-dotenv
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'PIL':
                __import__('PIL')
            elif package == 'fitz':
                __import__('fitz')
            elif package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)
    
    return missing


def check_tesseract():
    """Check if Tesseract is installed."""
    print("\nChecking Tesseract OCR...")
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"  ✓ Tesseract version: {version}")
        return True
    except Exception as e:
        print(f"  ✗ Tesseract not found: {e}")
        print("    Install from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False


def check_env_file():
    """Check if .env file exists."""
    print("\nChecking environment configuration...")
    env_file = Path(".env")
    if env_file.exists():
        print("  ✓ .env file found")
        
        # Check if API key is set
        from dotenv import load_dotenv
        import os
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key and api_key != "your_api_key_here":
            print("  ✓ GOOGLE_API_KEY is set")
            return True
        else:
            print("  ⚠ GOOGLE_API_KEY not set or using placeholder")
            return False
    else:
        print("  ✗ .env file not found")
        print("    Create .env file with: GOOGLE_API_KEY=your_key")
        return False


def check_structure():
    """Check if project structure is correct."""
    print("\nChecking project structure...")
    
    required_dirs = [
        'src/ocr',
        'src/qa',
        'src/llm',
        'src/utils',
        'data/forms_db',
        'docs'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✓ {dir_path}/")
        else:
            print(f"  ✗ {dir_path}/ - MISSING")
            all_exist = False
    
    required_files = [
        'app.py',
        'requirements.txt',
        'README.md'
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - MISSING")
            all_exist = False
    
    return all_exist


def main():
    """Run all checks."""
    print("=" * 60)
    print("Intelligent Form Agent - Setup Verification")
    print("=" * 60)
    print()
    
    missing_packages = check_dependencies()
    tesseract_ok = check_tesseract()
    env_ok = check_env_file()
    structure_ok = check_structure()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if missing_packages:
        print(f"\n⚠ Missing packages: {', '.join(missing_packages)}")
        print("  Install with: pip install -r requirements.txt")
    else:
        print("\n✓ All Python packages installed")
    
    if not tesseract_ok:
        print("\n⚠ Tesseract OCR not found - OCR will not work")
    
    if not env_ok:
        print("\n⚠ Environment not configured - API calls will fail")
    
    if not structure_ok:
        print("\n⚠ Project structure incomplete")
    
    if not missing_packages and tesseract_ok and env_ok and structure_ok:
        print("\n✅ All checks passed! Project is ready to use.")
        print("\nNext steps:")
        print("  1. Run: streamlit run app.py")
        print("  2. Test Gemini API: python test_gemini.py")
    else:
        print("\n⚠ Some issues found. Please fix them before running the project.")
    
    print()


if __name__ == "__main__":
    main()

