# Azerbaijani Court Case Sorter - Replit Project

## Project Overview
An AI-powered web application for processing, indexing, and searching Azerbaijani court documents with advanced natural language processing capabilities.

## Current Setup Status
- **Language**: Python 3.11 
- **Framework**: FastAPI
- **Port**: 5000 (configured for Replit environment)
- **Status**: Successfully imported and running

## Key Features
- Smart PDF document processing for Azerbaijani court documents
- AI-powered search with natural language queries
- Document metadata extraction (court names, judges, case types, etc.)
- User authentication with JWT tokens
- Responsive web interface with Bootstrap

## Architecture
- **Backend**: FastAPI with Uvicorn
- **Database**: SQLite for document storage
- **Authentication**: JWT with bcrypt password hashing
- **Frontend**: HTML5, CSS3, JavaScript
- **Document Processing**: PDF parsing with metadata extraction

## Current Configuration
- Host: 0.0.0.0 (configured for Replit proxy environment)
- Port: 5000 (required for Replit frontend)
- Deployment: Configured for autoscale deployment

## Development Notes
- Initial setup uses stub versions of AI/ML components to avoid heavy dependencies
- Core FastAPI application is fully functional
- PDF processing and document management systems are operational
- Authentication system with admin user (admin/admin123) is working

## Project Structure
```
├── main.py                 # Main FastAPI application (port 5000)
├── requirements.txt        # Python dependencies
├── app/                   # Core application modules
│   ├── database.py        # SQLite document storage
│   ├── auth.py           # JWT authentication
│   ├── document_processor.py  # PDF processing
│   ├── rag_system_stub.py    # Simplified RAG system
│   └── ai_bot_stub.py        # Simplified AI bot
├── templates/             # HTML templates
│   └── index.html        # Main interface
└── static/               # CSS and JavaScript assets
    ├── css/style.css
    └── js/app.js
```

## Recent Changes (Import Setup)
1. Configured FastAPI to run on port 5000 with 0.0.0.0 host
2. Created stub versions of AI/ML components for initial functionality
3. Fixed import issues in authentication module
4. Set up workflow for continuous server operation
5. Configured autoscale deployment settings

## Default Credentials
- Username: admin
- Password: admin123

## Future Enhancements
- Integration of full AI/ML capabilities (sentence transformers, ChromaDB)
- Enhanced document processing with OCR
- Multi-language support
- Advanced analytics and reporting