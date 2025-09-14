import httpx
from typing import Dict, Iterator, Any, Optional
from .settings import Settings
from .utils import retry

class TashuApiClient:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        headers = {
            "User-Agent": "collector/1.0",
        }
        if self.settings.API_TOKEN:
            headers["api-token"] = self.settings.API_TOKEN

        self._http = httpx.Client(
            base_url=self.settings.BASE_URL,
            timeout=self.settings.TIMEOUT,
            headers=headers,
        )

    @retry(times=3, delay=1.0)
    def _get(self, url: str) -> Dict[str, Any]:
        resp = self._http.get(url)
        resp.raise_for_status()
        return resp.json()

    def iter_stations_pages(self) -> Iterator[Dict[str, Any]]:
        url = "/v1/openapi/station"
        data = self._get(url)
        yield data
        next_url = data.get("next")
        while next_url:
            data = self._get(next_url)  # TODO: Next의 값이 Null이 아닌 Link로 가정함. Link가 아닌 Boolean과 같은 데이터라면 수정 필요
            yield data
            next_url = data.get("next")

    def fetch_all_stations_raw(self) -> Dict[str, Any]:
        """모든 페이지 results를 합쳐 하나의 dict로 반환"""
        merged = {"count": 0, "next": None, "previous": None, "results": []}
        for page in self.iter_stations_pages():
            merged["results"].extend(page.get("results", []))
        merged["count"] = len(merged["results"])
        return merged
