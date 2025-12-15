# RSM Document Intelligence Platform - Streamlit UI

**Professional Document Processing Pipeline Demo**

This Streamlit application provides a professional, client-ready interface to demonstrate the document processing pipeline with the following sequential steps:

1. **Document Upload** - Upload PDF, Excel, or CSV files
2. **Integrity Check** - Validate document structure and integrity
3. **Document Conversion** - Convert documents to Markdown format
4. **Value Extraction** - Extract structured fields and metadata
5. **Document Classification** - Classify documents into predefined categories

## Features

- ✅ **Professional RSM Branding** - Custom logo and color scheme
- ✅ **Sequential Pipeline Execution** - Step-by-step processing flow
- ✅ **Real-time Progress Indicators** - Visual status updates
- ✅ **Comprehensive Error Handling** - Clear error messages and recovery
- ✅ **JSON Response Visualization** - Formatted API responses
- ✅ **Markdown Content Preview** - View converted documents
- ✅ **Results Summary Dashboard** - Final classification metrics
- ✅ **Modern UI Design** - Clean, professional interface

## Prerequisites

- Python 3.8 or higher
- Backend API running (default: http://localhost:8080)
- Valid authentication token
- User ID

## Installation

1. Navigate to the StreamlitUI directory:
```bash
cd StreamlitUI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. The application will open in your default web browser (usually at http://localhost:8501)

3. Configure the application:
   - Enter the **API Base URL** (default: http://localhost:8080)
   - Enter your **Authorization Token** (Bearer token)
   - Enter your **User ID**

4. Upload a document:
   - Click "Browse files" and select a PDF, Excel, or CSV file
   - Choose extraction mode (automatic or user-specified)
   - If user-specified, enter comma-separated keys to extract

5. Click "🚀 Process Document" to start the pipeline

6. Monitor the progress:
   - Each step will show a spinner while processing
   - Success/error messages will appear for each step
   - Results will be displayed in expandable sections

## API Endpoints Used

1. `POST /document/<agentId>` - Document Upload
2. `POST /data-integrity/check/<agentId>` - Integrity Check
3. `POST /data-conversion/convert/<agentId>` - Document Conversion
4. `POST /document-classification/extract-values` - Value Extraction
5. `POST /document-classification/classify-document` - Document Classification

## Configuration

- **Agent ID**: Hardcoded as `6863c52887896a5cd21a2ef7`
- **API Base URL**: Configurable in the sidebar (default: http://localhost:8080)
- **Supported File Types**: PDF (.pdf), Excel (.xlsx, .xls), CSV (.csv)
- **Theme**: Custom RSM branding colors (configurable in `.streamlit/config.toml`)
- **Logo**: RSM logo SVG located in `assets/rsm_logo.svg` (can be replaced with your own logo)

## Error Handling

The application handles errors at each step:
- Network errors
- API errors (HTTP status codes)
- Validation errors
- Missing required fields

All errors are displayed in red with clear error messages indicating which step failed.

## Notes

- The pipeline stops if any step fails (except for warnings in integrity check)
- All results are stored in session state and persist until cleared
- Use the "Clear All Results" button to reset the application state
- File uploads are limited by the backend API (typically 20MB)

## Troubleshooting

**Connection Error**: Make sure the backend API is running and accessible at the configured URL.

**Authentication Error**: Verify that your token is valid and has the required permissions.

**File Upload Error**: Check file size (must be under 20MB) and file type (must be PDF, Excel, or CSV).

**Timeout Error**: Large files may take longer to process. The timeouts are configured in `config.py`.

## Support

For issues or questions, please contact the development team.

