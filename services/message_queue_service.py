from typing import Dict, List
from datetime import datetime, timedelta
import time

class MessageQueueService:
    def __init__(self, message_window_seconds: int = 5):
        self.pending_messages: Dict[str, List[Dict]] = {}
        self.message_window_seconds = message_window_seconds
    
    def add_message(self, conversation_id: str, message: str):
        """Add a message to the pending queue."""
        if conversation_id not in self.pending_messages:
            self.pending_messages[conversation_id] = []
        
        self.pending_messages[conversation_id].append({
            "message": message,
            "timestamp": datetime.now()
        })
        
        # Remove messages older than the window
        self._cleanup_old_messages(conversation_id)
    
    def process_messages(self, conversation_id: str) -> str:
        """Process pending messages and return the final message to respond to."""
        if conversation_id not in self.pending_messages or not self.pending_messages[conversation_id]:
            return None
        
        # Wait a short time to collect potential sequential messages
        time.sleep(0.5)
        
        # Cleanup old messages again after waiting
        self._cleanup_old_messages(conversation_id)
        
        messages = self.pending_messages[conversation_id]
        if not messages:
            return None
        
        # Get the last message
        final_message = messages[-1]["message"]
        
        # Clear pending messages for this conversation
        self.pending_messages[conversation_id] = []
        
        return final_message
    
    def _cleanup_old_messages(self, conversation_id: str):
        """Remove messages older than the window."""
        if conversation_id not in self.pending_messages:
            return
        
        cutoff_time = datetime.now() - timedelta(seconds=self.message_window_seconds)
        self.pending_messages[conversation_id] = [
            msg for msg in self.pending_messages[conversation_id]
            if msg["timestamp"] > cutoff_time
        ] 