"""
Authentication Manager for Court Case Sorter
Handles user authentication and authorization
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import jwt
import bcrypt
from functools import wraps

logger = logging.getLogger(__name__)

class AuthManager:
    """Manages user authentication and authorization"""

    def __init__(self, secret_key: str = "your-secret-key-change-in-production"):
        """
        Initialize authentication manager

        Args:
            secret_key: JWT secret key
        """
        self.secret_key = secret_key
        self.algorithm = "HS256"

        # In-memory user storage (in production, use database)
        self.users = self._initialize_default_users()

    def _initialize_default_users(self) -> Dict[str, Dict[str, Any]]:
        """Initialize default users"""
        # Create default admin user
        admin_password = self._hash_password("admin123")
        return {
            "admin": {
                "id": 1,
                "username": "admin",
                "email": "admin@court.gov.az",
                "password_hash": admin_password,
                "is_admin": True,
                "created_at": datetime.now().isoformat()
            }
        }

    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def _generate_token(self, user: Dict[str, Any]) -> str:
        """Generate JWT token for user"""
        try:
            payload = {
                "user_id": user["id"],
                "username": user["username"],
                "is_admin": user["is_admin"],
                "exp": datetime.utcnow() + timedelta(days=1),  # Token expires in 1 day
                "iat": datetime.utcnow()
            }

            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token

        except Exception as e:
            logger.error(f"Error generating token: {str(e)}")
            raise

    def _verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return user data"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return None

    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """
        Authenticate a user

        Args:
            username: Username
            password: Password

        Returns:
            JWT token if authentication successful, None otherwise
        """
        try:
            user = self.users.get(username)
            if not user:
                logger.warning(f"User not found: {username}")
                return None

            if self._verify_password(password, user["password_hash"]):
                token = self._generate_token(user)
                logger.info(f"User {username} authenticated successfully")
                return token
            else:
                logger.warning(f"Invalid password for user: {username}")
                return None

        except Exception as e:
            logger.error(f"Error authenticating user {username}: {str(e)}")
            return None

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token

        Args:
            token: JWT token

        Returns:
            User data if token is valid, None otherwise
        """
        return self._verify_token(token)

    def create_user(self, username: str, email: str, password: str, is_admin: bool = False) -> bool:
        """
        Create a new user

        Args:
            username: Username
            email: Email address
            password: Password
            is_admin: Whether user is admin

        Returns:
            True if user created successfully, False otherwise
        """
        try:
            if username in self.users:
                logger.warning(f"User already exists: {username}")
                return False

            user = {
                "id": len(self.users) + 1,
                "username": username,
                "email": email,
                "password_hash": self._hash_password(password),
                "is_admin": is_admin,
                "created_at": datetime.now().isoformat()
            }

            self.users[username] = user
            logger.info(f"User created: {username}")
            return True

        except Exception as e:
            logger.error(f"Error creating user {username}: {str(e)}")
            return False

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user information

        Args:
            username: Username

        Returns:
            User data if found, None otherwise
        """
        return self.users.get(username)

    def update_user(self, username: str, updates: Dict[str, Any]) -> bool:
        """
        Update user information

        Args:
            username: Username
            updates: Dictionary of fields to update

        Returns:
            True if updated successfully, False otherwise
        """
        try:
            if username not in self.users:
                logger.warning(f"User not found: {username}")
                return False

            user = self.users[username]

            # Update allowed fields
            allowed_fields = ['email', 'is_admin']
            for field in allowed_fields:
                if field in updates:
                    user[field] = updates[field]

            logger.info(f"User updated: {username}")
            return True

        except Exception as e:
            logger.error(f"Error updating user {username}: {str(e)}")
            return False

    def delete_user(self, username: str) -> bool:
        """
        Delete a user

        Args:
            username: Username

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if username not in self.users:
                logger.warning(f"User not found: {username}")
                return False

            # Don't allow deleting the last admin user
            if self.users[username]["is_admin"]:
                admin_count = sum(1 for u in self.users.values() if u["is_admin"])
                if admin_count <= 1:
                    logger.warning("Cannot delete last admin user")
                    return False

            del self.users[username]
            logger.info(f"User deleted: {username}")
            return True

        except Exception as e:
            logger.error(f"Error deleting user {username}: {str(e)}")
            return False

    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Get all users

        Returns:
            List of all users
        """
        return list(self.users.values())

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Change user password

        Args:
            username: Username
            old_password: Current password
            new_password: New password

        Returns:
            True if password changed successfully, False otherwise
        """
        try:
            user = self.users.get(username)
            if not user:
                logger.warning(f"User not found: {username}")
                return False

            if not self._verify_password(old_password, user["password_hash"]):
                logger.warning(f"Invalid old password for user: {username}")
                return False

            user["password_hash"] = self._hash_password(new_password)
            logger.info(f"Password changed for user: {username}")
            return True

        except Exception as e:
            logger.error(f"Error changing password for user {username}: {str(e)}")
            return False

    def is_admin(self, token: str) -> bool:
        """
        Check if user is admin

        Args:
            token: JWT token

        Returns:
            True if user is admin, False otherwise
        """
        user_data = self._verify_token(token)
        return user_data and user_data.get("is_admin", False)

    def get_user_count(self) -> int:
        """
        Get total number of users

        Returns:
            Number of users
        """
        return len(self.users)

    def get_admin_count(self) -> int:
        """
        Get number of admin users

        Returns:
            Number of admin users
        """
        return sum(1 for user in self.users.values() if user["is_admin"])

    def reset_user_password(self, username: str, new_password: str) -> bool:
        """
        Reset user password (admin function)

        Args:
            username: Username
            new_password: New password

        Returns:
            True if password reset successfully, False otherwise
        """
        try:
            user = self.users.get(username)
            if not user:
                logger.warning(f"User not found: {username}")
                return False

            user["password_hash"] = self._hash_password(new_password)
            logger.info(f"Password reset for user: {username}")
            return True

        except Exception as e:
            logger.error(f"Error resetting password for user {username}: {str(e)}")
            return False

    def validate_token_format(self, token: str) -> bool:
        """
        Validate token format

        Args:
            token: JWT token

        Returns:
            True if token format is valid, False otherwise
        """
        try:
            # Basic format validation
            parts = token.split('.')
            if len(parts) != 3:
                return False

            # Try to decode without verification
            jwt.decode(token, options={"verify_signature": False})
            return True

        except:
            return False
