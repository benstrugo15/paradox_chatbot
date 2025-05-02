from typing import Dict, Optional
import asyncio
from datetime import datetime, timedelta
import uuid
from exceptions import InvalidMessageError, RateLimitError
import logging

logger = logging.getLogger(__name__)

class RequestHandler:
    def __init__(self, message_window_seconds: int = 5, max_requests_per_minute: int = 60):
        self.pending_requests: Dict[str, Dict] = {}
        self.message_window_seconds = message_window_seconds
        self.locks: Dict[str, asyncio.Lock] = {}
        self.rate_limits: Dict[str, Dict] = {}
        self.max_requests_per_minute = max_requests_per_minute

    async def get_lock(self, conversation_id: str) -> asyncio.Lock:
        if conversation_id not in self.locks:
            self.locks[conversation_id] = asyncio.Lock()
        return self.locks[conversation_id]

    def _check_rate_limit(self, conversation_id: str):
        now = datetime.now()
        if conversation_id not in self.rate_limits:
            self.rate_limits[conversation_id] = {
                "requests": [],
                "last_cleanup": now
            }
        
        # Cleanup old requests
        cutoff_time = now - timedelta(minutes=1)
        self.rate_limits[conversation_id]["requests"] = [
            req_time for req_time in self.rate_limits[conversation_id]["requests"]
            if req_time > cutoff_time
        ]
        
        # Check rate limit
        if len(self.rate_limits[conversation_id]["requests"]) >= self.max_requests_per_minute:
            raise RateLimitError()
        
        self.rate_limits[conversation_id]["requests"].append(now)

    async def process_request(self, conversation_id: Optional[str], message: str) -> tuple[str, str]:
        if not message or not isinstance(message, str):
            raise InvalidMessageError()
        
        conversation_id = conversation_id or str(uuid.uuid4())
        self._check_rate_limit(conversation_id)
        
        try:
            async with await self.get_lock(conversation_id):
                self._add_request(conversation_id, message)
                await asyncio.sleep(0.5)
                final_message = self._get_final_message(conversation_id)
                if not final_message:
                    raise InvalidMessageError("No valid message to process")
                return conversation_id, final_message
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            raise

    def _add_request(self, conversation_id: str, message: str):
        if not message.strip():
            raise InvalidMessageError("Message cannot be empty")
        
        if conversation_id not in self.pending_requests:
            self.pending_requests[conversation_id] = {
                "messages": [],
                "last_updated": datetime.now()
            }
        
        self.pending_requests[conversation_id]["messages"].append({
            "message": message,
            "timestamp": datetime.now()
        })
        
        self._cleanup_old_messages(conversation_id)

    def _get_final_message(self, conversation_id: str) -> str:
        if conversation_id not in self.pending_requests:
            return None
        
        messages = self.pending_requests[conversation_id]["messages"]
        if not messages:
            return None
        
        final_message = messages[-1]["message"]
        self.pending_requests[conversation_id]["messages"] = []
        return final_message

    def _cleanup_old_messages(self, conversation_id: str):
        if conversation_id not in self.pending_requests:
            return
        
        cutoff_time = datetime.now() - timedelta(seconds=self.message_window_seconds)
        self.pending_requests[conversation_id]["messages"] = [
            msg for msg in self.pending_requests[conversation_id]["messages"]
            if msg["timestamp"] > cutoff_time
        ] 