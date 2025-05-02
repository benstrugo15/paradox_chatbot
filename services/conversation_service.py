from typing import Dict, List, Optional
from openai import OpenAI
from config import OPENAI_KEY
import asyncio
from exceptions import ConversationNotFoundError, ServiceUnavailableError, ValidationError
import logging
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Conversation:
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        self.messages: List[Dict] = []
        self.lock = asyncio.Lock()
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()

    def add_message(self, role: str, content: str):
        if not role or not content:
            raise ValidationError("Role and content cannot be empty")
        
        if role not in ["user", "assistant"]:
            raise ValidationError("Invalid role. Must be 'user' or 'assistant'")
        
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > 10:
            self.messages = self.messages[-10:]
        
        self.last_accessed = datetime.now()

    def get_last_messages(self, count: int = 5) -> List[Dict]:
        if count <= 0:
            raise ValidationError("Count must be positive")
        return self.messages[-count:]

class ConversationService:
    def __init__(self, max_conversations: int = 1000, max_age_hours: int = 24):
        self.conversations: Dict[str, Conversation] = {}
        self.client = OpenAI(api_key=OPENAI_KEY)
        self.lock = asyncio.Lock()
        self.max_conversations = max_conversations
        self.max_age_hours = max_age_hours

    async def get_conversation(self, conversation_id: str) -> Conversation:
        async with self.lock:
            if conversation_id not in self.conversations:
                raise ConversationNotFoundError(conversation_id)
            return self.conversations[conversation_id]

    async def _cleanup_old_conversations(self):
        cutoff_time = datetime.now() - timedelta(hours=self.max_age_hours)
        self.conversations = {
            conv_id: conv for conv_id, conv in self.conversations.items()
            if conv.last_accessed > cutoff_time
        }

    async def add_message(self, conversation_id: str, role: str, content: str):
        try:
            await self._cleanup_old_conversations()
            
            if len(self.conversations) >= self.max_conversations:
                raise ServiceUnavailableError("conversation", "Maximum number of conversations reached")
            
            conversation = await self.get_conversation(conversation_id)
            async with conversation.lock:
                conversation.add_message(role, content)
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            raise

    async def get_last_messages(self, conversation_id: str, count: int = 5) -> List[Dict]:
        try:
            conversation = await self.get_conversation(conversation_id)
            async with conversation.lock:
                return conversation.get_last_messages(count)
        except Exception as e:
            logger.error(f"Error getting last messages: {str(e)}")
            raise

    async def get_summary(self, conversation_id: str) -> str:
        try:
            conversation = await self.get_conversation(conversation_id)
            async with conversation.lock:
                if not conversation.messages:
                    return "No conversation history available."
                
                formatted_messages = "\n".join([
                    f"{msg['role']}: {msg['content']}"
                    for msg in conversation.messages
                ])
                
                try:
                    completion = self.client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that summarizes conversations. Provide a concise summary of the conversation in a single paragraph."},
                            {"role": "user", "content": f"Please summarize this conversation:\n\n{formatted_messages}"}
                        ]
                    )
                    
                    return completion.choices[0].message.content
                except Exception as e:
                    logger.error(f"OpenAI API error: {str(e)}")
                    raise ServiceUnavailableError("OpenAI", "Failed to generate summary")
        except Exception as e:
            logger.error(f"Error getting summary: {str(e)}")
            raise 