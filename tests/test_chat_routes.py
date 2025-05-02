import pytest
from fastapi.testclient import TestClient
from main import app
from services.conversation_service import ConversationService
from services.message_queue_service import MessageQueueService
import uuid

client = TestClient(app)

def test_query_endpoint():
    # Test without conversation_id
    response = client.post("/api/v1/query", json={"message": "Are there startups about wine in Chicago?"})
    assert response.status_code == 200
    assert "output" in response.json()
    assert "conversation_id" in response.json()
    
    conversation_id = response.json()["conversation_id"]
    
    # Test with conversation_id
    response = client.post("/api/v1/query", json={
        "message": "And in NY?",
        "conversation_id": conversation_id
    })
    assert response.status_code == 200
    assert "output" in response.json()
    assert response.json()["conversation_id"] == conversation_id

def test_summarize_endpoint():
    # First create a conversation
    response = client.post("/api/v1/query", json={"message": "Are there startups about wine in Chicago?"})
    conversation_id = response.json()["conversation_id"]
    
    # Test summarize
    response = client.post("/api/v1/summarize", json={"conversation_id": conversation_id})
    assert response.status_code == 200
    assert "summary" in response.json()
    assert isinstance(response.json()["summary"], str)
    
    # Test with invalid conversation_id
    response = client.post("/api/v1/summarize", json={"conversation_id": str(uuid.uuid4())})
    assert response.status_code == 400

def test_message_queue():
    message_queue = MessageQueueService()
    conversation_id = str(uuid.uuid4())
    
    # Test adding messages
    message_queue.add_message(conversation_id, "First message")
    message_queue.add_message(conversation_id, "Second message")
    
    # Test processing messages
    final_message = message_queue.process_messages(conversation_id)
    assert final_message == "Second message"
    
    # Test empty queue
    final_message = message_queue.process_messages(conversation_id)
    assert final_message is None

def test_conversation_service():
    service = ConversationService()
    conversation_id = str(uuid.uuid4())
    
    # Test adding messages
    service.add_message(conversation_id, "user", "Hello")
    service.add_message(conversation_id, "assistant", "Hi there!")
    
    # Test getting last messages
    messages = service.get_last_messages(conversation_id)
    assert len(messages) == 2
    
    # Test getting summary
    summary = service.get_summary(conversation_id)
    assert isinstance(summary, str)
    
    # Test with invalid conversation_id
    messages = service.get_last_messages(str(uuid.uuid4()))
    assert len(messages) == 0 