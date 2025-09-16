from typing import Type, Dict, Any, Optional
from .base import Scraper

_REGISTRY: Dict[str, Type[Scraper]] = {}

def register(name: str):
    def deco(cls: Type[Scraper]) -> Type[Scraper]:
        _REGISTRY[name] = cls
        cls.name = name
        return cls
    return deco

class ScraperFactory:
    @staticmethod
    def create(name: str, client: Any, **kwargs: Any) -> Scraper:
        try:
            cls = _REGISTRY[name]
        except KeyError:
            raise ValueError(f"Unknown scraper: {name}. Registered: {list(_REGISTRY)}")
        return cls(client=client, **kwargs)

def create(name: str, client: Optional[Any] = None, **kwargs: Any) -> Scraper:
    if client is None:
        from collector.core.client import TashuApiClient
        client = TashuApiClient.from_env()
    return ScraperFactory.create(name, client=client, **kwargs)