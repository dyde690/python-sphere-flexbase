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


class SearchQuery:
    """Builder for complex search queries."""
    
    def __init__(self):
        self.conditions: List[Dict] = []
        self.or_groups: List[List[Dict]] = []
        self._sort_field: Optional[str] = None
        self._sort_order: str = "asc"
        self._page: int = 1
        self._per_page: int = 10
        self._fts_query: Optional[str] = None
        self._fts_fields: List[str] = []
    
    def where(self, field: str, op: str, value: Any) -> "SearchQuery":
        """Add a condition. Operators: =, !=, >, <, >=, <=, ~, in, between, regex, ~="""
        cond = {"field": field, "op": op}
        if isinstance(value, (list, tuple)):
            cond["values"] = [str(v) for v in value]
        else:
            cond["value"] = str(value)
        self.conditions.append(cond)
        return self
    
    def eq(self, field: str, value: Any) -> "SearchQuery":
        """Exact match."""
        return self.where(field, "=", value)
    
    def ne(self, field: str, value: Any) -> "SearchQuery":
        """Not equal."""
        return self.where(field, "!=", value)
    
    def gt(self, field: str, value: Any) -> "SearchQuery":
        """Greater than."""
        return self.where(field, ">", value)
    
    def gte(self, field: str, value: Any) -> "SearchQuery":
        """Greater than or equal."""
        return self.where(field, ">=", value)
    
    def lt(self, field: str, value: Any) -> "SearchQuery":
        """Less than."""
        return self.where(field, "<", value)
    
    def lte(self, field: str, value: Any) -> "SearchQuery":
        """Less than or equal."""
        return self.where(field, "<=", value)
    
    def contains(self, field: str, value: str) -> "SearchQuery":
        """Substring match (case-insensitive)."""
        return self.where(field, "~", value)
    
    def in_list(self, field: str, values: List[Any]) -> "SearchQuery":
        """Value in list."""
        cond = {"field": field, "op": "in", "values": [str(v) for v in values]}
        self.conditions.append(cond)
        return self
    
    def between(self, field: str, min_val: Any, max_val: Any) -> "SearchQuery":
        """Value between min and max (inclusive)."""
        cond = {"field": field, "op": "between", "values": [str(min_val), str(max_val)]}
        self.conditions.append(cond)
        return self
    
    def regex(self, field: str, pattern: str) -> "SearchQuery":
        """Regex pattern match."""
        return self.where(field, "regex", pattern)
    
    def fuzzy(self, field: str, value: str, distance: int = 2) -> "SearchQuery":
        """Fuzzy match with Levenshtein distance."""
        cond = {"field": field, "op": "~=", "value": value, "fuzzy_distance": distance}
        self.conditions.append(cond)
        return self
    
    def exists(self, field: str) -> "SearchQuery":
        """Field exists."""
        return self.where(field, "exists", "1")
    
    def not_exists(self, field: str) -> "SearchQuery":
        """Field doesn't exist."""
        return self.where(field, "!exists", "1")
    
    def fts(self, query: str, fields: Optional[List[str]] = None) -> "SearchQuery":
        """Full-text search with BM25 ranking."""
        self._fts_query = query
        if fields:
            self._fts_fields = fields
        return self
    
    def sort(self, field: str, order: str = "asc") -> "SearchQuery":
        """Sort results by field. Order: 'asc' or 'desc'."""
        self._sort_field = field
        self._sort_order = order
        return self
    
    def page(self, page: int) -> "SearchQuery":
        """Set page number (1-indexed)."""
        self._page = max(1, page)
        return self
    
    def per_page(self, limit: int) -> "SearchQuery":
        """Set results per page (max 100)."""
        self._per_page = min(100, max(1, limit))
        return self
    
    def to_dict(self) -> Dict:
        """Convert to JSON body for POST request."""
        result: Dict[str, Any] = {
            "page": self._page,
            "per_page": self._per_page
        }
        
        if self.conditions:
            result["conditions"] = self.conditions
        
        if self.or_groups:
            result["or_groups"] = self.or_groups
        
        if self._sort_field:
            result["sort"] = {"field": self._sort_field, "order": self._sort_order}
        
        if self._fts_query:
            result["q"] = self._fts_query
            if self._fts_fields:
                result["fts_fields"] = self._fts_fields
        
        return result


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
            per_page: int = 10,
            sort: Optional[str] = None,
            order: str = "asc"
    ) -> Dict:
        """
        Search documents using query parameters.
        
        Supports filtering by fields with operators:
        - Exact match: {"name": "Alice"}
        - Not equal: {"status:!=": "deleted"}
        - Comparison: {"age:>": 25, "age:<=": 50}
        - Substring: {"name:~": "Ali"}
        - In list: {"status:in": "active,pending"}
        - Between: {"price:between": "100,500"}
        - Regex: {"email:regex": ".*@gmail\\.com"}
        - Fuzzy: {"name:~=": "Alise"}  # finds "Alice"
        
        Pagination and sorting supported.
        """
        params = filters.copy() if filters else {}
        params["page"] = str(page)
        params["per_page"] = str(per_page)
        
        if sort:
            params["sort"] = sort
            params["order"] = order

        response = self.session.get(f"{self.base_url}/documents/{collection}/search", params=params)
        return self._handle_response(response)
    
    def search(self, collection: str, query: SearchQuery) -> Dict:
        """
        Advanced search using SearchQuery builder.
        Uses POST endpoint for complex queries.
        
        Example:
            query = SearchQuery()\\
                .contains("name", "phone")\\
                .between("price", 100, 1000)\\
                .in_list("category", ["electronics", "gadgets"])\\
                .sort("price", "desc")\\
                .page(1).per_page(20)
            
            results = client.search("products", query)
        """
        response = self.session.post(
            f"{self.base_url}/documents/{collection}/search",
            json=query.to_dict()
        )
        return self._handle_response(response)
    
    def fts_search(
            self,
            collection: str,
            query: str,
            fields: Optional[List[str]] = None,
            page: int = 1,
            per_page: int = 10
    ) -> Dict:
        """
        Full-text search with BM25 ranking.
        
        Args:
            collection: Collection name
            query: Search query text
            fields: Optional list of fields to search in
            page: Page number (1-indexed)
            per_page: Results per page (max 100)
        
        Returns:
            Dict with 'data', 'total', 'page', 'per_page', 'pages'
        """
        params = {
            "q": query,
            "page": str(page),
            "per_page": str(per_page)
        }
        if fields:
            params["fts_fields"] = ",".join(fields)
        
        response = self.session.get(f"{self.base_url}/documents/{collection}/search", params=params)
        return self._handle_response(response)
    
    def search_async(
            self,
            collection: str,
            filters: Optional[Dict[str, Union[str, int]]] = None,
            page: int = 1,
            per_page: int = 10
    ) -> str:
        """
        Start an async search job.
        Returns job_id which can be used with get_search_job().
        """
        params = filters.copy() if filters else {}
        params["page"] = str(page)
        params["per_page"] = str(per_page)
        
        response = self.session.get(f"{self.base_url}/documents/{collection}/search/async", params=params)
        result = self._handle_response(response)
        return result.get("job_id")
    
    def get_search_job(self, job_id: str) -> Dict:
        """
        Get status and results of an async search job.
        
        Returns:
            Dict with 'job_id', 'status' ('queued', 'running', 'done', 'error'),
            and 'result' when status is 'done'
        """
        response = self.session.get(f"{self.base_url}/search/jobs/{job_id}")
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

