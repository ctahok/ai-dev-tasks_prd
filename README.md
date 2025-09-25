# 🇦🇿 Azerbaijani Court Case Sorter

An AI-powered web application for processing, indexing, and searching Azerbaijani court documents with advanced natural language processing capabilities.

## ✨ Features

### 🔍 **Smart Document Processing**
- **PDF Processing**: Automatically extracts metadata from Azerbaijani court documents
- **Metadata Extraction**: Identifies key information including:
  - Court name (Məhkəmənin adı)
  - Case number (İş nömrəsi)
  - Judge name (Hakim)
  - Case type (İşin növü)
  - District (Rayon)
  - Decision type (QƏTNAMƏ/QƏRAR)
  - Year and dates
  - Parties involved

### 🤖 **AI-Powered Search**
- **Natural Language Queries**: Search in Azerbaijani using conversational language
- **RAG System**: Retrieval-Augmented Generation with open-source LLMs
- **Semantic Search**: Find documents based on meaning, not just keywords
- **Dynamic Filtering**: Interconnected dropdown filters that update based on selections

### 💬 **Intelligent AI Bot**
- **Azerbaijani Language Support**: Full Azerbaijani language processing
- **Context-Aware Responses**: Understands legal terminology and context
- **Query Analysis**: Breaks down complex queries into searchable components
- **Conversational Interface**: Chat-like interaction for document discovery

### 🗄️ **Advanced Database Management**
- **SQLite Backend**: Efficient storage and retrieval of document metadata
- **Vector Search**: ChromaDB integration for semantic similarity search
- **Scalable Architecture**: Designed to handle millions of documents
- **Admin Panel**: Document management and user administration

### 🌐 **Modern Web Interface**
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Updates**: Live search results and filter updates
- **File Upload**: Support for PDF and ZIP file uploads
- **Progress Tracking**: Visual feedback for document processing
- **Export Functionality**: Export search results in various formats

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Sample PDF court documents (optional, for testing)

### Installation

1. **Clone or download the project files**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the test script to verify installation:**
   ```bash
   python test_system.py
   ```

4. **Start the web application:**
   ```bash
   python main.py
   ```

5. **Open your browser and navigate to:**
   ```
   http://localhost:8000
   ```

### Default Login Credentials
- **Username**: `admin`
- **Password**: `admin123`

## 📁 Project Structure

```
├── main.py                 # Main FastAPI application
├── requirements.txt        # Python dependencies
├── test_system.py          # System test script
├── README.md              # This file
├──
├── app/                   # Core application modules
│   ├── __init__.py
│   ├── document_processor.py  # PDF processing and metadata extraction
│   ├── database.py           # Database management
│   ├── rag_system.py         # RAG system with vector search
│   ├── ai_bot.py             # AI bot for natural language queries
│   └── auth.py               # Authentication and authorization
│
├── templates/             # HTML templates
│   └── index.html            # Main web interface
│
└── static/               # Static assets
    ├── css/
    │   └── style.css         # Custom CSS styles
    └── js/
        └── app.js            # Frontend JavaScript
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_PATH=./court_documents.db

# RAG System Configuration
RAG_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
CHROMA_DB_PATH=./chroma_db

# Authentication
JWT_SECRET_KEY=your-secret-key-change-in-production

# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### Supported File Types
- **PDF**: Individual court document files
- **ZIP**: Archives containing multiple PDF files

### Supported Courts
The system is pre-configured to recognize common Azerbaijani courts:
- Ağdam Rayon Məhkəməsi
- Şirvan Apellyasiya Məhkəməsi
- Şirvan İnzibati Məhkəməsi
- Şirvan Kommersiya Məhkəməsi

## 🧪 Testing

### Run System Tests
```bash
python test_system.py
```

This will test:
- ✅ Document processing with sample files
- ✅ Database operations
- ✅ RAG system functionality
- ✅ AI bot responses
- ✅ Full pipeline integration

### Manual Testing
1. **Upload Documents**: Use the web interface to upload PDF files
2. **Search**: Try natural language queries in Azerbaijani
3. **Filter**: Use dynamic filters to narrow down results
4. **Chat**: Interact with the AI bot for assistance

## 🔍 Usage Examples

### Natural Language Queries
```
"Hakim Fikrət Hüseynovun qərarları"
"Ağdam rayon məhkəməsinin 2025-ci il qərarları"
"Mülki işlər üzrə qətnamələr"
"Şirvan Apellyasiya Məhkəməsinin inzibati işləri"
```

### Structured Search
- Filter by judge name
- Filter by court type
- Filter by year
- Filter by case type
- Combine multiple filters

## 🏗️ Architecture

### Core Components

1. **Document Processor** (`document_processor.py`)
   - PDF text extraction using pdfplumber
   - Azerbaijani text pattern recognition
   - Metadata extraction with regex patterns
   - Document validation and cleaning

2. **Database Manager** (`database.py`)
   - SQLite database with optimized schema
   - Document storage and retrieval
   - Metadata indexing for fast filtering
   - Filter options caching

3. **RAG System** (`rag_system.py`)
   - Sentence transformer embeddings
   - ChromaDB vector storage
   - Semantic similarity search
   - Document chunking and indexing

4. **AI Bot** (`ai_bot.py`)
   - Natural language understanding
   - Query analysis and parsing
   - Azerbaijani legal terminology
   - Conversational responses

5. **Authentication** (`auth.py`)
   - JWT-based authentication
   - User management
   - Role-based access control
   - Password hashing with bcrypt

### Technology Stack
- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Database**: SQLite with ChromaDB
- **AI/ML**: Sentence Transformers, PyTorch
- **Document Processing**: pdfplumber, PyPDF2
- **Authentication**: JWT, bcrypt
- **UI Framework**: Bootstrap 5

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for secure password storage
- **Input Validation**: Comprehensive input sanitization
- **File Upload Security**: File type validation and size limits
- **SQL Injection Protection**: Parameterized queries
- **XSS Protection**: HTML escaping and content sanitization

## 📊 Performance

### Scalability Features
- **Vector Indexing**: Efficient similarity search with ChromaDB
- **Database Optimization**: Indexed queries and connection pooling
- **Chunked Processing**: Memory-efficient document processing
- **Caching**: Filter options and metadata caching
- **Async Processing**: Non-blocking file uploads and processing

### Resource Requirements
- **Minimum**: 4GB RAM, 2 CPU cores
- **Recommended**: 8GB RAM, 4 CPU cores
- **Storage**: 10GB+ for document storage and embeddings

## 🚀 Deployment

### Local Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### Production Deployment (Docker)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

### Cloud Deployment
The system is designed to work with:
- **Replit**: Ready-to-deploy configuration
- **Heroku**: With Gunicorn WSGI server
- **AWS**: EC2, Lambda, or ECS
- **Google Cloud**: Cloud Run or Compute Engine
- **Azure**: Container Instances or VMs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include type hints
- Write comprehensive tests
- Update documentation

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the test files for usage examples

## 🔄 Future Enhancements

### Planned Features
- [ ] Multi-language support (English, Russian)
- [ ] Advanced analytics and reporting
- [ ] Batch document processing API
- [ ] Integration with e-mehkeme.gov.az scraping
- [ ] Mobile application
- [ ] Real-time collaboration features
- [ ] Advanced export formats (PDF, Excel, CSV)
- [ ] Machine learning model fine-tuning
- [ ] Document similarity scoring
- [ ] Citation network analysis

### Roadmap
- **v1.1**: Enhanced UI/UX and performance optimizations
- **v1.2**: Multi-language support and advanced analytics
- **v2.0**: Integration with external court databases
- **v2.1**: Machine learning model improvements
- **v3.0**: Enterprise features and API expansion

---

**Built with ❤️ for the Azerbaijani legal community**

*Empowering legal professionals with AI-driven document discovery and analysis*
