"""Test script for Gemini API call with sample OCR text and question."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.llm.gemini import call_gemini, UNIFIED_SYSTEM
import json


def test_gemini_with_sample_data():
    """Test Gemini API call with sample OCR text and question."""
    
    # Sample OCR text (simulating a form)
    sample_ocr_text = """
    JOB APPLICATION FORM
    
    Full Name: Alex Johnson
    Date of Birth: 14-Mar-1996
    Address: 22 Park Street, Bangalore
    Phone: +91-9876541111
    Email: alex.johnson@example.com
    
    Educational Qualification:
    Bachelor of Engineering in Computer Science (2018)
    CGPA: 8.6/10
    
    Work Experience:
    - Software Intern at TechNova Solutions (6 months)
    - Worked on React.js, APIs, and basic backend tasks.
    
    Skills:
    Python, JavaScript, React, SQL, Git
    
    Why Are You Applying for This Position?
    I want to work in a fast-growing tech company and enhance my software development skills.
    
    Signature: Alex Johnson
    """
    
    # Sample question
    question = "What is the applicant's name and what skills do they have?"
    
    print("Testing Gemini API call...")
    
    try:
        # Build user prompt (matching unified_form_query format)
        user_prompt = f"""FILES:
--- FILE: sample_form.pdf ---
{sample_ocr_text}
---QUESTION---
{question}

Return JSON according to the schema in system prompt. Return JSON only."""
        
        # Call Gemini
        raw_response = call_gemini(UNIFIED_SYSTEM, user_prompt)
        
        # Try to parse JSON to verify it works
        try:
            parsed = json.loads(raw_response)
            # If parsing succeeds, API is working
            print("✅ call_gemini is working!")
        except json.JSONDecodeError:
            # Try to extract JSON
            import re
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                try:
                    json.loads(json_match.group(0))
                    print("✅ call_gemini is working!")
                except:
                    print("call_gemini returned invalid response")
            else:
                print("all_gemini returned invalid response")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    test_gemini_with_sample_data()

