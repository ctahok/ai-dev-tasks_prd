"""
Database Manager for Court Documents
Handles document storage, retrieval, and search operations
"""

import sqlite3
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import os
import hashlib

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages document storage and retrieval operations"""

    def __init__(self, db_path: str = "./court_documents.db"):
        """
        Initialize database manager

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        """Initialize the database and create tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    file_path TEXT,
                    text_content TEXT,
                    metadata TEXT,  -- JSON string
                    processed_at TEXT NOT NULL,
                    status TEXT DEFAULT 'processed',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Document metadata index table for faster filtering
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS document_metadata (
                    document_id TEXT PRIMARY KEY,
                    court_name TEXT,
                    case_number TEXT,
                    judge TEXT,
                    case_type TEXT,
                    district TEXT,
                    decision_type TEXT,
                    year TEXT,
                    applicant TEXT,
                    parties TEXT,  -- JSON string
                    dates TEXT,    -- JSON string
                    FOREIGN KEY (document_id) REFERENCES documents (id)
                )
            ''')

            # Filter options cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS filter_options (
                    filter_type TEXT PRIMARY KEY,
                    options TEXT,  -- JSON string
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Users table for authentication
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    password_hash TEXT NOT NULL,
                    is_admin BOOLEAN DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
            conn.close()

            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

    def store_document(self, doc_data: Dict[str, Any]) -> str:
        """
        Store a document in the database

        Args:
            doc_data: Document data dictionary

        Returns:
            Document ID
        """
        try:
            # Generate document ID
            doc_id = self._generate_document_id(doc_data)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Store main document
            cursor.execute('''
                INSERT OR REPLACE INTO documents
                (id, filename, file_path, text_content, metadata, processed_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc_id,
                doc_data.get('filename', ''),
                doc_data.get('file_path', ''),
                doc_data.get('text_content', ''),
                json.dumps(doc_data.get('metadata', {})),
                doc_data.get('processed_at', datetime.now().isoformat()),
                doc_data.get('status', 'processed')
            ))

            # Store metadata for filtering
            metadata = doc_data.get('metadata', {})
            cursor.execute('''
                INSERT OR REPLACE INTO document_metadata
                (document_id, court_name, case_number, judge, case_type,
                 district, decision_type, year, applicant, parties, dates)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc_id,
                metadata.get('court_name', ''),
                metadata.get('case_number', ''),
                metadata.get('judge', ''),
                metadata.get('case_type', ''),
                metadata.get('district', ''),
                metadata.get('decision_type', ''),
                metadata.get('year', ''),
                metadata.get('applicant', ''),
                json.dumps(metadata.get('parties', [])),
                json.dumps(metadata.get('dates', {}))
            ))

            conn.commit()
            conn.close()

            # Update filter options cache
            self._update_filter_options()

            logger.info(f"Stored document {doc_id} in database")
            return doc_id

        except Exception as e:
            logger.error(f"Error storing document: {str(e)}")
            raise

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a document from the database

        Args:
            doc_id: Document ID

        Returns:
            Document data dictionary or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT d.*, dm.*
                FROM documents d
                LEFT JOIN document_metadata dm ON d.id = dm.document_id
                WHERE d.id = ?
            ''', (doc_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return self._row_to_document_dict(row)
            else:
                return None

        except Exception as e:
            logger.error(f"Error retrieving document {doc_id}: {str(e)}")
            return None

    def search_documents(self, filters: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Search documents using structured filters

        Args:
            filters: Dictionary of filter criteria

        Returns:
            List of matching documents
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Build query dynamically based on filters
            query_parts = []
            params = []

            if filters.get('judge'):
                query_parts.append("dm.judge LIKE ?")
                params.append(f"%{filters['judge']}%")

            if filters.get('court'):
                query_parts.append("dm.court_name LIKE ?")
                params.append(f"%{filters['court']}%")

            if filters.get('case_type'):
                query_parts.append("dm.case_type LIKE ?")
                params.append(f"%{filters['case_type']}%")

            if filters.get('district'):
                query_parts.append("dm.district LIKE ?")
                params.append(f"%{filters['district']}%")

            if filters.get('year'):
                query_parts.append("dm.year = ?")
                params.append(filters['year'])

            if filters.get('decision_type'):
                query_parts.append("dm.decision_type LIKE ?")
                params.append(f"%{filters['decision_type']}%")

            # Base query
            if query_parts:
                where_clause = " AND ".join(query_parts)
                query = f'''
                    SELECT d.*, dm.*
                    FROM documents d
                    LEFT JOIN document_metadata dm ON d.id = dm.document_id
                    WHERE {where_clause}
                    ORDER BY d.created_at DESC
                    LIMIT 100
                '''
            else:
                query = '''
                    SELECT d.*, dm.*
                    FROM documents d
                    LEFT JOIN document_metadata dm ON d.id = dm.document_id
                    ORDER BY d.created_at DESC
                    LIMIT 100
                '''

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            return [self._row_to_document_dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []

    def get_filter_options(self) -> Dict[str, List[str]]:
        """
        Get available options for each filter type

        Returns:
            Dictionary with filter options
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            filter_options = {}

            # Get unique values for each filter type
            filter_queries = {
                'judge': "SELECT DISTINCT judge FROM document_metadata WHERE judge IS NOT NULL AND judge != ''",
                'court': "SELECT DISTINCT court_name FROM document_metadata WHERE court_name IS NOT NULL AND court_name != ''",
                'case_type': "SELECT DISTINCT case_type FROM document_metadata WHERE case_type IS NOT NULL AND case_type != ''",
                'district': "SELECT DISTINCT district FROM document_metadata WHERE district IS NOT NULL AND district != ''",
                'year': "SELECT DISTINCT year FROM document_metadata WHERE year IS NOT NULL AND year != ''",
                'decision_type': "SELECT DISTINCT decision_type FROM document_metadata WHERE decision_type IS NOT NULL AND decision_type != ''"
            }

            for filter_type, query in filter_queries.items():
                cursor.execute(query)
                rows = cursor.fetchall()
                options = [row[0] for row in rows if row[0]]
                filter_options[filter_type] = sorted(options)

            conn.close()

            return filter_options

        except Exception as e:
            logger.error(f"Error getting filter options: {str(e)}")
            return {}

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the database

        Args:
            doc_id: Document ID to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Delete from both tables
            cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            cursor.execute("DELETE FROM document_metadata WHERE document_id = ?", (doc_id,))

            conn.commit()
            conn.close()

            # Update filter options cache
            self._update_filter_options()

            logger.info(f"Deleted document {doc_id} from database")
            return True

        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {str(e)}")
            return False

    def _generate_document_id(self, doc_data: Dict[str, Any]) -> str:
        """
        Generate a unique document ID

        Args:
            doc_data: Document data

        Returns:
            Unique document ID
        """
        # Use filename and timestamp to generate ID
        filename = doc_data.get('filename', 'unknown')
        timestamp = doc_data.get('processed_at', datetime.now().isoformat())

        # Create hash for uniqueness
        content = f"{filename}_{timestamp}".encode()
        doc_hash = hashlib.md5(content).hexdigest()[:12]

        return f"doc_{doc_hash}"

    def _row_to_document_dict(self, row) -> Dict[str, Any]:
        """
        Convert database row to document dictionary

        Args:
            row: Database row

        Returns:
            Document dictionary
        """
        try:
            # Column names from the query
            columns = [
                'id', 'filename', 'file_path', 'text_content', 'metadata', 'processed_at', 'status', 'created_at',
                'document_id', 'court_name', 'case_number', 'judge', 'case_type',
                'district', 'decision_type', 'year', 'applicant', 'parties', 'dates'
            ]

            doc_dict = {}
            for i, column in enumerate(columns):
                if i < len(row):
                    value = row[i]
                    if column in ['metadata', 'parties', 'dates']:
                        try:
                            doc_dict[column] = json.loads(value) if value else {}
                        except:
                            doc_dict[column] = {}
                    else:
                        doc_dict[column] = value

            # Merge metadata
            if 'metadata' not in doc_dict:
                doc_dict['metadata'] = {}

            # Add metadata fields
            metadata_fields = ['court_name', 'case_number', 'judge', 'case_type', 'district', 'decision_type', 'year', 'applicant']
            for field in metadata_fields:
                if field in doc_dict and doc_dict[field]:
                    doc_dict['metadata'][field] = doc_dict[field]

            if 'parties' in doc_dict and doc_dict['parties']:
                doc_dict['metadata']['parties'] = doc_dict['parties']

            if 'dates' in doc_dict and doc_dict['dates']:
                doc_dict['metadata']['dates'] = doc_dict['dates']

            return doc_dict

        except Exception as e:
            logger.error(f"Error converting row to dict: {str(e)}")
            return {}

    def _update_filter_options(self):
        """
        Update the filter options cache
        """
        try:
            filter_options = self.get_filter_options()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Update cache
            for filter_type, options in filter_options.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO filter_options (filter_type, options, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (filter_type, json.dumps(options)))

            conn.commit()
            conn.close()

            logger.info("Updated filter options cache")

        except Exception as e:
            logger.error(f"Error updating filter options: {str(e)}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics

        Returns:
            Dictionary with database statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM documents")
            total_docs = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM documents WHERE status = 'processed'")
            processed_docs = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM documents WHERE status = 'failed'")
            failed_docs = cursor.fetchone()[0]

            conn.close()

            return {
                'total_documents': total_docs,
                'processed_documents': processed_docs,
                'failed_documents': failed_docs,
                'database_path': self.db_path
            }

        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return {'error': str(e)}

    def optimize_database(self):
        """
        Optimize database performance
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Rebuild indexes
            cursor.execute("REINDEX;")

            # Vacuum database
            cursor.execute("VACUUM;")

            conn.commit()
            conn.close()

            logger.info("Database optimized successfully")

        except Exception as e:
            logger.error(f"Error optimizing database: {str(e)}")
