from typing import Any
import aiohttp
import asyncio
import ssl
import os
import socket

_session = None
_connector = None


def _ssl_context() -> ssl.SSLContext | bool:
    v = os.getenv("VERIFY_SSL", "1").strip()
    if v in ("0", "false", "False", "FALSE", "no"):
        return ssl._create_unverified_context()
    cafile = os.getenv("CA_BUNDLE", "").strip()
    if cafile:
        return ssl.create_default_context(cafile=cafile)
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return True


def _timeout() -> aiohttp.ClientTimeout:
    return aiohttp.ClientTimeout(total=30, connect=10, sock_read=20)


async def _get_session() -> aiohttp.ClientSession:
    global _session, _connector
    if _session and not _session.closed:
        return _session
    ctx = _ssl_context()
    _connector = aiohttp.TCPConnector(
        ssl=ctx, ttl_dns_cache=300, family=socket.AF_INET, limit=50
    )
    _session = aiohttp.ClientSession(timeout=_timeout(), connector=_connector)
    return _session


async def shutdown_weather_client() -> None:
    global _session, _connector
    if _session and not _session.closed:
        await _session.close()
    _session = None
    _connector = None


async def _fetch_json(url: str, retries: int = 3) -> dict[str, Any]:
    delay = 1.0
    session = await _get_session()
    for i in range(retries):
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                raise Exception(
                    f"open weather refused request with status code: {resp.status}"
                )
        except (aiohttp.ClientError, asyncio.TimeoutError):
            if i == retries - 1:
                raise
            await asyncio.sleep(delay)
            delay *= 2
    raise RuntimeError("unreachable")


async def get_open_weather_response(
    API_KEY: str, lat: float, lon: float
) -> dict[str, Any]:
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=kr"
    )
    return await _fetch_json(url)


def parse_weather_data(data: dict[str, Any]) -> dict[str, Any]:
    r: dict[str, Any] = {}
    r["weather"] = [x["main"] for x in data.get("weather", [])]
    m = data.get("main", {})
    w = data.get("wind", {})
    r["temp"] = m.get("temp")
    r["wind_speed"] = w.get("speed")
    return r
