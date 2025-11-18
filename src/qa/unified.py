import json
import re
from ..llm.gemini import call_gemini, UNIFIED_SYSTEM


def _label_and_truncate_forms(forms_dict, per_file_char_limit=3000):
    """
    Build labeled block for prompt. Truncate each OCR text for token safety.
    """
    parts = []
    for fname, txt in forms_dict.items():
        snippet = txt.replace("\r\n", "\n")[:per_file_char_limit]
        parts.append(f"--- FILE: {fname} ---\n{snippet}\n")
    return "\n".join(parts)


def unified_form_query(forms_dict, question, model="gemini-flash-lite-latest",
                     per_file_char_limit=3000, max_output_tokens=1024):
    """
    Unified query: ask question over one or many forms.
    - forms_dict: {filename: ocr_text}
    - question: user question string
    Returns parsed JSON (python object) or raw string if parsing failed.
    """
    # 1) Build labeled files block (truncated)
    labeled_block = _label_and_truncate_forms(forms_dict, per_file_char_limit=per_file_char_limit)

    # 2) Build user prompt
    user_prompt = f"""FILES:
    {labeled_block}
    ---QUESTION---
    {question}

    IMPORTANT: Output JSON ONLY.
    Wrap the output JSON inside the markers:

    <JSON>
    { ... }
    </JSON>

    Do NOT include any text outside these markers.
    """

    # 3) Call Gemini (uses your call_gemini wrapper)
    raw_out = call_gemini(UNIFIED_SYSTEM, user_prompt, model=model, max_output_tokens=max_output_tokens)

    # 4) Try to parse JSON safely with multiple extraction strategies
    # Strategy 1: Try direct parsing
    try:
        parsed = json.loads(raw_out.strip())
        return {"success": True, "result": parsed, "raw": raw_out}
    except Exception:
        pass
    
    # Strategy 2: Extract from <JSON>...</JSON> tags
    try:
        json_match = re.search(r'<JSON>\s*(.*?)\s*</JSON>', raw_out, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
            parsed = json.loads(json_str)
            return {"success": True, "result": parsed, "raw": raw_out}
    except Exception:
        pass
    
    # Strategy 3: Extract from ```json ... ``` code blocks
    try:
        json_match = re.search(r'```json\s*(.*?)\s*```', raw_out, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
            parsed = json.loads(json_str)
            return {"success": True, "result": parsed, "raw": raw_out}
    except Exception:
        pass
    
    # Strategy 4: Extract from ``` ... ``` code blocks (without json label)
    try:
        json_match = re.search(r'```\s*(.*?)\s*```', raw_out, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
            # Remove "json" if it's the first line
            if json_str.startswith('json'):
                json_str = json_str[4:].strip()
            parsed = json.loads(json_str)
            return {"success": True, "result": parsed, "raw": raw_out}
    except Exception:
        pass
    
    # Strategy 5: Find first { or [ and try to extract complete JSON
    try:
        # Find first { or [
        start_char = None
        start_idx = None
        for i, char in enumerate(raw_out):
            if char in ['{', '[']:
                start_char = char
                start_idx = i
                break
        
        if start_idx is not None:
            # Find matching closing bracket
            depth = 0
            end_idx = None
            for i in range(start_idx, len(raw_out)):
                if raw_out[i] == start_char:
                    depth += 1
                elif raw_out[i] == ('}' if start_char == '{' else ']'):
                    depth -= 1
                    if depth == 0:
                        end_idx = i + 1
                        break
            
            if end_idx:
                json_str = raw_out[start_idx:end_idx]
                parsed = json.loads(json_str)
                return {"success": True, "result": parsed, "raw": raw_out}
    except Exception:
        pass
    
    # Strategy 6: Try to find JSON object/array with regex
    try:
        # Match JSON object
        json_obj_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw_out, re.DOTALL)
        if json_obj_match:
            json_str = json_obj_match.group(0)
            parsed = json.loads(json_str)
            return {"success": True, "result": parsed, "raw": raw_out}
        
        # Match JSON array
        json_arr_match = re.search(r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]', raw_out, re.DOTALL)
        if json_arr_match:
            json_str = json_arr_match.group(0)
            parsed = json.loads(json_str)
            return {"success": True, "result": parsed, "raw": raw_out}
    except Exception:
        pass
    
    # All strategies failed: return error with raw output
    return {"success": False, "error": "Could not parse LLM output as JSON", "raw": raw_out}

