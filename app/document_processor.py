"""
Document Processor for Azerbaijani Court Documents
Extracts metadata and content from PDF court documents
"""

import pdfplumber
import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Processes Azerbaijani court documents and extracts metadata"""

    def __init__(self):
        # Azerbaijani text patterns for key information
        self.patterns = {
            'court_name': r'Məhkəmənin adı[:\s]*([^\n\r]+)',
            'case_number': r'İş\s+No[:\s]*([^\n\r]+)',
            'judge': r'Hakim[:\s]*([^\n\r]+)',
            'clerk': r'Katib[:\s]*([^\n\r]+)',
            'applicant': r'Ərizəçi[:\s]*([^\n\r]+)',
            'case_type': r'İşin növü[:\s]*([^\n\r]+)',
            'court_act': r'Məhkəmə aktı[:\s]*([^\n\r]+)',
            'district': r'Rayon[:\s]*([^\n\r]+)',
            'decision_type': r'(QƏTNAMƏ|QƏRAR|QƏRARNAMƏ)',
            'decision_text': r'Qətetdi[:\s]*(.+?)(?=Azərbaycan Respublikası|$)',
            'year': r'(\d{4})',
            'date': r'(\d{1,2}[.\s]+\d{1,2}[.\s]+\d{4})'
        }

        # Common Azerbaijani court names
        self.court_names = [
            'AĞDAM RAYON MƏHKƏMƏSİ',
            'ŞİRVAN APELİYYASİYA MƏHKƏMƏSİ',
            'ŞİRVAN İNZİBATİ MƏHKƏMƏSİ',
            'ŞİRVAN KOMMERSİYA MƏHKƏMƏSİ'
        ]

    def process_document(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Process a PDF document and extract metadata

        Args:
            file_path: Path to the PDF file

        Returns:
            Dictionary containing extracted metadata and content
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None

            # Extract text from PDF
            text = self._extract_text_from_pdf(file_path)
            if not text:
                logger.warning(f"No text extracted from {file_path}")
                return None

            # Extract metadata
            metadata = self._extract_metadata(text)

            # Create document data structure
            doc_data = {
                'file_path': file_path,
                'filename': os.path.basename(file_path),
                'processed_at': datetime.now().isoformat(),
                'text_content': text,
                'metadata': metadata,
                'status': 'processed'
            }

            logger.info(f"Successfully processed document: {file_path}")
            return doc_data

        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            return None

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text content from PDF file"""
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            return text.strip()

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return ""

    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata from document text"""
        metadata = {}

        try:
            # Extract basic information using regex patterns
            for field, pattern in self.patterns.items():
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                if match:
                    value = match.group(1).strip()
                    if field == 'decision_text':
                        # For decision text, get more content
                        value = self._clean_decision_text(value)
                    metadata[field] = value

            # Extract court information
            metadata['court_info'] = self._extract_court_info(text)

            # Extract parties involved
            metadata['parties'] = self._extract_parties(text)

            # Extract dates
            metadata['dates'] = self._extract_dates(text)

            # Clean and normalize metadata
            metadata = self._clean_metadata(metadata)

        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")

        return metadata

    def _extract_court_info(self, text: str) -> Dict[str, str]:
        """Extract court-specific information"""
        court_info = {}

        # Find court name
        for court_name in self.court_names:
            if court_name in text:
                court_info['court_name'] = court_name
                break

        # Extract location/venue
        venue_pattern = r'([A-ZƏÜÖĞÇŞİ]+)\s*(rayon|şəhər|qəsəbə)'
        match = re.search(venue_pattern, text, re.IGNORECASE)
        if match:
            court_info['venue'] = match.group(0)

        return court_info

    def _extract_parties(self, text: str) -> List[str]:
        """Extract parties involved in the case"""
        parties = []

        # Look for plaintiff/defendant patterns
        plaintiff_patterns = [
            r'İddiaçı[:\s]*([^\n\r]+)',
            r'Ərizəçi[:\s]*([^\n\r]+)',
            r'Məhkum[:\s]*([^\n\r]+)'
        ]

        defendant_patterns = [
            r'Cavabdeh[:\s]*([^\n\r]+)',
            r'Təqsirləndirilən[:\s]*([^\n\r]+)'
        ]

        for pattern in plaintiff_patterns + defendant_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                party = match.strip()
                if party and len(party) > 3:  # Filter out very short matches
                    parties.append(party)

        return list(set(parties))  # Remove duplicates

    def _extract_dates(self, text: str) -> Dict[str, str]:
        """Extract important dates from the document"""
        dates = {}

        # Look for various date formats
        date_patterns = [
            (r'(\d{1,2})[.\s]+(\d{1,2})[.\s]+(\d{4})', 'dd_mm_yyyy'),
            (r'(\d{4})[.\s]+(\d{1,2})[.\s]+(\d{1,2})', 'yyyy_mm_dd'),
            (r'(\d{1,2})[.\s]+([A-Za-zƏÜÖĞÇŞİ]+)[.\s]+(\d{4})', 'dd_month_yyyy')
        ]

        for pattern, format_type in date_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    if format_type == 'dd_mm_yyyy':
                        day, month, year = match
                        date_str = f"{day.zfill(2)}.{month.zfill(2)}.{year}"
                    elif format_type == 'yyyy_mm_dd':
                        year, month, day = match
                        date_str = f"{day.zfill(2)}.{month.zfill(2)}.{year}"
                    else:  # dd_month_yyyy
                        day, month, year = match
                        date_str = f"{day.zfill(2)}.{month}.{year}"

                    dates[format_type] = date_str
                except:
                    continue

        return dates

    def _clean_decision_text(self, text: str) -> str:
        """Clean and format decision text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove common artifacts
        text = re.sub(r'[X\d]+\s*', '', text)  # Remove anonymized placeholders

        return text.strip()

    def _clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize extracted metadata"""
        cleaned = {}

        for key, value in metadata.items():
            if isinstance(value, str):
                # Remove extra whitespace
                cleaned_value = ' '.join(value.split())

                # Remove common artifacts
                cleaned_value = re.sub(r'^[:\s]*', '', cleaned_value)
                cleaned_value = re.sub(r'[:\s]*$', '', cleaned_value)

                # Skip if too short or empty
                if len(cleaned_value) > 2:
                    cleaned[key] = cleaned_value
            else:
                cleaned[key] = value

        return cleaned

    def validate_document(self, doc_data: Dict[str, Any]) -> bool:
        """Validate that the document contains required information"""
        if not doc_data or 'metadata' not in doc_data:
            return False

        metadata = doc_data['metadata']

        # Check for essential fields
        essential_fields = ['court_name', 'case_number', 'judge']
        return any(field in metadata for field in essential_fields)

    def get_processing_stats(self) -> Dict[str, int]:
        """Get processing statistics"""
        return {
            'total_processed': 0,  # Would be tracked in a real implementation
            'successful': 0,
            'failed': 0
        }
