"""
Stub AI Bot for initial setup
Provides basic functionality without heavy ML dependencies
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class AIBot:
    """Stub AI bot for initial testing"""

    def __init__(self):
        """Initialize stub AI bot"""
        self.responses = {
            "default": "Azərbaycan məhkəmə sisteminin sənədləri üzrə kömək edə bilərəm. Sualınızı soruşun.",
            "search_help": "Axtarış üçün hakimin adı, məhkəmənin adı və ya iş növünü daxil edin.",
            "no_results": "Təəssüf ki, axtarış nəticəsində heç bir sənəd tapılmadı."
        }
        logger.info("AI Bot initialized in stub mode")

    def chat(self, message: str) -> str:
        """Simple chat response without ML"""
        try:
            message_lower = message.lower()
            
            # Simple keyword-based responses
            if any(greeting in message_lower for greeting in ['salam', 'hello', 'salam alaikum']):
                return "Salam! Məhkəmə sənədləri ilə bağlı kömək edə bilərəm."
            
            elif 'axtarış' in message_lower or 'search' in message_lower:
                return self.responses["search_help"]
            
            elif 'hakim' in message_lower:
                return "Hakimin adına görə axtarış aparın. Axtarış sahəsinə hakimin tam adını daxil edin."
                
            elif 'məhkəmə' in message_lower:
                return "Məhkəmənin adına görə axtarış üçün məhkəmənin tam adını yazın."
                
            else:
                return self.responses["default"]
                
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return "Üzr istəyirik, texniki problem yaşandı. Yenidən cəhd edin."

    def search_documents(self, query: str) -> List[Dict[str, Any]]:
        """Simple document search without ML"""
        try:
            # This would integrate with the database for actual search
            # For now, return placeholder
            return []
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []