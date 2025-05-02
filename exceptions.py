from fastapi import HTTPException, status
from typing import Optional

class ChatbotException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class ConversationNotFoundError(ChatbotException):
    def __init__(self, conversation_id: str):
        super().__init__(
            f"Conversation with ID {conversation_id} not found",
            status.HTTP_404_NOT_FOUND
        )

class InvalidMessageError(ChatbotException):
    def __init__(self, message: str = "Invalid message format"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)

class RateLimitError(ChatbotException):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS)

class ServiceUnavailableError(ChatbotException):
    def __init__(self, service: str, message: Optional[str] = None):
        msg = message or f"{service} service is currently unavailable"
        super().__init__(msg, status.HTTP_503_SERVICE_UNAVAILABLE)

class ValidationError(ChatbotException):
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY) 