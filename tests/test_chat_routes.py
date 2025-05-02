import pytest
from fastapi.testclient import TestClient
from main import app
from services.conversation_service import ConversationService
import uuid
import asyncio
from datetime import datetime

client = TestClient(app)

def test_query_endpoint():
    response = client.post("/api/v1/query", json={"message": "Are there startups about wine in Chicago?"})
    assert response.status_code == 200
    assert "output" in response.json()
    assert "conversation_id" in response.json()
    
    conversation_id = response.json()["conversation_id"]
    
    response = client.post("/api/v1/query", json={
        "message": "And in NY?",
        "conversation_id": conversation_id
    })
    assert response.status_code == 200
    assert "output" in response.json()
    assert response.json()["conversation_id"] == conversation_id

def test_summarize_endpoint():
    response = client.post("/api/v1/query", json={"message": "Are there startups about wine in Chicago?"})
    conversation_id = response.json()["conversation_id"]
    
    response = client.post("/api/v1/summarize", json={"conversation_id": conversation_id})
    assert response.status_code == 200
    assert "summary" in response.json()
    assert isinstance(response.json()["summary"], str)
    
    response = client.post("/api/v1/summarize", json={})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_conversation_service():
    service = ConversationService()
    conversation_id = str(uuid.uuid4())
    message_time = datetime.now()
    await service.add_message(conversation_id, "user", "Hello", message_time)
    await service.add_message(conversation_id, "assistant", "Hi there!", message_time)
    
    messages = await service.get_context_messages(conversation_id, message_time)
    assert len(messages) == 2
    
    summary = await service.get_summary(conversation_id, message_time)
    assert isinstance(summary, str)
    
    messages = await service.get_context_messages(str(uuid.uuid4()), message_time)
    assert len(messages) == 0