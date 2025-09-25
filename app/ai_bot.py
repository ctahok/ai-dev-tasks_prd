"""
AI Bot for Court Document Queries
Handles natural language queries in Azerbaijani and English
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AIBot:
    """AI bot for processing natural language queries about court documents"""

    def __init__(self):
        # Azerbaijani language patterns and responses
        self.azerbaijani_patterns = {
            'greetings': [
                r'salam', r'hello', r'hi', r'hey',
                r'xaış', r'günaydın', r'axşamınız xeyir'
            ],
            'judge_queries': [
                r'(.*?)hakim(.*?)',
                r'(.*?)qərar(.*?)vermiş',
                r'(.*?)çıxarmış',
                r'(.*?)qətnamə'
            ],
            'court_queries': [
                r'(.*?)məhkəmə',
                r'(.*?)rayon',
                r'(.*?)şəhər'
            ],
            'case_type_queries': [
                r'(.*?)işin növü',
                r'(.*?)mülki',
                r'(.*?)inzibati',
                r'(.*?)kommersiya'
            ],
            'year_queries': [
                r'(\d{4})',
                r'ili?',
                r'tarix'
            ]
        }

        # Common Azerbaijani legal terms
        self.legal_terms = {
            'hakim': 'judge',
            'məhkəmə': 'court',
            'qərar': 'decision',
            'qətnamə': 'resolution',
            'inzibati': 'administrative',
            'mülki': 'civil',
            'kommersiya': 'commercial',
            'rayon': 'district',
            'şəhər': 'city',
            'il': 'year',
            'tarix': 'date',
            'ərizəçi': 'applicant',
            'cavabdeh': 'defendant',
            'iddiaçı': 'plaintiff'
        }

        # Response templates in Azerbaijani
        self.responses = {
            'greeting': [
                'Salam! Mən məhkəmə sənədləri üzrə köməkçi AI botam.',
                'Salam! Məhkəmə işləri haqqında suallarınızı cavablandıra bilərəm.',
                'Salam! Hansı məhkəmə sənədi ilə bağlı köməyə ehtiyacınız var?'
            ],
            'clarification': [
                'Zəhmət olmasa, axtarışınızı daha dəqiq edin.',
                'Daha çox detal verə bilərsinizmi?',
                'Hansı hakim, məhkəmə və ya il sizi maraqlandırır?'
            ],
            'no_results': [
                'Təəssüf ki, bu meyarlara uyğun sənəd tapılmadı.',
                'Axtarışınız üçün uyğun nəticə yoxdur.',
                'Başqa meyarlarla yenidən cəhd edin.'
            ],
            'found_results': [
                'Sizin üçün {} uyğun sənəd tapdım.',
                'Axtarışınıza {} nəticə uyğun gəlir.',
                'Budur, axtardığınız sənədlər:'
            ]
        }

    def chat(self, message: str) -> str:
        """
        Process a chat message and return a response

        Args:
            message: User message

        Returns:
            Bot response
        """
        try:
            # Normalize message
            message = message.lower().strip()

            # Check for greetings
            if self._is_greeting(message):
                return self._get_random_response('greeting')

            # Analyze query and extract search criteria
            search_criteria = self._analyze_query(message)

            if search_criteria:
                # Perform search
                results = self._perform_search(search_criteria)

                if results:
                    return self._format_results_response(results, len(results))
                else:
                    return self._get_random_response('no_results')
            else:
                return self._get_random_response('clarification')

        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            return "Bağışlayın, xəta baş verdi. Zəhmət olmasa, yenidən cəhd edin."

    def search_documents(self, query: str) -> List[Dict[str, Any]]:
        """
        Search documents based on natural language query

        Args:
            query: Natural language query

        Returns:
            List of relevant documents
        """
        try:
            # Analyze the query
            search_criteria = self._analyze_query(query)

            if search_criteria:
                return self._perform_search(search_criteria)
            else:
                return []

        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []

    def _is_greeting(self, message: str) -> bool:
        """Check if message is a greeting"""
        for pattern in self.azerbaijani_patterns['greetings']:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        return False

    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze natural language query and extract search criteria

        Args:
            query: User query

        Returns:
            Dictionary of search criteria
        """
        criteria = {}

        try:
            # Extract judge information
            judge_match = self._extract_judge_info(query)
            if judge_match:
                criteria['judge'] = judge_match

            # Extract court information
            court_match = self._extract_court_info(query)
            if court_match:
                criteria['court'] = court_match

            # Extract case type
            case_type_match = self._extract_case_type(query)
            if case_type_match:
                criteria['case_type'] = case_type_match

            # Extract year
            year_match = self._extract_year(query)
            if year_match:
                criteria['year'] = year_match

            # Extract district
            district_match = self._extract_district(query)
            if district_match:
                criteria['district'] = district_match

            # If no specific criteria found, treat as general search
            if not criteria:
                criteria['general_search'] = query

        except Exception as e:
            logger.error(f"Error analyzing query: {str(e)}")

        return criteria

    def _extract_judge_info(self, query: str) -> Optional[str]:
        """Extract judge information from query"""
        # Look for judge names (Azerbaijani names typically end with common suffixes)
        judge_patterns = [
            r'([A-ZƏÜÖĞÇŞİ][a-zəüöğçşı̇]+ [A-ZƏÜÖĞÇŞİ][a-zəüöğçşı̇]+)',
            r'([A-ZƏÜÖĞÇŞİ][a-zəüöğçşı̇]+)',
        ]

        for pattern in judge_patterns:
            match = re.search(pattern, query)
            if match:
                judge_name = match.group(1).strip()
                # Validate it's likely a judge name (not too short, not a common word)
                if len(judge_name) > 5 and judge_name not in ['məhkəmə', 'qərar', 'hakim']:
                    return judge_name

        return None

    def _extract_court_info(self, query: str) -> Optional[str]:
        """Extract court information from query"""
        court_keywords = [
            'ağdam', 'şirvan', 'bakı', 'gəncə', 'sumqayıt', 'mingəçevir',
            'apellyasiya', 'inzibati', 'kommersiya', 'rayon'
        ]

        for keyword in court_keywords:
            if keyword in query:
                return keyword

        return None

    def _extract_case_type(self, query: str) -> Optional[str]:
        """Extract case type from query"""
        case_types = {
            'mülki': 'civil',
            'inzibati': 'administrative',
            'kommersiya': 'commercial',
            'cinayət': 'criminal'
        }

        for az_type, en_type in case_types.items():
            if az_type in query:
                return az_type

        return None

    def _extract_year(self, query: str) -> Optional[str]:
        """Extract year from query"""
        year_pattern = r'(\d{4})'
        match = re.search(year_pattern, query)
        if match:
            return match.group(1)

        return None

    def _extract_district(self, query: str) -> Optional[str]:
        """Extract district information from query"""
        district_keywords = [
            'ağdam', 'şirvan', 'bakı', 'gəncə', 'sumqayıt', 'mingəçevir',
            'quzanlı', 'sarıcalı', 'çəmənli'
        ]

        for keyword in district_keywords:
            if keyword in query:
                return keyword

        return None

    def _perform_search(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Perform search based on criteria

        Args:
            criteria: Search criteria

        Returns:
            List of matching documents
        """
        try:
            # Import database manager here to avoid circular imports
            from app.database import DatabaseManager

            db_manager = DatabaseManager()

            if 'general_search' in criteria:
                # For general search, we would use the RAG system
                # For now, return empty list as placeholder
                return []
            else:
                # Use structured search
                return db_manager.search_documents(criteria)

        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            return []

    def _format_results_response(self, results: List[Dict[str, Any]], count: int) -> str:
        """
        Format search results into a response

        Args:
            results: Search results
            count: Number of results

        Returns:
            Formatted response string
        """
        try:
            if count == 0:
                return self._get_random_response('no_results')

            response = self._get_random_response('found_results').format(count)
            response += "\n\n"

            # Add brief information about top results
            for i, result in enumerate(results[:3]):  # Show top 3 results
                metadata = result.get('metadata', {})

                response += f"{i+1}. {metadata.get('case_number', 'Unknown')} - "
                response += f"{metadata.get('court_name', 'Unknown Court')} - "
                response += f"{metadata.get('judge', 'Unknown Judge')}\n"

            if count > 3:
                response += f"\n... və daha {count - 3} sənəd tapıldı."

            return response

        except Exception as e:
            logger.error(f"Error formatting results: {str(e)}")
            return self._get_random_response('found_results').format(count)

    def _get_random_response(self, response_type: str) -> str:
        """
        Get a random response from the available options

        Args:
            response_type: Type of response to get

        Returns:
            Random response string
        """
        import random

        responses = self.responses.get(response_type, ['Bağışlayın, cavab tapa bilmirəm.'])
        return random.choice(responses)

    def translate_legal_terms(self, text: str) -> str:
        """
        Translate legal terms between Azerbaijani and English

        Args:
            text: Text to translate

        Returns:
            Translated text
        """
        translated = text.lower()

        for az_term, en_term in self.legal_terms.items():
            translated = re.sub(r'\b' + az_term + r'\b', en_term, translated, flags=re.IGNORECASE)

        return translated

    def get_query_suggestions(self, partial_query: str) -> List[str]:
        """
        Get query suggestions based on partial input

        Args:
            partial_query: Partial query string

        Returns:
            List of suggested queries
        """
        suggestions = [
            'Hakim Fikrət Hüseynovun qərarları',
            'Ağdam rayon məhkəməsinin 2025-ci il qərarları',
            'Mülki işlər üzrə qətnamələr',
            'Şirvan Apellyasiya Məhkəməsinin inzibati işləri',
            '2024-cü il kommersiya məhkəmə qərarları'
        ]

        # Filter suggestions based on partial query
        if partial_query:
            filtered = [s for s in suggestions if partial_query.lower() in s.lower()]
            return filtered[:5]

        return suggestions[:5]

    def validate_query(self, query: str) -> Dict[str, Any]:
        """
        Validate and analyze a query

        Args:
            query: Query to validate

        Returns:
            Validation results
        """
        validation = {
            'is_valid': True,
            'has_judge': False,
            'has_court': False,
            'has_year': False,
            'has_case_type': False,
            'suggestions': []
        }

        try:
            # Check for required elements
            if len(query.strip()) < 3:
                validation['is_valid'] = False
                return validation

            # Analyze query components
            criteria = self._analyze_query(query)

            if 'judge' in criteria:
                validation['has_judge'] = True

            if 'court' in criteria:
                validation['has_court'] = True

            if 'year' in criteria:
                validation['has_year'] = True

            if 'case_type' in criteria:
                validation['has_case_type'] = True

            # Get suggestions
            validation['suggestions'] = self.get_query_suggestions(query)

        except Exception as e:
            logger.error(f"Error validating query: {str(e)}")
            validation['is_valid'] = False

        return validation
