# http_client.py
from __future__ import annotations
import asyncio, aiohttp, ssl, socket, random, time, json
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from settings import Settings


@dataclass
class ProxyNode:
    url: str
    last_fail: float = 0.0
    cooldown: int = 60
    success: int = 0
    fail: int = 0

    def healthy(self, now: float) -> bool:
        return (now - self.last_fail) >= self.cooldown


class ProxyPool:
    def __init__(self, settings: Settings):
        self.s = settings
        self.nodes: List[ProxyNode] = [
            ProxyNode(p, cooldown=settings.proxy_cooldown) for p in settings.proxy_urls
        ]
        self.i = 0
        self.lock = asyncio.Lock()
        self._refresh_task: Optional[asyncio.Task] = None

    async def start(self):
        if self._refresh_task or not self.s.proxy_list_source_url:
            return
        self._refresh_task = asyncio.create_task(self._refresh_loop())

    async def _refresh_loop(self):
        while True:
            try:
                urls = await fetch_proxy_list(self.s)
                async with self.lock:
                    self.nodes = [
                        ProxyNode(u, cooldown=self.s.proxy_cooldown) for u in urls
                    ] or self.nodes
                if self.s.http_debug:
                    print(json.dumps({"proxy_refresh": len(self.nodes)}))
            except Exception as e:
                if self.s.http_debug:
                    print(json.dumps({"proxy_refresh_error": str(e)}))
            await asyncio.sleep(self.s.proxy_refresh_interval)

    async def pick(self) -> Optional[ProxyNode]:
        if self._refresh_task is None:
            await self.start()
        if not self.nodes:
            return None
        now = time.time()
        async with self.lock:
            for _ in range(len(self.nodes)):
                n = self.nodes[self.i]
                self.i = (self.i + 1) % len(self.nodes)
                if n.healthy(now):
                    return n
            return min(self.nodes, key=lambda n: n.last_fail)

    async def mark_success(self, n: Optional[ProxyNode]):
        if not n:
            return
        async with self.lock:
            n.success += 1
            n.last_fail = 0

    async def mark_failure(self, n: Optional[ProxyNode], penalty: int):
        if not n:
            return
        async with self.lock:
            n.fail += 1
            n.last_fail = time.time()
            n.cooldown = max(n.cooldown, penalty)


def _ssl_ctx(st: Settings) -> ssl.SSLContext | bool:
    if not st.verify_ssl:
        return ssl._create_unverified_context()
    if st.ca_bundle:
        return ssl.create_default_context(cafile=st.ca_bundle)
    return ssl.create_default_context()


async def fetch_proxy_list(st: Settings) -> List[str]:
    if not st.proxy_list_source_url:
        return st.proxy_urls
    async with aiohttp.ClientSession() as s:
        async with s.get(
            st.proxy_list_source_url, timeout=aiohttp.ClientTimeout(total=20)
        ) as r:
            txt = await r.text()
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    if st.proxy_format.lower() == "raw":
        return lines
    return [f"http://{l}" for l in lines if ":" in l]


class AsyncHTTP:
    def __init__(self, settings: Settings):
        self.s = settings
        self.pool = (
            ProxyPool(settings)
            if (settings.proxy_urls or settings.proxy_list_source_url)
            else None
        )
        self.connector = aiohttp.TCPConnector(
            ssl=_ssl_ctx(settings),
            ttl_dns_cache=300,
            limit=0,
            family=socket.AF_UNSPEC,
            enable_cleanup_closed=True,
        )
        self.session = aiohttp.ClientSession(
            connector=self.connector, trust_env=False, raise_for_status=False
        )

    async def close(self):
        await self.session.close()
        await self.connector.close()

    async def _do(
        self,
        method: str,
        url: str,
        *,
        headers=None,
        params=None,
        json_body=None,
        data=None,
        proxy: Optional[str] = None,
    ):
        if self.s.http_debug:
            print(
                json.dumps(
                    {"req": {"method": method, "url": url, "proxy": proxy}},
                    ensure_ascii=False,
                )
            )
        return await self.session.request(
            method.upper(),
            url,
            headers=headers,
            params=params,
            json=json_body,
            data=data,
            proxy=proxy,
            timeout=aiohttp.ClientTimeout(
                sock_connect=self.s.http_timeout_connect,
                sock_read=self.s.http_timeout_read,
            ),
        )

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers=None,
        params=None,
        json_body=None,
        data=None,
        max_attempts=None,
    ):
        attempts = (
            max_attempts if max_attempts is not None else (self.s.retry_total + 1)
        )
        last_exc = None
        tried_direct = False
        if self.s.allow_direct:
            try:
                await asyncio.sleep(
                    self.s.jitter_base + random.random() * self.s.jitter_extra
                )
                r = await self._do(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    json_body=json_body,
                    data=data,
                    proxy=None,
                )
                if r.status in (401, 403, 429):
                    last_exc = RuntimeError(f"blocked {r.status} direct")
                    await r.release()
                elif 500 <= r.status < 600:
                    last_exc = RuntimeError(f"server {r.status} direct")
                    await r.release()
                else:
                    return r
            except (
                asyncio.TimeoutError,
                aiohttp.ClientConnectorError,
                aiohttp.ClientProxyConnectionError,
                aiohttp.ClientHttpProxyError,
            ) as e:
                last_exc = e
            except aiohttp.ClientSSLError as e:
                last_exc = e
            except aiohttp.ClientError as e:
                last_exc = e
            tried_direct = True
        if not self.pool:
            if tried_direct:
                raise last_exc or RuntimeError("all attempts failed (direct)")
            raise RuntimeError("no proxy configured and direct disabled")
        await self.pool.start()
        for i in range(1, attempts + 1):
            node = await self.pool.pick()
            proxy = node.url if node else None
            await asyncio.sleep(
                self.s.jitter_base + random.random() * self.s.jitter_extra
            )
            try:
                r = await self._do(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    json_body=json_body,
                    data=data,
                    proxy=proxy,
                )
                if r.status in (401, 403, 429):
                    await self.pool.mark_failure(node, penalty=120)
                    last_exc = RuntimeError(f"blocked {r.status} via {proxy}")
                    await r.release()
                    continue
                if 500 <= r.status < 600:
                    await self.pool.mark_failure(node, penalty=60)
                    last_exc = RuntimeError(f"server {r.status} via {proxy}")
                    await r.release()
                    await asyncio.sleep(self.s.backoff_base * i)
                    continue
                await self.pool.mark_success(node)
                return r
            except (
                asyncio.TimeoutError,
                aiohttp.ClientConnectorError,
                aiohttp.ClientProxyConnectionError,
                aiohttp.ClientHttpProxyError,
            ) as e:
                await self.pool.mark_failure(node, penalty=90)
                last_exc = e
                await asyncio.sleep(self.s.backoff_base * i)
            except aiohttp.ClientSSLError as e:
                await self.pool.mark_failure(node, penalty=180)
                last_exc = e
                await asyncio.sleep(self.s.backoff_base * i)
            except aiohttp.ClientError as e:
                await self.pool.mark_failure(node, penalty=60)
                last_exc = e
                await asyncio.sleep(self.s.backoff_base * i)
        raise last_exc or RuntimeError("all attempts failed")

    async def get_json(
        self, url: str, *, headers=None, params=None, max_attempts=None
    ) -> Dict[str, Any]:
        r = await self.request(
            "GET", url, headers=headers, params=params, max_attempts=max_attempts
        )
        try:
            j = await r.json()
        finally:
            await r.release()
        return j

    async def post_json(
        self, url: str, *, headers=None, json_body=None, max_attempts=None
    ) -> Dict[str, Any]:
        r = await self.request(
            "POST", url, headers=headers, json_body=json_body, max_attempts=max_attempts
        )
        try:
            j = await r.json()
        finally:
            await r.release()
        return j

    async def patch_json(
        self, url: str, *, headers=None, json_body=None, max_attempts=None
    ) -> Dict[str, Any]:
        r = await self.request(
            "PATCH",
            url,
            headers=headers,
            json_body=json_body,
            max_attempts=max_attempts,
        )
        try:
            j = await r.json()
        finally:
            await r.release()
        return j
