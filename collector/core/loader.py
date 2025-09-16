from __future__ import annotations
import importlib
import pkgutil
from typing import List

def autodiscover_scrapers(pkg_name: str = "collector.scrapers") -> List[str]:
    pkg = importlib.import_module(pkg_name)
    discovered = []
    for m in pkgutil.iter_modules(pkg.__path__, pkg_name + "."):
        importlib.import_module(m.name)
        discovered.append(m.name)
    return discovered