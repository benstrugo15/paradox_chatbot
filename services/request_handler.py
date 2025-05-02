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
        self.rate_limits: Dict[str, Dict] = {}
        self.max_requests_per_minute = max_requests_per_minute

    def _check_rate_limit(self, conversation_id: str):
        now = datetime.now()
        if conversation_id not in self.rate_limits:
            self.rate_limits[conversation_id] = {
                "requests": [],
                "last_cleanup": now
            }

        cutoff_time = now - timedelta(minutes=1)
        self.rate_limits[conversation_id]["requests"] = [
            req_time for req_time in self.rate_limits[conversation_id]["requests"]
            if req_time > cutoff_time
        ]

        if len(self.rate_limits[conversation_id]["requests"]) >= self.max_requests_per_minute:
            raise RateLimitError()

        self.rate_limits[conversation_id]["requests"].append(now)

    async def process_request(self, conversation_id: Optional[str], message: str) -> tuple[str, str]:
        if not message or not isinstance(message, str):
            raise InvalidMessageError()

        conversation_id = conversation_id or str(uuid.uuid4())
        self._check_rate_limit(conversation_id)

        try:
            self._add_request(conversation_id, message)
            return conversation_id, message
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
            "timestamp": datetime.now(),
            "sequence": len(self.pending_requests[conversation_id]["messages"])
        })

        self._cleanup_old_messages(conversation_id)

    def _cleanup_old_messages(self, conversation_id: str):
        if conversation_id not in self.pending_requests:
            return

        cutoff_time = datetime.now() - timedelta(seconds=self.message_window_seconds)
        self.pending_requests[conversation_id]["messages"] = [
            msg for msg in self.pending_requests[conversation_id]["messages"]
            if msg["timestamp"] > cutoff_time
        ]

    async def is_last_message(self, conversation_id: str) -> bool:
        if conversation_id not in self.pending_requests:
            return True

        # Wait for a short time to allow other messages to arrive
        await asyncio.sleep(0.5)

        # Check if any new messages arrived during the wait
        if conversation_id not in self.pending_requests:
            return True

        # Get the latest message timestamp
        latest_timestamp = max(
            msg["timestamp"] for msg in self.pending_requests[conversation_id]["messages"]
        )

        # Wait a bit more to be sure no more messages are coming
        await asyncio.sleep(0.5)

        # Check if any newer messages arrived
        if conversation_id not in self.pending_requests:
            return True

        current_latest = max(
            msg["timestamp"] for msg in self.pending_requests[conversation_id]["messages"]
        )

        # If the latest message hasn't changed, this is the last message
        return current_latest == latest_timestamp
