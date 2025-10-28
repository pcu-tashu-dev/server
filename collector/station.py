# station.py
from __future__ import annotations
import asyncio
from typing import Dict, Any, List
from http_client import AsyncHTTP
from settings import Settings


async def get_station_response(http: AsyncHTTP, st: Settings) -> Dict[str, Any]:
    return await http.get_json(
        st.tashu_url,
        headers={"api-token": st.tashu_key},
        max_attempts=st.retry_total + 1,
    )


def parse_station(res: Dict[str, Any]) -> List[Dict[str, Any]]:
    data = res.get("results") or res.get("result") or res.get("data") or []
    return list(data)


async def insert_station(rows: List[Dict[str, Any]], st: Settings) -> None:
    if not st.pb_url:
        return
    http = AsyncHTTP(st)
    try:
        sem = asyncio.Semaphore(st.concurrency)
        headers = {"Content-Type": "application/json"}
        if st.pb_admin_token:
            headers["Authorization"] = f"Bearer {st.pb_admin_token}"

        async def upsert_one(r: Dict[str, Any]):
            sid = str(r.get("id") or r.get("station_id") or r.get("stationId") or "")
            if not sid:
                return
            url_list = f"{st.pb_url.rstrip('/')}/api/collections/{st.pb_station_collection}/records"
            q = {"filter": f'station_id="{sid}"', "perPage": "1"}
            found = await http.get_json(
                url_list, params=q, max_attempts=st.retry_total + 1
            )
            items = found.get("items") or found.get("records") or []
            body = {"station_id": sid, **r}
            if items:
                rec_id = items[0].get("id")
                await http.patch_json(
                    f"{url_list}/{rec_id}",
                    headers=headers,
                    json_body=body,
                    max_attempts=st.retry_total + 1,
                )
            else:
                await http.post_json(
                    url_list,
                    headers=headers,
                    json_body=body,
                    max_attempts=st.retry_total + 1,
                )

        await asyncio.gather(*(upsert_one(r) for r in rows))
    finally:
        await http.close()
