from __future__ import annotations

from typing import List

import requests

from wikibee._types import SearchResult
from wikibee.client import WikiClient


class SearchError(RuntimeError):
    """Raised when the search service fails to retrieve results."""


class SearchService:
    """Wrapper around WikiClient.search_articles with error translation."""

    def __init__(self, client: WikiClient | None = None) -> None:
        self._client = client or WikiClient()

    def search(self, term: str, *, limit: int, timeout: int) -> List[SearchResult]:
        try:
            return self._client.search_articles(term, limit=limit, timeout=timeout)
        except (
            requests.exceptions.RequestException
        ) as exc:  # pragma: no cover - depends on network
            raise SearchError(str(exc)) from exc
        except Exception as exc:  # defensive against unexpected failures
            raise SearchError(str(exc)) from exc
