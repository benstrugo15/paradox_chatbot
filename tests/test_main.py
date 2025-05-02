from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app

client = TestClient(app)

@patch('services.neural_search_service.NeuralSearcher')
@patch('services.chatbot_service.Chatbot')
def test_query_endpoint(mock_chatbot, mock_neural_searcher):
    # Setup mock returns
    mock_neural_searcher_instance = Mock()
    mock_neural_searcher.return_value = mock_neural_searcher_instance
    mock_neural_searcher_instance.search.return_value = ["mock search result"]
    
    mock_chatbot.search.return_value = "Mock chatbot response"

    # Test data
    test_message = {"message": "test query"}
    
    # Make request to endpoint
    response = client.post("/query", json=test_message)
    
    # Assert response
    assert response.status_code == 200
    assert response.json() == {"output": "Mock chatbot response"}
    
    # Verify our mocks were called correctly
    mock_neural_searcher_instance.search.assert_called_once_with(text="test query")
    mock_chatbot.search.assert_called_once_with(
        client,  # OpenAI client
        ["mock search result"],  # retrieved data
        "test query"  # original query
    )

def test_query_endpoint_invalid_input():
    # Test with missing message field
    response = client.post("/query", json={})
    assert response.status_code == 422

    # Test with wrong data type
    response = client.post("/query", json={"message": 123})
    assert response.status_code == 422 