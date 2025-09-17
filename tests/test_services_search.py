import pytest

from wikibee.services.search import SearchError, SearchService


class StubClient:
    def __init__(self) -> None:
        self.calls = []
        self.results = []

    def search_articles(self, term: str, *, limit: int, timeout: int):
        self.calls.append((term, limit, timeout))
        if isinstance(self.results, Exception):
            raise self.results
        return self.results


def test_search_service_forwards_parameters() -> None:
    client = StubClient()
    client.results = ["result"]
    service = SearchService(client=client)

    results = service.search(term="A", limit=5, timeout=12)

    assert results == ["result"]
    assert client.calls == [("A", 5, 12)]


def test_search_service_wraps_client_exceptions() -> None:
    client = StubClient()
    client.results = RuntimeError("boom")
    service = SearchService(client=client)

    with pytest.raises(SearchError):
        service.search(term="fail", limit=3, timeout=9)
