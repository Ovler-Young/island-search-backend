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
