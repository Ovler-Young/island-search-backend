import asyncio
import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient


APPLICATION_PATH = Path(__file__).parents[1] / "saveweb-search-backend.py"
SPEC = importlib.util.spec_from_file_location("application", APPLICATION_PATH)
assert SPEC is not None
assert SPEC.loader is not None
APPLICATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(APPLICATION)


def test_root_route_returns_html():
    response = TestClient(APPLICATION.app).get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_uses_nmbxd_meilisearch_index():
    assert APPLICATION.INDEX_NAME == "nmbxd"


class FakeSearchResult:
    estimated_total_hits = 1
    hits = [{
        "_id": "post-1",
        "id": 42,
        "now": 1_700_000_000,
        "title": "Example",
        "content": "Body",
        "userid": "alice",
    }]


class FakeIndex:
    async def search(self, query, **kwargs):
        assert query == "example"
        assert kwargs["attributes_to_retrieve"] == [
            "_id", "id", "fid", "ext", "now", "name", "title", "content",
            "parent", "type", "userid",
        ]
        return FakeSearchResult()


class FakeClient:
    def index(self, index_name):
        assert index_name == "nmbxd"
        return FakeIndex()


async def no_load():
    return 0


def test_search_adapts_nmbxd_fields_for_the_frontend(monkeypatch):
    monkeypatch.setattr(APPLICATION, "client", FakeClient())
    monkeypatch.setattr(APPLICATION, "get_load", no_load)

    result = asyncio.run(APPLICATION.search(q="example"))

    assert result["hits"] == [{
        "_id": "post-1",
        "id": 42,
        "now": 1_700_000_000,
        "title": "Example",
        "content": "Body",
        "userid": "alice",
        "author": "alice",
        "tags": "",
        "date": 1_700_000_000,
        "link": "#",
    }]
