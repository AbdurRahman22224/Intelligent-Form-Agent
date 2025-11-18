"""Streamlit UI for Intelligent Form Agent - Creative Extension."""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ocr.ocr import ocr_file
from src.qa.unified import unified_form_query
from src.utils.storage import save_form, load_all_forms_with_names
from src.llm.gemini import call_gemini, SUMMARY_SYSTEM
import json


st.set_page_config(
    page_title="Intelligent Form Agent",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Intelligent Form Agent")
st.markdown("Upload forms and ask questions about them using AI-powered analysis.")


# Sidebar navigation
page = st.sidebar.selectbox("Navigate", ["Upload Forms", "Ask Questions"])


if page == "Upload Forms":
    st.header("Upload Forms")
    st.markdown("Upload up to 3 PDF or image files. Each will be processed with OCR and saved.")
    
    uploaded_files = st.file_uploader(
        "Choose files",
        type=['pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        # Limit to 3 files
        if len(uploaded_files) > 3:
            st.warning("Only the first 3 files will be processed.")
            uploaded_files = uploaded_files[:3]
        
        for idx, uploaded_file in enumerate(uploaded_files):
            st.subheader(f"File {idx + 1}: {uploaded_file.name}")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if st.button(f"Process {uploaded_file.name}", key=f"process_{idx}"):
                    try:
                        with st.spinner("Running OCR..."):
                            file_bytes = uploaded_file.read()
                            ocr_text = ocr_file(file_bytes, uploaded_file.name)
                            
                            # Save form
                            form_id = save_form(file_bytes, uploaded_file.name, ocr_text)
                            
                            st.success(f"✅ Form processed and saved! Form ID: {form_id}")
                            st.session_state[f'ocr_{idx}'] = ocr_text
                            st.session_state[f'form_id_{idx}'] = form_id
                    
                    except Exception as e:
                        st.error(f"Error processing file: {str(e)}")
            
            with col2:
                if f'ocr_{idx}' in st.session_state:
                    st.text_area(
                        f"Extracted Text ({uploaded_file.name})",
                        st.session_state[f'ocr_{idx}'],
                        height=200,
                        key=f"text_{idx}"
                    )


elif page == "Ask Questions":
    st.header("Ask Questions")
    # Load all forms with filenames
    forms_with_names = load_all_forms_with_names()
    
    if not forms_with_names:
        st.info("No forms found. Please upload forms first using the 'Upload Forms' page.")
    else:
        st.text(f"Found {len(forms_with_names)} saved form(s).")
        
        # Create a mapping for easier access
        form_id_to_filename = {form_id: info['filename'] for form_id, info in forms_with_names.items()}
        forms_dict = {form_id: info['ocr_text'] for form_id, info in forms_with_names.items()}
        
        # Display forms with filenames
        with st.expander("View Saved Forms"):
            for form_id, info in forms_with_names.items():
                filename = info['filename']
                ocr_text = info['ocr_text']
                st.text(f"📄 {filename}")
                st.text_area(
                    f"OCR Text Preview",
                    ocr_text[:500] + "..." if len(ocr_text) > 500 else ocr_text,
                    height=100,
                    key=f"preview_{form_id}",
                    disabled=True
                )
        
        # Form selection dropdown - show filenames
        form_list = list(forms_dict.keys())
        
        selected_forms = st.multiselect(
            "Select form(s) to query:",
            options=form_list,
            format_func=lambda x: f"{form_id_to_filename[x]}",
            default=form_list if len(form_list) > 0 else []
        )
        
        # Filter forms_dict based on selection
        if selected_forms:
            filtered_forms_dict = {form_id: forms_dict[form_id] for form_id in selected_forms}
        else:
            filtered_forms_dict = forms_dict  # If nothing selected, use all forms
        
        # Question input
        question = st.text_input("Enter your question:")
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            ask_button = st.button("Ask Question", disabled=not question or not filtered_forms_dict, use_container_width=True)
        with col2:
            summary_button = st.button("Generate Summary", disabled=not filtered_forms_dict, use_container_width=True)
        
        # Show JSON toggle
        show_json = st.checkbox("Show Raw JSON", value=False)
        
        if ask_button:
            with st.spinner("Analyzing forms..."):
                try:
                    # Use filtered_forms_dict based on user selection
                    result = unified_form_query(filtered_forms_dict, question)
                    
                    if result["success"]:
                        st.success("✅ Analysis complete!")
                        
                        # Display formatted result
                        if isinstance(result["result"], dict) and result["result"].get("mode") == "single":
                            # Single form answer
                            st.markdown("### 📝 Answer")
                            answer = result["result"].get("answer", "No answer provided")
                            if answer:
                                st.info(answer)
                            else:
                                st.warning("No answer could be determined from the form.")
                            
                            # Confidence badge
                            confidence = result["result"].get("confidence", "UNKNOWN")
                            if confidence == "HIGH":
                                st.success(f"Confidence: {confidence}")
                            elif confidence == "MEDIUM":
                                st.warning(f"Confidence: {confidence}")
                            else:
                                st.error(f"Confidence: {confidence}")
                            
                            # Evidence
                            if result["result"].get("evidence"):
                                st.markdown("### 📎 Evidence")
                                for ev in result["result"]["evidence"]:
                                    ev_file = ev.get('file', 'Unknown')
                                    ev_display = form_id_to_filename.get(ev_file, ev_file)
                                    st.write(f"**{ev_display}**: `{ev.get('snippet', '')}`")
                            
                            # Note if present
                            if result["result"].get("note"):
                                st.info(f"ℹ️ Note: {result['result']['note']}")
                                
                        elif isinstance(result["result"], list):
                            # Multi-form answer
                            st.markdown(f"### 📊 Found {len(result['result'])} matching form(s)")
                            for item in result["result"]:
                                file_id = item.get('file', '')
                                display_name = form_id_to_filename.get(file_id, file_id)
                                
                                with st.expander(f"📄 {display_name}", expanded=True):
                                    # Extracted fields
                                    extracted = item.get("extracted", {})
                                    if extracted:
                                        st.markdown("**Extracted Information:**")
                                        for key, value in extracted.items():
                                            if value is not None:
                                                st.write(f"- **{key.replace('_', ' ').title()}**: {value}")
                                    
                                    # Confidence
                                    confidence = item.get('confidence', 'UNKNOWN')
                                    if confidence == "HIGH":
                                        st.success(f"Confidence: {confidence}")
                                    elif confidence == "MEDIUM":
                                        st.warning(f"Confidence: {confidence}")
                                    else:
                                        st.error(f"Confidence: {confidence}")
                                    
                                    # Evidence
                                    if item.get("evidence"):
                                        st.markdown("**Evidence:**")
                                        for ev in item["evidence"]:
                                            st.write(f"- `{ev.get('snippet', '')}`")
                        
                        # Show raw JSON if toggle is on
                        if show_json:
                            st.markdown("---")
                            st.markdown("### Raw JSON Response")
                            st.json(result["result"])
                    else:
                        st.error(f"Error: {result.get('error', 'Unknown error')}")
                        st.text_area("Raw output:", result.get("raw", ""), height=200)
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
        
        if summary_button:
            with st.spinner("Generating summary..."):
                try:
                    # Build summary prompt
                    if len(filtered_forms_dict) == 1:
                        # Single form summary
                        form_id = list(filtered_forms_dict.keys())[0]
                        ocr_text = list(filtered_forms_dict.values())[0]
                        filename = form_id_to_filename.get(form_id, form_id)
                        user_prompt = f"""Form: {filename}

                                        OCR Text:
                                        {ocr_text}

                                        Generate a comprehensive summary of this form."""
                    else:
                        # Multi-form summary
                        labeled_forms = []
                        for form_id, ocr_text in filtered_forms_dict.items():
                            filename = form_id_to_filename.get(form_id, form_id)
                            # Use full OCR text for better summaries (no truncation)
                            labeled_forms.append(f"--- Form: {filename} ---\n{ocr_text}\n")
                        
                        user_prompt = f"""Multiple Forms:

                                        {''.join(labeled_forms)}

                                        Generate a comprehensive summary for each form."""
                    
                    # Call Gemini with summary system prompt
                    raw_summary = call_gemini(SUMMARY_SYSTEM, user_prompt)
                    
                    # Try to parse JSON
                    try:
                        summary_data = json.loads(raw_summary)
                    except:
                        # Try to extract JSON from markdown or tags
                        import re
                        json_match = re.search(r'\{.*\}', raw_summary, re.DOTALL)
                        if json_match:
                            try:
                                summary_data = json.loads(json_match.group(0))
                            except:
                                summary_data = {"summary": raw_summary, "raw": True}
                        else:
                            summary_data = {"summary": raw_summary, "raw": True}
                    
                    # Display summary
                    st.success("✅ Summary generated!")
                    
                    if summary_data.get("raw"):
                        # If not JSON, show as plain text
                        st.markdown("### 📄 Summary")
                        st.info(summary_data.get("summary", raw_summary))
                    else:
                        # Display structured summary
                        st.markdown("### 📄 Summary")
                        summary_text = summary_data.get("summary", "No summary generated")
                        st.info(summary_text)
                        
                        # Key fields
                        key_fields = summary_data.get("key_fields", {})
                        if key_fields:
                            st.markdown("### 🔑 Key Fields")
                            for key, value in key_fields.items():
                                if value is not None:
                                    st.write(f"- **{key.replace('_', ' ').title()}**: {value}")
                        
                        # Warnings
                        warnings = summary_data.get("warnings", [])
                        if warnings:
                            st.markdown("### ⚠️ Warnings")
                            for warning in warnings:
                                st.warning(warning)
                        
                        # Form type
                        form_type = summary_data.get("form_type")
                        if form_type:
                            st.markdown(f"**Form Type:** {form_type}")
                    
                    # Show raw JSON if toggle is on
                    if show_json:
                        st.markdown("---")
                        st.markdown("### Raw JSON Response")
                        st.json(summary_data)
                
                except Exception as e:
                    st.error(f"Error generating summary: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())

