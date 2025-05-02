import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app

client = TestClient(app)

@patch('services.neural_search_service.NeuralSearcher')
@patch('services.chatbot_service.Chatbot')
def test_query_endpoint(mock_chatbot, mock_neural_searcher):
    mock_neural_searcher_instance = Mock()
    mock_neural_searcher.return_value = mock_neural_searcher_instance
    mock_neural_searcher_instance.search.return_value = ["mock search result"]
    
    mock_chatbot.search.return_value = "Mock chatbot response"

    test_message = {"message": "test query"}
    
    response = client.post("/query", json=test_message)
    
    assert response.status_code == 200
    assert response.json() == {"output": "Mock chatbot response"}
    
    mock_neural_searcher_instance.search.assert_called_once_with(text="test query")
    mock_chatbot.search.assert_called_once_with(
        client,
        ["mock search result"],
        "test query"
    )

@pytest.mark.asyncio
async def test_query_endpoint_invalid_input():
    response = client.post("/api/v1/query", json={})
    assert response.status_code == 422

    response = client.post("/api/v1/query", json={"message": 123})
    assert response.status_code == 422 