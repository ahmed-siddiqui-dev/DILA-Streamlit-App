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
from typing import Optional, Dict, Any, Tuple

# Hardcoded Agent ID
AGENT_ID = "69174f5b808a5f1b07561164"

CORE_API_BASE_URL = "http://localhost:8080"
CLASSIFICATION_API_BASE_URL = "http://localhost:8082"
LABELING_API_BASE_URL = "http://localhost:8081"
USER_EMAIL = "moeed.ahmad1@intellixcore1.ai"
PASSWORD = "Test@1234"

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
        margin: 0.25rem 0 0 0;
        font-size: 0.95rem;
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

if 'document_id' not in st.session_state:
    st.session_state.document_id = None
if 'integrity_status' not in st.session_state:
    st.session_state.integrity_status = None
if 'markdown_content' not in st.session_state:
    st.session_state.markdown_content = None
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None
if 'classification_result' not in st.session_state:
    st.session_state.classification_result = None
if 'labeling_result' not in st.session_state:
    st.session_state.labeling_result = None
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
if 'downloaded_file_data' not in st.session_state:
    st.session_state.downloaded_file_data = None
if 'downloaded_file_name' not in st.session_state:
    st.session_state.downloaded_file_name = None
if 'show_processing_steps' not in st.session_state:
    st.session_state.show_processing_steps = False


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
    if step_key == 'integrity_conversion':
        return 'completed' if (st.session_state.integrity_status and st.session_state.markdown_content) else 'pending'
    elif step_key == 'extraction_classification':
        return 'completed' if (st.session_state.extracted_data and st.session_state.classification_result) else 'pending'
    elif step_key == 'labeling':
        return 'completed' if st.session_state.labeling_result else 'pending'
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
            <h1>Data Intake and Labelling Agent</h1>
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
            st.session_state.document_id = None
            st.session_state.integrity_status = None
            st.session_state.markdown_content = None
            st.session_state.extracted_data = None
            st.session_state.classification_result = None
            st.session_state.labeling_result = None
            st.session_state.downloaded_file_data = None
            st.session_state.downloaded_file_name = None
            st.session_state.show_processing_steps = False
            clear_errors()
            st.rerun()
    
    st.markdown("### Document Upload & Processing")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "**Choose a document to process**",
            type=['pdf', 'xlsx', 'xls', 'csv'],
            help="Supported formats: PDF, Excel (.xlsx, .xls), CSV"
        )
        
        if uploaded_file:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.info(f"**File**: {uploaded_file.name} | **Size**: {file_size_mb:.2f} MB")
        
        st.markdown("---")
        
        # Extraction mode dropdown - commented out (using auto-extraction only)
        # extraction_mode_options = {
        #     "Auto-Extraction Mode": "automatic",
        #     "User specified Mode": "user_specified"
        # }
        # 
        # selected_label = st.selectbox(
        #     "**Extraction Mode**",
        #     options=list(extraction_mode_options.keys()),
        #     help="Choose automatic extraction or specify keys manually"
        # )
        # 
        # extraction_mode = extraction_mode_options[selected_label]
        # 
        # user_keys_input = None
        # if extraction_mode == "user_specified":
        #     user_keys_input = st.text_input(
        #         "**User Keys** (comma-separated)",
        #         placeholder="e.g., Invoice_no, Amount, Account_number",
        #         help="Enter keys to extract, separated by commas"
        #     )
        
        # Always use automatic extraction mode
        extraction_mode = "automatic"
        user_keys_input = None
        
        process_button = st.button("Process Document", type="primary", use_container_width=True)
    
    with col2:
        st.markdown("### Quick Info")
        st.markdown("""
        **Supported Formats:**
        - PDF Documents
        - Excel Files (.xlsx, .xls)
        - CSV Files
        
        **Pipeline Steps:**
        1. Integrity Check & Document Conversion
        2. Extraction & Classification
        3. Labeling & Data Output
        """)
    
    if process_button:
        # Reset all states when starting new processing
        st.session_state.document_id = None
        st.session_state.integrity_status = None
        st.session_state.markdown_content = None
        st.session_state.extracted_data = None
        st.session_state.classification_result = None
        st.session_state.labeling_result = None
        st.session_state.downloaded_file_data = None
        st.session_state.downloaded_file_name = None
        st.session_state.show_processing_steps = False
        clear_errors()
        
        if not uploaded_file:
            st.error("**Please upload a file first!**")
            return
        
        if not st.session_state.is_authenticated or not st.session_state.auth_token:
            st.error("**Authentication required!**")
            return
        
        # Set show_processing_steps to True now that we're starting processing
        st.session_state.show_processing_steps = True
        
        file_name = uploaded_file.name
        file_size = uploaded_file.size
        file_extension = os.path.splitext(file_name)[1].lower()
        
        if file_extension not in ['.pdf', '.xlsx', '.xls', '.csv']:
            st.error(f"**Unsupported file type**: {file_extension}")
            return
        
        with st.spinner("Uploading document..."):
            try:
                uploaded_file.seek(0)
                document_id = upload_document(
                    CORE_API_BASE_URL, st.session_state.auth_token, uploaded_file, 
                    file_name, file_size, file_extension, st.session_state.user_id
                )
                st.session_state.document_id = document_id
                # Store model_name (currently empty string, but may be used later)
                st.session_state.model_name = ""
            except Exception as e:
                display_error(str(e), "Document Upload")
                st.stop()
        
        # Show processing steps during active processing
        st.markdown("---")
        st.markdown("### Processing Pipeline")
        st.markdown("---")
        
        with st.container():
                st.markdown("#### Step 1: Integrity Check & Document Conversion")
                
                st.markdown("##### 1.1 Integrity Check")
                try:
                    with st.spinner("Validating document structure and integrity..."):
                        integrity_result = check_integrity(CORE_API_BASE_URL, st.session_state.auth_token, document_id)
                        st.session_state.integrity_status = integrity_result
                    
                    status = integrity_result.get('status', '').lower()
                    if status == 'valid' or status == 'v':
                        display_success_with_icon("Document integrity check passed!")
                    else:
                        error_msg = integrity_result.get('message', 'Document validation failed')
                        display_error(error_msg, "Integrity Check")
                        st.warning("**Integrity check failed. Pipeline stopped.**")
                        st.stop()
                        
                except Exception as e:
                    display_error(str(e), "Integrity Check")
                    st.stop()
                
                st.markdown("---")
                
                st.markdown("##### 1.2 Document Conversion")
                try:
                    with st.spinner("Converting document to Markdown format..."):
                        conversion_result = convert_document(CORE_API_BASE_URL, st.session_state.auth_token, document_id)
                        markdown_content = conversion_result.get('markdownContent', '')
                        st.session_state.markdown_content = markdown_content
                    
                    if markdown_content:
                        display_success_with_icon("Document converted to Markdown successfully!")
                    else:
                        raise Exception("No markdown content in response")
                        
                except Exception as e:
                    display_error(str(e), "Document Conversion")
                    st.stop()
        
        st.markdown("---")
        
        with st.container():
                st.markdown("#### Step 2: Value Extraction & Document Classification")
                
                st.markdown("##### 2.1 Value Extraction")
                try:
                    with st.spinner("Extracting structured fields and metadata..."):
                        # User-specified keys logic - commented out (using auto-extraction only)
                        # user_keys_list = None
                        # if extraction_mode == "user_specified" and user_keys_input:
                        #     user_keys_list = [key.strip() for key in user_keys_input.split(',') if key.strip()]
                        
                        extraction_result = extract_values(
                            CLASSIFICATION_API_BASE_URL, st.session_state.auth_token, markdown_content, 
                            extraction_mode, None, document_id
                        )
                        st.session_state.extracted_data = extraction_result
                    
                    extracted_fields = extraction_result.get('extractedFields', {})
                    client_metadata = extraction_result.get('clientMetadata', {})
                    
                    display_success_with_icon("Value extraction completed!")
                        
                except Exception as e:
                    display_error(str(e), "Value Extraction")
                    st.stop()
                
                st.markdown("---")
                
                st.markdown("##### 2.2 Document Classification")
                try:
                    with st.spinner("Classifying document using AI..."):
                        classification_result = classify_document(
                            CLASSIFICATION_API_BASE_URL, st.session_state.auth_token, extracted_fields, client_metadata, document_id
                        )
                        st.session_state.classification_result = classification_result
                    
                    document_class = classification_result.get('documentClass', 'Unknown')
                    probability = classification_result.get('probabilityScore', 0.0)
                    classification_document_id = classification_result.get('documentId', document_id)
                    
                    display_success_with_icon("Document classified successfully!")
                    
                    st.markdown(f"""
                    <div style="margin: 1rem 0 1.5rem 0;">
                        <p style="font-size: 1rem; color: #6b7280; margin: 0.5rem 0;">Document Category</p>
                        <p style="font-size: 1.5rem; font-weight: 600; color: #1e3a5f; margin: 0;">{document_class}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    display_error(str(e), "Document Classification")
                    st.stop()
        
        st.markdown("---")
        
        with st.container():
                st.markdown("#### Step 3: Labeling & Data Output")
                try:
                    classification_result = st.session_state.classification_result
                    if not classification_result:
                        raise Exception("Classification result not found")
                    
                    document_class = classification_result.get('documentClass', 'Unknown')
                    probability = classification_result.get('probabilityScore', 0.0)
                    
                    labeling_document_id = classification_result.get('documentId')
                    if not labeling_document_id:
                        labeling_document_id = document_id
                        if not labeling_document_id:
                            raise Exception("Document ID not found")
                    
                    extraction_result = st.session_state.extracted_data
                    if not extraction_result:
                        raise Exception("Extraction result not found")
                    client_metadata = extraction_result.get('clientMetadata', {})
                    
                    with st.spinner("Enriching document with external metadata and applying labeling rules..."):
                        labeling_result = label_document(
                            LABELING_API_BASE_URL, st.session_state.auth_token, labeling_document_id,
                            document_class, probability, client_metadata
                        )
                        st.session_state.labeling_result = labeling_result
                    
                    label_path = labeling_result.get('labelPath', 'N/A')
                    enriched_client_metadata = labeling_result.get('clientMetadata', {})
                    internal_metadata = enriched_client_metadata.get('internal', {})
                    external_metadata = enriched_client_metadata.get('external', {})
                    
                    display_success_with_icon("Document labeled and enriched successfully!")
                    
                    st.markdown(f"""
                    <div style="margin: 1rem 0 1.5rem 0;">
                        <p style="font-size: 1rem; color: #6b7280; margin: 0.5rem 0;">Document Category</p>
                        <p style="font-size: 1.5rem; font-weight: 600; color: #1e3a5f; margin: 0;">{document_class}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_label1, col_label2 = st.columns(2)
                    with col_label1:
                        st.markdown("##### Internal Metadata")
                        st.json(internal_metadata)
                    with col_label2:
                        st.markdown("##### External Metadata")
                        st.json(external_metadata if external_metadata else {"message": "No external metadata found"})
                    
                    st.markdown("---")
                    display_success_with_icon("Document Labeling Completed Successfully")
                    
                    # Show download button as part of processing results
                    labeling_document_id_for_download = labeling_document_id
                    
                    # Document Path with Download Button
                    col_path, col_download = st.columns([5, 1])
                    with col_path:
                        st.markdown(f"""
                        <div style="margin: 1rem 0 1.5rem 0;">
                            <p style="font-size: 1rem; color: #6b7280; margin: 0.5rem 0;">Document Path</p>
                            <p style="font-size: 1rem; font-weight: 500; color: #1e3a5f; margin: 0; word-break: break-all; line-height: 1.6;">{label_path}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_download:
                        st.markdown("<div style='margin-top: 2.5rem;'></div>", unsafe_allow_html=True)
                        
                        # If file not cached, fetch it first
                        if not st.session_state.downloaded_file_data or not st.session_state.downloaded_file_name:
                            try:
                                with st.spinner("Preparing download..."):
                                    file_content, filename = download_document(
                                        CORE_API_BASE_URL,
                                        st.session_state.auth_token,
                                        AGENT_ID,
                                        labeling_document_id_for_download,
                                        st.session_state.model_name,
                                        "input"
                                    )
                                    st.session_state.downloaded_file_data = file_content
                                    st.session_state.downloaded_file_name = filename
                            except Exception as e:
                                st.error(f"**Download failed**: {str(e)}")
                        
                        # Show download button if file data is available
                        if st.session_state.downloaded_file_data and st.session_state.downloaded_file_name:
                            st.download_button(
                                label="📥 Download",
                                data=st.session_state.downloaded_file_data,
                                file_name=st.session_state.downloaded_file_name,
                                mime="application/octet-stream",
                                key="save_input_file_persistent"
                            )
                    
                except Exception as e:
                    display_error(str(e), "Labeling & Data Output")
                    st.stop()
    
    # Show cached results when not actively processing (e.g., after download button click)
    if not process_button and st.session_state.labeling_result and st.session_state.document_id:
        st.markdown("---")
        st.markdown("### Processing Pipeline")
        st.markdown("---")
        
        with st.container():
            st.markdown("#### Step 1: Integrity Check & Document Conversion")
            
            st.markdown("##### 1.1 Integrity Check")
            if st.session_state.integrity_status:
                status = st.session_state.integrity_status.get('status', '').lower()
                if status == 'valid' or status == 'v':
                    display_success_with_icon("Document integrity check passed!")
                else:
                    error_msg = st.session_state.integrity_status.get('message', 'Document validation failed')
                    st.error(f"**Integrity Check**: {error_msg}")
            
            st.markdown("---")
            
            st.markdown("##### 1.2 Document Conversion")
            if st.session_state.markdown_content:
                display_success_with_icon("Document converted to Markdown successfully!")
        
        st.markdown("---")
        
        with st.container():
            st.markdown("#### Step 2: Value Extraction & Document Classification")
            
            st.markdown("##### 2.1 Value Extraction")
            if st.session_state.extracted_data:
                display_success_with_icon("Value extraction completed!")
            
            st.markdown("---")
            
            st.markdown("##### 2.2 Document Classification")
            if st.session_state.classification_result:
                document_class = st.session_state.classification_result.get('documentClass', 'Unknown')
                display_success_with_icon("Document classified successfully!")
                
                st.markdown(f"""
                <div style="margin: 1rem 0 1.5rem 0;">
                    <p style="font-size: 1rem; color: #6b7280; margin: 0.5rem 0;">Document Category</p>
                    <p style="font-size: 1.5rem; font-weight: 600; color: #1e3a5f; margin: 0;">{document_class}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        with st.container():
            st.markdown("#### Step 3: Labeling & Data Output")
            if st.session_state.labeling_result:
                classification_result = st.session_state.classification_result
                document_class = classification_result.get('documentClass', 'Unknown') if classification_result else 'Unknown'
                
                label_path = st.session_state.labeling_result.get('labelPath', 'N/A')
                enriched_client_metadata = st.session_state.labeling_result.get('clientMetadata', {})
                internal_metadata = enriched_client_metadata.get('internal', {})
                external_metadata = enriched_client_metadata.get('external', {})
                
                display_success_with_icon("Document labeled and enriched successfully!")
                
                st.markdown(f"""
                <div style="margin: 1rem 0 1.5rem 0;">
                    <p style="font-size: 1rem; color: #6b7280; margin: 0.5rem 0;">Document Category</p>
                    <p style="font-size: 1.5rem; font-weight: 600; color: #1e3a5f; margin: 0;">{document_class}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col_label1, col_label2 = st.columns(2)
                with col_label1:
                    st.markdown("##### Internal Metadata")
                    st.json(internal_metadata)
                with col_label2:
                    st.markdown("##### External Metadata")
                    st.json(external_metadata if external_metadata else {"message": "No external metadata found"})
                
                st.markdown("---")
                display_success_with_icon("Document Labeling Completed Successfully")
                
                # Show download button as part of processing results
                labeling_document_id = None
                if st.session_state.classification_result:
                    labeling_document_id = st.session_state.classification_result.get('documentId')
                if not labeling_document_id:
                    labeling_document_id = st.session_state.document_id
                
                # Document Path with Download Button
                col_path, col_download = st.columns([5, 1])
                with col_path:
                    st.markdown(f"""
                    <div style="margin: 1rem 0 1.5rem 0;">
                        <p style="font-size: 1rem; color: #6b7280; margin: 0.5rem 0;">Document Path</p>
                        <p style="font-size: 1rem; font-weight: 500; color: #1e3a5f; margin: 0; word-break: break-all; line-height: 1.6;">{label_path}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col_download:
                    st.markdown("<div style='margin-top: 2.5rem;'></div>", unsafe_allow_html=True)
                    
                    # If file not cached, fetch it first
                    if not st.session_state.downloaded_file_data or not st.session_state.downloaded_file_name:
                        try:
                            with st.spinner("Preparing download..."):
                                file_content, filename = download_document(
                                    CORE_API_BASE_URL,
                                    st.session_state.auth_token,
                                    AGENT_ID,
                                    labeling_document_id,
                                    st.session_state.model_name,
                                    "input"
                                )
                                st.session_state.downloaded_file_data = file_content
                                st.session_state.downloaded_file_name = filename
                        except Exception as e:
                            st.error(f"**Download failed**: {str(e)}")
                    
                    # Show download button if file data is available
                    if st.session_state.downloaded_file_data and st.session_state.downloaded_file_name:
                        st.download_button(
                            label="📥 Download",
                            data=st.session_state.downloaded_file_data,
                            file_name=st.session_state.downloaded_file_name,
                            mime="application/octet-stream",
                            key="save_input_file_persistent"
                        )
    
    if st.session_state.errors:
        st.markdown("---")
        st.error("### Errors Encountered")
        for error in st.session_state.errors:
            st.error(error)


if __name__ == "__main__":
    main()
