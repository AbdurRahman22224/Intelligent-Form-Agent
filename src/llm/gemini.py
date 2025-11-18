import os
import textwrap
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# System prompt from Colab notebook - unified system for all query types
UNIFIED_SYSTEM = textwrap.dedent("""
You are a document-understanding assistant for an assignment.
You will be given multiple labeled OCR texts from uploaded forms and a user QUESTION.
Your job:
  1) Determine whether the QUESTION targets a single form (e.g., "What is Alex's name in file X?")
     or is a multi-form/horizontal question (e.g., "Which forms request > 500000?").
  2) Use ONLY the provided OCR texts. Do NOT invent information.
  3) Answer concisely. Always include provenance (file name + short snippet).
  4) Always return EXACT JSON (no extra text). See output schema below.
  5) If uncertain about numeric comparisons, set confidence to "LOW" and include raw snippet.
  6) If question is ambiguous, include a top-level "note" with a short clarifying suggestion.

OUTPUT SCHEMA (must follow exactly):
If the answer is naturally a single answer (single-form question), return an object:
{
  "mode": "single",
  "file": "<filename_or_null>",
  "answer": "<short answer or null>",
  "evidence": [ {"file":"<filename>","snippet":"<short text>"} ],
  "confidence": "HIGH|MEDIUM|LOW"
}

If the answer is multi-form (list/aggregation), return an array of objects (one per matching file):
[
  {
    "file":"<filename>",
    "extracted": { "<field>": <value or null>, ... },
    "evidence":[ {"snippet":"<short text>"} ],
    "confidence":"HIGH|MEDIUM|LOW"
  },
  ...
]

If you cannot answer anything, return an empty array [].
""").strip()

SUMMARY_SYSTEM = textwrap.dedent("""
You are a form summarization assistant. Your task is to generate concise, informative summaries of form documents.

Given OCR text from one or more forms, create a summary that includes:
- Form type/purpose
- Key information (names, dates, amounts, identifiers)
- Important details or notable items
- Any missing or incomplete information

Return EXACT JSON:
{
  "summary": "<concise summary text (2-4 sentences)>",
  "key_fields": {
    "<field_name>": "<value or null>",
    ...
  },
  "warnings": ["<list of missing or incomplete items>"],
  "form_type": "<type of form or null>"
}

Keep the summary clear and focused on the most important information.
""").strip()



def call_gemini(system_prompt, user_prompt, model="gemini-flash-lite-latest",
                max_output_tokens=1024, retries=1, truncate_to=3000):
    """
    Robust replacement for the Gemini call in Colab - extracted from notebook.
    - Returns a string: the model text on success, or a JSON-stringified error object on failure.
    - Keeps same simple call shape so you can drop it in place of your old function.
    """
    import json
    import time
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in .env file.")
    
    genai.configure(api_key=api_key)
    prompt_full = system_prompt + "\n\n" + user_prompt

    for attempt in range(retries + 1):
        try:
            model_instance = genai.GenerativeModel(model_name=model)
            # On retry, optionally send a truncated prompt to reduce safety/token issues
            send_prompt = prompt_full if attempt == 0 else prompt_full[:truncate_to]

            resp = model_instance.generate_content(
                send_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.0,
                    max_output_tokens=max_output_tokens
                )
            )

            # 1) Preferred fast accessor (may raise if no Part present)
            try:
                text = resp.text
                if text is not None:
                    return text
            except Exception:
                # fall through to safer inspection
                pass

            # 2) If no resp.text, check candidates array (older/newer client shapes)
            raw = getattr(resp, "_raw_response", None) or getattr(resp, "to_dict", lambda: None)()
            # If resp has candidates-like structure, try to extract first candidate text
            try:
                # safe traversal for common shapes
                candidates = raw.get("candidates") if isinstance(raw, dict) else None
                if candidates and len(candidates) > 0:
                    c0 = candidates[0]
                    # common nesting: c0['content'][0]['text']
                    if isinstance(c0, dict):
                        cont = c0.get("content")
                        if cont and isinstance(cont, list) and len(cont) > 0 and isinstance(cont[0], dict):
                            txt = cont[0].get("text")
                            if txt:
                                return txt
                        # some clients put plain text in c0.get('text')
                        if c0.get("text"):
                            return c0.get("text")
            except Exception:
                pass

            # 3) If prompt_feedback/safety exists -> return clear error JSON
            pf = getattr(resp, "prompt_feedback", None)
            if pf and getattr(pf, "safety_ratings", None):
                try:
                    ratings = pf.safety_ratings
                    safety_reason = ", ".join(f"{r.category.name}:{r.probability.name}" for r in ratings)
                except Exception:
                    safety_reason = str(pf)
                err = {"error": "blocked_by_safety", "safety_reason": safety_reason}
                print(f"[call_gemini] Warning: blocked by safety -> {safety_reason}")
                return json.dumps(err)

            # 4) Try to find any 'text' anywhere in raw response as last fallback
            def _find_text(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if k == "text" and isinstance(v, str):
                            return v
                        res = _find_text(v)
                        if res:
                            return res
                elif isinstance(obj, list):
                    for e in obj:
                        res = _find_text(e)
                        if res:
                            return res
                return None

            found = _find_text(raw) if raw is not None else None
            if found:
                return found

            # 5) Nothing usable found — either retry or return diagnostic
            if attempt < retries:
                time.sleep(1 + attempt * 2)
                continue

            # return diagnostic raw for debugging as JSON
            return json.dumps({"error": "no_content_generated", "raw_response_preview": str(raw)[:2000]})

        except Exception as exc:
            # network / API error -> retry if possible, else return error JSON
            if attempt < retries:
                time.sleep(1 + attempt * 2)
                continue
            return json.dumps({"error": "exception_calling_api", "details": str(exc)})

    # fallback (shouldn't be reached)
    return json.dumps({"error": "unknown_failure"})

