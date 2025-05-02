import pytest
import responses
from flexbase_client import FlexBaseClient
from flexbase_client.exceptions import (
    UnauthorizedError,
    BadRequestError,
    NotFoundError
)

@pytest.fixture
def client():
    return FlexBaseClient(api_key="test_key", base_url="http://localhost:8080")

@pytest.fixture
def mock_responses():
    with responses.RequestsMock() as rsps:
        yield rsps

def test_create_collection(client, mock_responses):
    mock_responses.add(
        responses.POST,
        "http://localhost:8080/collections",
        json={"id": "test_collection"},
        status=200
    )
    
    result = client.create_collection("test_collection")
    assert result == {"id": "test_collection"}

def test_insert_document(client, mock_responses):
    mock_responses.add(
        responses.POST,
        "http://localhost:8080/collections/test/documents",
        json={"id": "doc1", "name": "test"},
        status=200
    )
    
    result = client.insert_document("test", {"name": "test"})
    assert result == {"id": "doc1", "name": "test"}

def test_get_documents(client, mock_responses):
    mock_responses.add(
        responses.GET,
        "http://localhost:8080/collections/test/documents",
        json=[{"id": "doc1"}, {"id": "doc2"}],
        status=200
    )
    
    result = client.get_documents("test")
    assert len(result) == 2
    assert result[0]["id"] == "doc1"

def test_unauthorized_error(client, mock_responses):
    mock_responses.add(
        responses.GET,
        "http://localhost:8080/collections/test/documents",
        status=401
    )
    
    with pytest.raises(UnauthorizedError):
        client.get_documents("test")

def test_bad_request_error(client, mock_responses):
    mock_responses.add(
        responses.POST,
        "http://localhost:8080/collections/test/documents",
        status=400,
        json={"error": "Invalid data"}
    )
    
    with pytest.raises(BadRequestError):
        client.insert_document("test", {"invalid": "data"})

def test_not_found_error(client, mock_responses):
    mock_responses.add(
        responses.GET,
        "http://localhost:8080/collections/test/documents/nonexistent",
        status=404
    )
    
    with pytest.raises(NotFoundError):
        client.get_document_by_id("test", "nonexistent") 