import pytest
from services.chatbot_service import Chatbot
from unittest.mock import Mock, patch
import json
from openai.types.chat import ChatCompletion, ChatCompletionMessage

@pytest.fixture
def chatbot():
    return Chatbot()

@pytest.fixture
def mock_openai_response():
    return ChatCompletion(
        id="test-id",
        object="chat.completion",
        created=1234567890,
        model="gpt-4",
        choices=[
            {
                "index": 0,
                "message": ChatCompletionMessage(
                    role="assistant",
                    content=json.dumps({"answer": "Test answer"})
                ),
                "finish_reason": "stop"
            }
        ]
    )

def test_search_without_context(chatbot, mock_openai_response):
    with patch.object(chatbot.client.chat.completions, 'create', return_value=mock_openai_response):
        data = [{"name": "Test Startup", "city": "Chicago", "description": "A test startup"}]
        response = chatbot.search(data, "What startups are in Chicago?")
        assert response == "Test answer"

def test_search_with_context(chatbot, mock_openai_response):
    with patch.object(chatbot.client.chat.completions, 'create', return_value=mock_openai_response):
        data = [{"name": "Test Startup", "city": "Chicago", "description": "A test startup"}]
        context_messages = [
            {"role": "user", "content": "What startups are in Chicago?"},
            {"role": "assistant", "content": "There is Test Startup in Chicago"}
        ]
        response = chatbot.search(data, "And in New York?", context_messages)
        assert response == "Test answer"

def test_is_follow_up_question_with_indicators(chatbot):
    context_messages = [
        {"role": "user", "content": "What startups are in Chicago?"},
        {"role": "assistant", "content": "There is Test Startup in Chicago"}
    ]
    
    # Test with different follow-up indicators
    follow_up_messages = [
        "And in New York?",
        "What about New York?",
        "How about New York?",
        "Also in New York?",
        "In addition to Chicago, what about New York?"
    ]
    
    for message in follow_up_messages:
        assert chatbot._is_follow_up_question(message, context_messages)

def test_is_follow_up_question_without_indicators(chatbot):
    context_messages = [
        {"role": "user", "content": "What startups are in Chicago?"},
        {"role": "assistant", "content": "There is Test Startup in Chicago"}
    ]
    
    # Test with non-follow-up messages
    non_follow_up_messages = [
        "Tell me about startups",
        "What's the weather like?",
        "List all startups"
    ]
    
    for message in non_follow_up_messages:
        assert not chatbot._is_follow_up_question(message, context_messages)

def test_build_system_prompt(chatbot):
    data = [
        {"name": "Startup1", "city": "Chicago", "description": "First startup"},
        {"name": "Startup2", "city": "New York", "description": "Second startup"}
    ]
    
    prompt = chatbot._build_system_prompt(data)
    
    assert "Startup1" in prompt
    assert "Chicago" in prompt
    assert "First startup" in prompt
    assert "Startup2" in prompt
    assert "New York" in prompt
    assert "Second startup" in prompt
    assert "You are a Q&A chatbot" in prompt
    assert "JSON format" in prompt 