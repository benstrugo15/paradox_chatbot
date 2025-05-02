from fastapi import Depends
from services.chatbot_service import Chatbot
from services.neural_search_service import NeuralSearcher
from services.conversation_service import ConversationService
from services.request_handler import RequestHandler
from config import OPENAI_KEY, QDRANT_URL, MODEL_NAME

# Create singleton instances
_chatbot = Chatbot()
_neural_searcher = NeuralSearcher(collection_name="startups")
_conversation_service = ConversationService()
_request_handler = RequestHandler()

def get_chatbot() -> Chatbot:
    return _chatbot

def get_neural_searcher() -> NeuralSearcher:
    return _neural_searcher

def get_conversation_service() -> ConversationService:
    return _conversation_service

def get_request_handler() -> RequestHandler:
    return _request_handler 