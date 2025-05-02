import os
from typing import Dict, List, Optional, Any, Union
import requests
from requests import Session

from .exceptions import (
    FlexBaseError,
    UnauthorizedError,
    BadRequestError,
    NotFoundError,
    ConnectionError,
    TimeoutError
)


class FlexBaseClient:
    def __init__(
            self,
            api_key: Optional[str] = None,
            base_url: str = "http://localhost:8080"
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("FLEXBASE_API_KEY")

        if not self.api_key:
            raise ValueError(
                "API key is required. Provide it either directly or via FLEXBASE_API_KEY environment variable")

        self.session = Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def _handle_response(self, response: requests.Response) -> Any:
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise UnauthorizedError("Invalid API key")
            elif response.status_code == 400:
                raise BadRequestError(response.text)
            elif response.status_code == 404:
                raise NotFoundError(response.text)
            raise FlexBaseError(f"HTTP error occurred: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Connection error occurred: {str(e)}")
        except requests.exceptions.Timeout as e:
            raise TimeoutError(f"Request timed out: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise FlexBaseError(f"Request failed: {str(e)}")

    def create_collection(self, name: str) -> Dict:
        """Create a new collection."""
        response = self.session.post(f"{self.base_url}/collection/{name}")
        return self._handle_response(response)

    def insert_document(self, collection: str, data: Dict) -> Dict:
        """Insert a new document into a collection."""
        response = self.session.post(
            f"{self.base_url}/document/{collection}",
            json=data
        )
        return self._handle_response(response)

    def get_documents(self, collection: str) -> List[Dict]:
        """Get all documents from a collection."""
        response = self.session.get(f"{self.base_url}/documents/{collection}")
        return self._handle_response(response)

    def search_documents(
            self,
            collection: str,
            filters: Optional[Dict[str, Union[str, int]]] = None,
            page: int = 1,
            per_page: int = 10
    ) -> Dict:
        """
        Search documents using query parameters.
        Supports filtering by fields and pagination.
        """
        params = filters.copy() if filters else {}
        params["page"] = str(page)
        params["per_page"] = str(per_page)

        response = self.session.get(f"{self.base_url}/documents/{collection}/search", params=params)
        return self._handle_response(response)

    def update_document(self, collection: str, doc_id: str, changes: Dict) -> Dict:
        """Update a document."""
        response = self.session.put(
            f"{self.base_url}/document/{collection}/{doc_id}",
            json=changes
        )
        return self._handle_response(response)

    def delete_document(self, collection: str, doc_id: str) -> None:
        """Delete a document."""
        response = self.session.delete(f"{self.base_url}/document/{collection}/{doc_id}")
        self._handle_response(response)

    def get_document_by_id(self, collection: str, doc_id: str) -> Optional[Dict]:
        """Get a specific document by ID by searching."""
        result = self.search_documents(collection, filters={"_id": doc_id})
        return result.get("data", [None])[0]
