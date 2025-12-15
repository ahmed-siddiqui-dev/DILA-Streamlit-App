"""
RSM Document Intelligence Platform - Streamlit UI
Document Processing Pipeline: Upload, Integrity Check, Conversion, Extraction, Classification, and Labeling
"""

import streamlit as st
import requests
import json
import os
import re
import base64
import zipfile
import io
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

# Hardcoded Agent ID
AGENT_ID = "69174f5b808a5f1b07561164"

CORE_API_BASE_URL = "https://intellixcore-develop-64h7qzl6ga-ew.a.run.app"
CLASSIFICATION_API_BASE_URL = "https://intellixcore-develop-64h7qzl6ga-ew.a.run.app"
USER_EMAIL = "ahmed.siddiqui@intellixcore.com"
PASSWORD = "ZXCASD123!a"

st.set_page_config(
    page_title="RSM Document Intelligence Platform",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Header wrapper - Contains logo and blue bar */
    .header-wrapper {
        display: flex;
        align-items: center;
        gap: 0;
        margin-bottom: 1.5rem;
    }
    
    /* Logo - Standalone, outside blue bar */
    .header-logo {
        display: flex;
        align-items: center;
        flex-shrink: 0;
        padding-right: 2rem;
        min-height: 100px;
    }
    
    .header-logo svg {
        display: block;
    }
    
    .header-logo img {
        display: block;
    }
    
    /* Blue bar - Starts after logo, contains only title */
    .main-header {
        background: #0F97D5;
        padding: 1.5rem 2rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        justify-content: flex-end;
        flex: 1;
        min-height: 100px;
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 1.9rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-align: right;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        text-align: right;
    }
    
    /* Step cards */
    .step-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #0F97D5;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .step-card.success {
        border-left-color: #28a745;
    }
    
    .step-card.error {
        border-left-color: #dc3545;
    }
    
    .step-card.pending {
        border-left-color: #ffc107;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 0.25rem;
    }
    
    .status-success {
        background-color: #d4edda;
        color: #155724;
    }
    
    .status-pending {
        background-color: #fff3cd;
        color: #856404;
    }
    
    .status-error {
        background-color: #f8d7da;
        color: #721c24;
    }
    
    /* Metrics */
    .metric-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Logo container */
    .logo-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Pipeline visualization */
    .pipeline-step {
        display: flex;
        align-items: center;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 6px;
        background: #f8f9fa;
        transition: all 0.3s ease;
    }
    
    .pipeline-step.active {
        background: #e7f3ff;
        border-left: 3px solid #0F97D5;
    }
    
    .pipeline-step.completed {
        background: #d4edda;
        border-left: 3px solid #28a745;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom button styling */
    .stButton>button {
        background: #0F97D5;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: #0F97D5 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Session state for multiple files - using dictionaries keyed by file name
if 'files_data' not in st.session_state:
    st.session_state.files_data = {}  # {filename: {document_id, integrity_status, markdown_content, extracted_data, classification_result, labeling_result, errors, status}}
if 'errors' not in st.session_state:
    st.session_state.errors = []
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False
if 'model_name' not in st.session_state:
    st.session_state.model_name = ""
if 'show_processing_steps' not in st.session_state:
    st.session_state.show_processing_steps = False
if 'previous_uploaded_files' not in st.session_state:
    st.session_state.previous_uploaded_files = None
if 'file_uploader_key' not in st.session_state:
    st.session_state.file_uploader_key = 0
if 'cached_file_downloads' not in st.session_state:
    st.session_state.cached_file_downloads = {}  # {document_id: (file_content, filename)}


def display_success_with_icon(message: str):
    """Display success message with professional checkmark icon"""
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; 
                background-color: #d4edda; border-left: 4px solid #28a745; 
                border-radius: 4px; margin: 0.5rem 0;">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16.7071 5.29289C17.0976 5.68342 17.0976 6.31658 16.7071 6.70711L8.70711 14.7071C8.31658 15.0976 7.68342 15.0976 7.29289 14.7071L3.29289 10.7071C2.90237 10.3166 2.90237 9.68342 3.29289 9.29289C3.68342 8.90237 4.31658 8.90237 4.70711 9.29289L8 12.5858L15.2929 5.29289C15.6834 4.90237 16.3166 4.90237 16.7071 5.29289Z" fill="#28a745"/>
        </svg>
        <span style="color: #155724; font-weight: 500;">{message}</span>
    </div>
    """, unsafe_allow_html=True)


def display_error(error_msg: str, step: str):
    """Display error message and store in session state"""
    st.session_state.errors.append(f"[{step}] {error_msg}")
    st.error(f"**{step}**: {error_msg}")


def clear_errors():
    """Clear all errors from session state"""
    st.session_state.errors = []


def extract_backend_error_message(response) -> str:
    """Safely extract error message from backend response"""
    status_code = response.status_code
    
    try:
        error_data = response.json()
        error_fields = ['message', 'error', 'errorMessage', 'detail', 'errors', 'error_description']
        
        for field in error_fields:
            if field in error_data:
                value = error_data[field]
                if isinstance(value, list) and len(value) > 0:
                    return str(value[0])
                elif isinstance(value, dict):
                    return value.get('message', str(value))
                else:
                    return str(value)
        
        return f"HTTP {status_code}: {json.dumps(error_data)}"
        
    except (ValueError, json.JSONDecodeError):
        error_text = response.text.strip()
        if error_text:
            return f"HTTP {status_code}: {error_text}"
        else:
            return f"HTTP {status_code}: {response.reason if hasattr(response, 'reason') else 'Unknown error'}"


def authenticate_user(api_base_url: str, user_email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user and get access token"""
    try:
        url = f"{api_base_url}/auth/login"
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "userEmail": user_email,
            "password": password
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return {
                'accessToken': result.get('accessToken'),
                'refreshToken': result.get('refreshToken'),
                'userId': result.get('userId'),
                'userEmail': result.get('userEmail')
            }
        else:
            error_msg = extract_backend_error_message(response)
            raise Exception(error_msg)
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        raise Exception(str(e))


def get_step_status(step_key):
    """Get status for a pipeline step"""
    if not st.session_state.files_data:
        return 'pending'
    
    files_data = st.session_state.files_data
    if step_key == 'integrity_conversion':
        completed = sum(1 for f in files_data.values() if f.get('integrity_status') and f.get('markdown_content'))
        return 'completed' if completed > 0 else 'pending'
    elif step_key == 'extraction_classification':
        completed = sum(1 for f in files_data.values() if f.get('extracted_data') and f.get('classification_result'))
        return 'completed' if completed > 0 else 'pending'
    elif step_key == 'labeling':
        completed = sum(1 for f in files_data.values() if f.get('labeling_result'))
        return 'completed' if completed > 0 else 'pending'
    return 'pending'


def upload_document(api_base_url: str, auth_token: str, file, file_name: str, file_size: float, file_extension: str, user_id: str) -> Optional[str]:
    """Upload document and get document ID"""
    try:
        url = f"{api_base_url}/document/{AGENT_ID}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "fileName": file_name,
            "fileExtension": file_extension,
            "fileSize": file_size,
            "knowledgeType": "u",
            "modelName": ""
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            document_id = result.get('documentStoreId')
            if document_id:
                signed_url = result.get('signedUrl')
                if signed_url:
                    file.seek(0)
                    upload_headers = {
                        'Content-Type': 'application/octet-stream',
                        'x-ms-blob-type': 'BlockBlob'
                    }
                    upload_response = requests.put(signed_url, data=file.read(), headers=upload_headers, timeout=60)
                    if upload_response.status_code in [200, 201, 204]:
                        return document_id
                    else:
                        raise Exception(f"File upload to storage failed: {upload_response.status_code}")
                return document_id
            else:
                raise Exception("Document ID not found in response")
        else:
            error_msg = extract_backend_error_message(response)
            raise Exception(error_msg)
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        raise Exception(str(e))


def check_integrity(api_base_url: str, auth_token: str, document_id: str) -> Dict[str, Any]:
    """Check document integrity"""
    try:
        url = f"{api_base_url}/document-integrity/validate/{document_id}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = extract_backend_error_message(response)
            raise Exception(error_msg)
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        raise Exception(str(e))


def convert_document(api_base_url: str, auth_token: str, document_id: str) -> Dict[str, Any]:
    """Convert document to Markdown"""
    try:
        url = f"{api_base_url}/data-conversion/{document_id}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        payload = {}
        
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = extract_backend_error_message(response)
            raise Exception(error_msg)
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        raise Exception(str(e))


def extract_values(api_base_url: str, auth_token: str, markdown_content: str, extraction_mode: str = "automatic", user_keys: Optional[list] = None, document_id: Optional[str] = None) -> Dict[str, Any]:
    """Extract values from Markdown"""
    try:
        url = f"{api_base_url}/document-classification/extract-values"
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "markdown": markdown_content,
            "extractionMode": extraction_mode
        }
        
        if extraction_mode == "user_specified" and user_keys:
            payload["userKeys"] = user_keys
        
        if document_id:
            payload["documentId"] = document_id
        
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = extract_backend_error_message(response)
            raise Exception(error_msg)
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        raise Exception(str(e))


def classify_document(api_base_url: str, auth_token: str, extracted_fields: Dict, client_metadata: Dict, document_id: Optional[str] = None) -> Dict[str, Any]:
    """Classify document"""
    try:
        url = f"{api_base_url}/document-classification/classify-document"
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "extractedFields": extracted_fields,
            "clientMetadata": client_metadata
        }
        
        if document_id:
            payload["documentId"] = document_id
        
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = extract_backend_error_message(response)
            raise Exception(error_msg)
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        raise Exception(str(e))


def label_document(api_base_url: str, auth_token: str, document_id: str, document_class: str, probability_score: float, client_metadata: Dict) -> Dict[str, Any]:
    """Label document and enrich with external metadata"""
    try:
        url = f"{api_base_url}/data-labeling/label-document/{document_id}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "documentClass": document_class,
            "probabilityScore": probability_score,
            "clientMetadata": client_metadata
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = extract_backend_error_message(response)
            raise Exception(error_msg)
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        raise Exception(str(e))


def download_document(api_base_url: str, auth_token: str, agent_id: str, document_id: str, model_name: str, input_or_output: str) -> Tuple[bytes, str]:
    """
    Download document from the API
    
    Args:
        api_base_url: Base URL of the API
        auth_token: Authentication token
        agent_id: Agent ID
        document_id: Document ID (MongoDB ObjectId)
        model_name: Model name (can be empty string)
        input_or_output: Either "input" or "output"
    
    Returns:
        tuple: (file_content_bytes, filename)
    
    Raises:
        Exception: If download fails
    """
    try:
        url = f"{api_base_url}/document/download/{agent_id}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "documentId": document_id,
            "modelName": model_name or "",
            "inputOrOutput": input_or_output
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        
        if response.status_code == 200:
            # Extract filename from Content-Disposition header
            content_disposition = response.headers.get('Content-Disposition', '')
            filename = 'download'
            
            if content_disposition:
                # Parse filename from Content-Disposition header
                # Format: attachment; filename={fileName}
                filename_match = re.search(r'filename=(.+)', content_disposition)
                if filename_match:
                    filename = filename_match.group(1).strip('"\'')
            
            return response.content, filename
        elif response.status_code == 404:
            error_data = response.json() if response.headers.get('Content-Type', '').startswith('application/json') else {}
            error_msg = error_data.get('message', 'File not found.')
            raise Exception(error_msg)
        elif response.status_code == 401:
            error_data = response.json() if response.headers.get('Content-Type', '').startswith('application/json') else {}
            error_msg = error_data.get('message', 'Unauthorized - Please check your authentication token')
            raise Exception(error_msg)
        else:
            error_msg = extract_backend_error_message(response)
            raise Exception(f"Download failed: {error_msg}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        raise Exception(str(e))


def render_rsm_logo():
    """Render RSM logo - Prioritizes PNG, then JPG, falls back to SVG, then inline SVG"""
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    
    png_path = os.path.join(assets_dir, 'RSM.png')
    if os.path.exists(png_path):
        with open(png_path, 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            return f'<img src="data:image/png;base64,{image_base64}" alt="RSM Logo" style="height: 100%; max-height: 120px; width: auto; object-fit: contain;" />'
    
    jpg_path = os.path.join(assets_dir, 'RSM.jpg')
    if os.path.exists(jpg_path):
        with open(jpg_path, 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            return f'<img src="data:image/jpeg;base64,{image_base64}" alt="RSM Logo" style="height: 100%; max-height: 120px; width: auto; object-fit: contain;" />'
    
    svg_path = os.path.join(assets_dir, 'rsm_logo.svg')
    if os.path.exists(svg_path):
        with open(svg_path, 'r') as f:
            svg_content = f.read()
            svg_content = re.sub(r'(<text[^>]*fill=["\'])[^"\']*(["\'])', r'\1#2d3748\2', svg_content)
            def add_fill_if_missing(match):
                text_tag = match.group(0)
                if 'fill=' not in text_tag:
                    return text_tag.replace('>', ' fill="#2d3748">')
                return text_tag
            svg_content = re.sub(r'<text[^>]*>', add_fill_if_missing, svg_content)
            return f'<div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;"><div style="transform: scale(4.5); transform-origin: center center;">{svg_content}</div></div>'
    
    logo_svg = """
    <svg width="240" height="90" xmlns="http://www.w3.org/2000/svg">
        <rect x="0" y="0" width="24" height="24" fill="#718096" rx="2" opacity="0.9"/>
        <rect x="32" y="0" width="40" height="24" fill="#48bb78" rx="2"/>
        <rect x="80" y="0" width="64" height="24" fill="#4299e1" rx="2"/>
        <text x="0" y="72" font-family="Arial, sans-serif" font-size="40" font-weight="bold" fill="#2d3748">RSM</text>
    </svg>
    """
    return f'<div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;"><div style="transform: scale(1.5); transform-origin: center center;">{logo_svg}</div></div>'


def main():
    if not st.session_state.is_authenticated:
        with st.spinner("Authenticating..."):
            try:
                auth_result = authenticate_user(CORE_API_BASE_URL, USER_EMAIL, PASSWORD)
                st.session_state.auth_token = auth_result['accessToken']
                st.session_state.user_id = auth_result['userId']
                st.session_state.refresh_token = auth_result.get('refreshToken')
                st.session_state.is_authenticated = True
                st.success("Authentication successful!")
            except Exception as e:
                st.error(f"**Authentication failed**: {str(e)}")
                st.error("Please check your credentials and API base URL.")
                st.stop()
    
    st.markdown("""
    <div class="header-wrapper">
        <div class="header-logo">
            """ + render_rsm_logo() + """
        </div>
        <div class="main-header">
            <div style="text-align: right;">
                <h1>Data Intake and Labelling Agent</h1>
                <h3>Phase-I</h3>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### Configuration")
        st.markdown("---")
        
        if st.session_state.is_authenticated:
            st.success("**Authenticated**")
            st.caption(f"User: {USER_EMAIL}")
        
        st.markdown("---")
        
        st.info(f"""
        **Agent ID**  
        `{AGENT_ID}`
        """)
        
        st.markdown("---")
        
        st.markdown("### Pipeline Status")
        
        steps = [
            ("1", "Integrity Check & Document Conversion", get_step_status('integrity_conversion')),
            ("2", "Extraction & Classification", get_step_status('extraction_classification')),
            ("3", "Labeling & Data Output", get_step_status('labeling'))
        ]
        
        for num, name, status in steps:
            status_text = "Completed" if status == 'completed' else "Pending"
            status_class = "completed" if status == 'completed' else "pending"
            st.markdown(f"""
            <div class="pipeline-step {status_class}">
                <span><strong>{num}. {name}</strong> - {status_text}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("Clear All Results", use_container_width=True, type="secondary"):
            st.session_state.files_data = {}
            st.session_state.show_processing_steps = False
            clear_errors()
            st.rerun()
    
    st.markdown("### Document Upload & Processing")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "**Choose one or more documents to process**",
            type=['pdf', 'xlsx', 'xls', 'csv'],
            help="Supported formats: PDF, Excel (.xlsx, .xls), CSV. You can select multiple files.",
            accept_multiple_files=True,
            key=f"file_uploader_{st.session_state.file_uploader_key}"
        )
        
        # Check if files have changed and clear results/reset uploader if they have
        current_file_names = None
        if uploaded_files:
            current_file_names = tuple(sorted([f.name for f in uploaded_files]))
        
        # If files have changed (including when files are removed), clear all results and reset uploader
        files_changed = False
        should_reset_uploader = False
        
        if st.session_state.previous_uploaded_files is not None:
            if current_file_names != st.session_state.previous_uploaded_files:
                # Files have changed, clear all results
                st.session_state.files_data = {}
                st.session_state.show_processing_steps = False
                clear_errors()
                files_changed = True
                
                # Check if this is a completely new selection (no overlap with previous)
                # If so, reset the uploader to show only the new files
                if current_file_names is not None:
                    previous_set = set(st.session_state.previous_uploaded_files)
                    current_set = set(current_file_names)
                    # If there's no overlap, it's a new selection - reset uploader
                    if not previous_set.intersection(current_set) and len(current_set) > 0:
                        should_reset_uploader = True
        elif current_file_names is None and st.session_state.files_data:
            # Files were cleared (went from having files to no files)
            st.session_state.files_data = {}
            st.session_state.show_processing_steps = False
            clear_errors()
            files_changed = True
        
        # Reset uploader if needed
        if should_reset_uploader:
            st.session_state.file_uploader_key += 1
            st.session_state.previous_uploaded_files = current_file_names
            st.rerun()
        
        # Update previous uploaded files (only if files didn't change, to avoid double update)
        if not files_changed:
            st.session_state.previous_uploaded_files = current_file_names
        
        if uploaded_files:
            col_info, col_clear = st.columns([4, 1])
            with col_info:
                st.info(f"**{len(uploaded_files)} file(s) selected:**")
            with col_clear:
                if st.button("Clear", key="clear_files_button", use_container_width=True):
                    st.session_state.file_uploader_key += 1
                    st.session_state.previous_uploaded_files = None
                    st.session_state.files_data = {}
                    st.session_state.show_processing_steps = False
                    clear_errors()
                    st.rerun()
        
        st.markdown("---")
        
        # Always use automatic extraction mode
        extraction_mode = "automatic"
        user_keys_input = None
        
        process_button = st.button("Process Documents", type="primary", use_container_width=True)
    
    with col2:
        st.markdown("### Quick Info")
        st.markdown("""
        **Supported Formats:**
        - PDF Documents
        - Excel Files (.xlsx, .xls)
        - CSV Files
        
        **Multiple Files:**
        - Select multiple files to process
        - Files are processed sequentially through each step
        - Failed files are skipped in subsequent steps
        
        **Pipeline Steps:**
        1. Integrity Check & Document Conversion
        2. Extraction & Classification
        3. Labeling & Data Output
        """)
    
    if process_button:
        # Reset all states when starting new processing
        st.session_state.files_data = {}
        st.session_state.show_processing_steps = False
        st.session_state.cached_file_downloads = {}  # Clear download cache
        clear_errors()
        
        if not uploaded_files or len(uploaded_files) == 0:
            st.error("**Please upload at least one file first!**")
            return
        
        if not st.session_state.is_authenticated or not st.session_state.auth_token:
            st.error("**Authentication required!**")
            return
        
        # Validate all files first
        valid_files = []
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            file_extension = os.path.splitext(file_name)[1].lower()
            if file_extension not in ['.pdf', '.xlsx', '.xls', '.csv']:
                st.warning(f"**Skipping {file_name}**: Unsupported file type {file_extension}")
                continue
            valid_files.append(uploaded_file)
        
        if not valid_files:
            st.error("**No valid files to process!**")
            return
        
        # Initialize file data structures
        for uploaded_file in valid_files:
            file_name = uploaded_file.name
            st.session_state.files_data[file_name] = {
                'document_id': None,
                'integrity_status': None,
                'markdown_content': None,
                'extracted_data': None,
                'classification_result': None,
                'labeling_result': None,
                'errors': [],
                'status': 'pending',  # pending, step1_complete, step2_complete, step3_complete, failed
                'file_object': uploaded_file
            }
        
        # Set show_processing_steps to True now that we're starting processing
        st.session_state.show_processing_steps = True
        
        # Show processing steps during active processing
        st.markdown("---")
        st.markdown("### Processing Pipeline")
        st.markdown(f"**Processing {len(valid_files)} file(s) sequentially through each sub-step**")
        st.markdown("---")
        
        # SUB-STEP 1.1: Upload all files
        st.markdown("#### Step 1.1: Document Upload")
        st.markdown("---")
        
        for file_name, file_data in st.session_state.files_data.items():
            uploaded_file = file_data['file_object']
            file_size = uploaded_file.size
            file_extension = os.path.splitext(file_name)[1].lower()
            
            try:
                with st.spinner(f"Uploading {file_name}..."):
                    uploaded_file.seek(0)
                    document_id = upload_document(
                        CORE_API_BASE_URL, st.session_state.auth_token, uploaded_file, 
                        file_name, file_size, file_extension, st.session_state.user_id
                    )
                    file_data['document_id'] = document_id
                    display_success_with_icon(f"**{file_name}**: Uploaded successfully!")
            except Exception as e:
                error_msg = f"Upload failed: {str(e)}"
                file_data['errors'].append(error_msg)
                file_data['status'] = 'failed'
                st.error(f"**{file_name}**: {error_msg}")
        
        st.markdown("---")
        
        # SUB-STEP 1.2: Integrity Check all files
        st.markdown("#### Step 1.2: Integrity Check")
        st.markdown("---")
        
        files_passed_integrity = []
        for file_name, file_data in st.session_state.files_data.items():
            if file_data['status'] == 'failed' or not file_data.get('document_id'):
                continue
            
            document_id = file_data['document_id']
            try:
                with st.spinner(f"Validating {file_name}..."):
                    integrity_result = check_integrity(CORE_API_BASE_URL, st.session_state.auth_token, document_id)
                    file_data['integrity_status'] = integrity_result
                
                status = integrity_result.get('status', '').lower()
                if status == 'valid' or status == 'v':
                    display_success_with_icon(f"**{file_name}**: Integrity check passed!")
                    files_passed_integrity.append(file_name)
                else:
                    error_msg = integrity_result.get('message', 'Document validation failed')
                    file_data['errors'].append(f"Integrity Check: {error_msg}")
                    file_data['status'] = 'failed'
                    st.error(f"**{file_name}**: {error_msg}")
            except Exception as e:
                error_msg = f"Integrity Check failed: {str(e)}"
                file_data['errors'].append(error_msg)
                file_data['status'] = 'failed'
                st.error(f"**{file_name}**: {error_msg}")
        
        st.markdown("---")
        
        # SUB-STEP 1.3: Convert all files that passed integrity
        st.markdown("#### Step 1.3: Document Conversion")
        st.markdown("---")
        
        files_passed_step1 = []
        for file_name in files_passed_integrity:
            file_data = st.session_state.files_data[file_name]
            document_id = file_data['document_id']
            
            try:
                with st.spinner(f"Converting {file_name} to Markdown..."):
                    conversion_result = convert_document(CORE_API_BASE_URL, st.session_state.auth_token, document_id)
                    markdown_content = conversion_result.get('markdownContent', '')
                    file_data['markdown_content'] = markdown_content
                
                if markdown_content:
                    display_success_with_icon(f"**{file_name}**: Converted to Markdown successfully!")
                    file_data['status'] = 'step1_complete'
                    files_passed_step1.append(file_name)
                else:
                    raise Exception("No markdown content in response")
            except Exception as e:
                error_msg = f"Document Conversion failed: {str(e)}"
                file_data['errors'].append(error_msg)
                file_data['status'] = 'failed'
                st.error(f"**{file_name}**: {error_msg}")
        
        st.markdown("---")
        
        # SUB-STEP 2.1: Extract values from all files that passed step 1
        if files_passed_step1:
            st.markdown("#### Step 2.1: Value Extraction")
            st.markdown(f"**Processing {len(files_passed_step1)} file(s) that passed Step 1**")
            st.markdown("---")
            
            files_passed_extraction = []
            for file_name in files_passed_step1:
                file_data = st.session_state.files_data[file_name]
                document_id = file_data['document_id']
                markdown_content = file_data['markdown_content']
                
                try:
                    with st.spinner(f"Extracting values from {file_name}..."):
                        extraction_result = extract_values(
                            CLASSIFICATION_API_BASE_URL, st.session_state.auth_token, markdown_content, 
                            extraction_mode, None, document_id
                        )
                        file_data['extracted_data'] = extraction_result
                    
                    display_success_with_icon(f"**{file_name}**: Value extraction completed!")
                    files_passed_extraction.append(file_name)
                except Exception as e:
                    error_msg = f"Value Extraction failed: {str(e)}"
                    file_data['errors'].append(error_msg)
                    file_data['status'] = 'failed'
                    st.error(f"**{file_name}**: {error_msg}")
            
            st.markdown("---")
            
            # SUB-STEP 2.2: Classify all files that passed extraction
            if files_passed_extraction:
                st.markdown("#### Step 2.2: Document Classification")
                st.markdown("---")
                
                files_passed_step2 = []
                for file_name in files_passed_extraction:
                    file_data = st.session_state.files_data[file_name]
                    document_id = file_data['document_id']
                    extraction_result = file_data['extracted_data']
                    extracted_fields = extraction_result.get('extractedFields', {})
                    client_metadata = extraction_result.get('clientMetadata', {})
                    
                    try:
                        with st.spinner(f"Classifying {file_name}..."):
                            classification_result = classify_document(
                                CLASSIFICATION_API_BASE_URL, st.session_state.auth_token, extracted_fields, client_metadata, document_id
                            )
                            file_data['classification_result'] = classification_result
                        
                        document_class = classification_result.get('documentClass', 'Unknown')
                        display_success_with_icon(f"**{file_name}**: Classified as **{document_class}**")
                        file_data['status'] = 'step2_complete'
                        files_passed_step2.append(file_name)
                    except Exception as e:
                        error_msg = f"Document Classification failed: {str(e)}"
                        file_data['errors'].append(error_msg)
                        file_data['status'] = 'failed'
                        st.error(f"**{file_name}**: {error_msg}")
                
                st.markdown("---")
                
                # SUB-STEP 3: Label all files that passed step 2
                if files_passed_step2:
                    st.markdown("#### Step 3: Labeling & Data Output")
                    st.markdown(f"**Processing {len(files_passed_step2)} file(s) that passed Step 2**")
                    st.markdown("---")
                    
                    for file_name in files_passed_step2:
                        file_data = st.session_state.files_data[file_name]
                        classification_result = file_data['classification_result']
                        document_id = file_data['document_id']
                        extraction_result = file_data['extracted_data']
                        
                        try:
                            document_class = classification_result.get('documentClass', 'Unknown')
                            probability = classification_result.get('probabilityScore', 0.0)
                            
                            labeling_document_id = classification_result.get('documentId')
                            if not labeling_document_id:
                                labeling_document_id = document_id
                            
                            client_metadata = extraction_result.get('clientMetadata', {})
                            
                            with st.spinner(f"Labeling {file_name}..."):
                                labeling_result = label_document(
                                    CORE_API_BASE_URL, st.session_state.auth_token, labeling_document_id,
                                    document_class, probability, client_metadata
                                )
                                file_data['labeling_result'] = labeling_result
                            
                            label_path = labeling_result.get('labelPath', 'N/A')
                            display_success_with_icon(f"**{file_name}**: Labeled and enriched successfully!")
                            file_data['status'] = 'step3_complete'
                        except Exception as e:
                            error_msg = f"Labeling failed: {str(e)}"
                            file_data['errors'].append(error_msg)
                            file_data['status'] = 'failed'
                            st.error(f"**{file_name}**: {error_msg}")
                    
                    st.markdown("---")
    
    # Show processing pipeline results after processing completes (so they don't disappear on download clicks)
    # This shows the step-by-step results for each file
    if st.session_state.files_data and not process_button:
        # Check if any processing has been done
        has_processing_results = any(
            f.get('document_id') or f.get('integrity_status') or f.get('markdown_content') 
            or f.get('extracted_data') or f.get('classification_result') or f.get('labeling_result')
            for f in st.session_state.files_data.values()
        )
        
        if has_processing_results:
            st.markdown("---")
            st.markdown("### Processing Pipeline Results")
            st.markdown("---")
            
            # Show results for each file by step
            for file_name, file_data in st.session_state.files_data.items():
                # Only show if file has any processing results
                if file_data.get('document_id'):
                    # Determine file status for color coding
                    is_success = file_data.get('status') == 'step3_complete' or file_data.get('labeling_result')
                    is_failed = file_data.get('status') == 'failed' or file_data.get('errors')
                    
                    # Set color based on status
                    if is_success:
                        status_color = "#28a745"  # Green for success
                        status_icon = "✅"
                    elif is_failed:
                        status_color = "#dc3545"  # Red for failed
                        status_icon = "❌"
                    else:
                        status_color = "#6c757d"  # Gray for in progress
                        status_icon = "⏳"
                    
                    # Create styled expander header with color coding
                    st.markdown(f"""
                    <style>
                    .streamlit-expanderHeader {{
                        background-color: {status_color} !important;
                        color: white !important;
                        border-radius: 4px;
                        padding: 0.5rem 1rem !important;
                    }}
                    </style>
                    """, unsafe_allow_html=True)
                                        
                    expander_label = f"{status_icon} **{file_name}** - Processing Steps"
                    with st.expander(expander_label, expanded=False):
                        # Step 1 Results
                        if file_data.get('integrity_status') or file_data.get('markdown_content'):
                            st.markdown("#### Step 1: Integrity Check & Document Conversion")
                            
                            if file_data.get('integrity_status'):
                                status = file_data['integrity_status'].get('status', '').lower()
                                if status == 'valid' or status == 'v':
                                    display_success_with_icon("Document integrity check passed!")
                                else:
                                    error_msg = file_data['integrity_status'].get('message', 'Document validation failed')
                                    st.error(f"**Integrity Check**: {error_msg}")
                            
                            if file_data.get('markdown_content'):
                                display_success_with_icon("Document converted to Markdown successfully!")
                        
                        # Step 2 Results
                        if file_data.get('extracted_data') or file_data.get('classification_result'):
                            st.markdown("---")
                            st.markdown("#### Step 2: Value Extraction & Document Classification")
                            
                            if file_data.get('extracted_data'):
                                display_success_with_icon("Value extraction completed!")
                            
                            if file_data.get('classification_result'):
                                document_class = file_data['classification_result'].get('documentClass', 'Unknown')
                                display_success_with_icon("Document classified successfully!")
                                st.markdown(f"""
                                <div style="margin: 1rem 0 1.5rem 0;">
                                    <p style="font-size: 1rem; color: #6b7280; margin: 0.5rem 0;">Document Category</p>
                                    <p style="font-size: 1.5rem; font-weight: 600; color: #1e3a5f; margin: 0;">{document_class}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Step 3 Results
                        if file_data.get('labeling_result'):
                            st.markdown("---")
                            st.markdown("#### Step 3: Labeling & Data Output")
                            display_success_with_icon("Document labeled and enriched successfully!")
                        
                        # Show errors if any
                        if file_data.get('errors'):
                            st.markdown("---")
                            st.error("**Errors encountered for this file:**")
                            for error in file_data['errors']:
                                st.error(f"• {error}")
                        
                        # Close the colored border div
                        st.markdown("</div>", unsafe_allow_html=True)
    
    # Show summary, download all, and detailed results whenever we have processed files
    # Show them both during active processing and after, but keep them stable on download clicks
    if st.session_state.files_data:
        st.markdown("---")
        st.markdown("### Processing Summary")
        total_files = len(st.session_state.files_data)
        completed_files = sum(1 for f in st.session_state.files_data.values() if f['status'] == 'step3_complete')
        failed_files = sum(1 for f in st.session_state.files_data.values() if f['status'] == 'failed')
        
        col_sum1, col_sum2, col_sum3 = st.columns(3)
        with col_sum1:
            st.metric("Total Files", total_files)
        with col_sum2:
            st.metric("Completed", completed_files)
        with col_sum3:
            st.metric("Failed", failed_files)
        
        # Get completed file names
        completed_file_names = [name for name, data in st.session_state.files_data.items() if data['status'] == 'step3_complete']
        
        # Detailed Results for each file (show first, before zip creation)
        if completed_file_names:
            st.markdown("---")
            st.markdown("### Detailed Results")
            st.markdown("---")
            
            # First, render all expanders immediately with metadata (no downloads yet)
            for file_name in completed_file_names:
                file_data = st.session_state.files_data[file_name]
                classification_result = file_data.get('classification_result')
                labeling_result = file_data.get('labeling_result')
                
                with st.expander(f"📄 **{file_name}** - Detailed Results", expanded=False):
                    
                    if labeling_result:
                        label_path = labeling_result.get('labelPath', 'N/A')
                        enriched_client_metadata = labeling_result.get('clientMetadata', {})
                        internal_metadata = enriched_client_metadata.get('internal', {})
                        external_metadata = enriched_client_metadata.get('external', {})
                        
                        col_label1, col_label2 = st.columns(2)
                        with col_label1:
                            st.markdown("##### Internal Metadata")
                            st.json(internal_metadata)
                        with col_label2:
                            st.markdown("##### External Metadata")
                            st.json(external_metadata if external_metadata else {"message": "No external metadata found"})
                        
                        st.markdown(f"""
                        <div style="margin: 1rem 0 1.5rem 0;">
                            <p style="font-size: 1rem; color: #6b7280; margin: 0.5rem 0;">Document Path</p>
                            <p style="font-size: 1rem; font-weight: 500; color: #1e3a5f; margin: 0; word-break: break-all; line-height: 1.6;">{label_path}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Individual download button
                        labeling_document_id = None
                        if classification_result:
                            labeling_document_id = classification_result.get('documentId')
                        if not labeling_document_id:
                            labeling_document_id = file_data.get('document_id')
                        
                        if labeling_document_id:
                            # Cache file downloads to avoid re-downloading on reruns
                            cache_key = f"{labeling_document_id}_{file_name}"
                            
                            # Show download button if cached, otherwise show placeholder
                            if cache_key in st.session_state.cached_file_downloads and st.session_state.cached_file_downloads[cache_key]:
                                # File is cached, show button immediately
                                file_content, filename = st.session_state.cached_file_downloads[cache_key]
                                st.download_button(
                                    label=f"Download 📥",
                                    data=file_content,
                                    file_name=filename,
                                    mime="application/octet-stream",
                                    key=f"download_individual_{file_name}_{labeling_document_id}"
                                )
                            else:
                                # File not cached, show placeholder that will be replaced on next rerun
                                st.info("💾 Preparing download...")
            
            # Download All button (downloads all files as ZIP)
            # Check if all files are ready to download
            ready_files = []
            for file_name in completed_file_names:
                file_data = st.session_state.files_data[file_name]
                classification_result = file_data.get('classification_result')
                labeling_document_id = None
                if classification_result:
                    labeling_document_id = classification_result.get('documentId')
                if not labeling_document_id:
                    labeling_document_id = file_data.get('document_id')
                
                if labeling_document_id:
                    cache_key = f"{labeling_document_id}_{file_name}"
                    if cache_key in st.session_state.cached_file_downloads and st.session_state.cached_file_downloads[cache_key]:
                        file_content, filename = st.session_state.cached_file_downloads[cache_key]
                        ready_files.append((file_name, filename, file_content, labeling_document_id))
            
            if len(ready_files) > 1:
                st.markdown("---")
                st.markdown("### Download All Files")
                
                # Create ZIP file in memory
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for file_name, filename, file_content, labeling_document_id in ready_files:
                        # Add each file to the ZIP with its original filename
                        zip_file.writestr(filename, file_content)
                
                zip_buffer.seek(0)
                
                # Generate timestamp-based filename: dd-mm-yyyy:HH:MM:SS
                # Note: Using hyphens instead of colons for Windows compatibility
                timestamp = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
                zip_filename = f"{timestamp}.zip"
                
                # Offer ZIP download
                st.download_button(
                    label=f"Download All Files as ZIP ({len(ready_files)} files)",
                    data=zip_buffer.getvalue(),
                    file_name=zip_filename,
                    mime="application/zip",
                    use_container_width=True,
                    key="download_all_zip"
                )
            
            # Now download any missing files in the background (this will trigger a rerun)
            files_to_download = []
            for file_name in completed_file_names:
                file_data = st.session_state.files_data[file_name]
                classification_result = file_data.get('classification_result')
                labeling_document_id = None
                if classification_result:
                    labeling_document_id = classification_result.get('documentId')
                if not labeling_document_id:
                    labeling_document_id = file_data.get('document_id')
                
                if labeling_document_id:
                    cache_key = f"{labeling_document_id}_{file_name}"
                    if cache_key not in st.session_state.cached_file_downloads:
                        files_to_download.append((file_name, labeling_document_id, cache_key))
            
            # Download missing files
            if files_to_download:
                # Use a single spinner for all downloads
                with st.spinner(f"Preparing downloads for {len(files_to_download)} file(s)..."):
                    for file_name, labeling_document_id, cache_key in files_to_download:
                        try:
                            file_content, filename = download_document(
                                CORE_API_BASE_URL,
                                st.session_state.auth_token,
                                AGENT_ID,
                                labeling_document_id,
                                st.session_state.model_name,
                                "input"
                            )
                            st.session_state.cached_file_downloads[cache_key] = (file_content, filename)
                        except Exception as e:
                            st.warning(f"Could not download {file_name}: {str(e)}")
                            st.session_state.cached_file_downloads[cache_key] = None
                
                # Rerun to show download buttons
                st.rerun()
    
    # Legacy cached results section - commented out to prevent duplicate displays
    # The summary and detailed results are now shown above when not actively processing
    # This prevents re-rendering when download buttons are clicked
    # if not process_button and st.session_state.files_data:
    #     st.markdown("---")
    #     st.markdown("### Processing Results")
    #     st.markdown("---")
    #     ... (legacy code removed to prevent duplicates)
    
    if st.session_state.errors:
        st.markdown("---")
        st.error("### Errors Encountered")
        for error in st.session_state.errors:
            st.error(error)


if __name__ == "__main__":
    main()
