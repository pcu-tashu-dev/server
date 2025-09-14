from abc import ABC, abstractmethod
from typing import Any, Iterable

class Scraper(ABC):
    name: str

    def __init__(self, client: Any, **kwargs: Any) -> None:
        self.client = client
        self.options = kwargs

    @abstractmethod
    def fetch(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    def parse(self, raw: Any) -> Iterable[dict]:
        raise NotImplementedError

    def validate(self, records: Iterable[dict]) -> Iterable[dict]:
        """검증 단계 (옵션)"""
        return records

    def run(self) -> list[dict]:
        raw = self.fetch()
        parsed = list(self.parse(raw))
        valid = list(self.validate(parsed))
        return valid
