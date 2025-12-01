# station.py
from __future__ import annotations
import asyncio
from typing import Dict, Any, List, Optional
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
        print("PB_URL is empty")
        return
    http = AsyncHTTP(st)
    default_zone_cache: Dict[str, str] = {}
    zones_cache: List[Dict[str, Any]] = []
    try:
        zones_cache = await load_zones(http, st)
        headers = {"Content-Type": "application/json"}
        if st.pb_admin_token:
            headers["Authorization"] = f"Bearer {st.pb_admin_token}"

        async def upsert_one(r: Dict[str, Any]):
            sid = str(r.get("id") or r.get("station_id") or r.get("stationId") or "")
            name = str(r.get("name") or sid or "")
            if not name or not sid:
                return
            try:
                lat = float(r.get("x_pos") or r.get("lat") or 0)
                lon = float(r.get("y_pos") or r.get("lon") or 0)
            except (TypeError, ValueError):
                return
            address = str(r.get("address") or "")
            zone_name = str(r.get("zone") or r.get("zone_id") or "").strip()
            zone_id = None
            if zone_name:
                zone_id = await resolve_zone(http, st, zone_name)
            if not zone_id:
                zone_id = find_zone_by_point(lat, lon, zones_cache)
            if not zone_id:
                zone_id = await get_default_zone(http, st, default_zone_cache)
            url_list = f"{st.pb_url.rstrip('/')}/api/collections/{st.pb_station_collection}/records"
            q = {"filter": f'name=\"{name}\"', "perPage": "1"}
            items = []
            try:
                found = await http.get_json(
                    url_list, params=q, max_attempts=st.retry_total + 1
                )
                items = found.get("items") or found.get("records") or []
            except Exception:
                items = []
            body = {
                "id": sid,
                "name": name,
                "address": address,
                "lat": lat,
                "lon": lon,
            }
            if zone_id:
                body["zone"] = zone_id
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


async def resolve_zone(http: AsyncHTTP, st: Settings, zone_name: str) -> str | None:
    """Return PocketBase relation id for the given zone name/zone_id."""
    url = f"{st.pb_url.rstrip('/')}/api/collections/{st.pb_zone_collection}/records"
    params = {"filter": f'zone_id=\"{zone_name}\"', "perPage": "1"}
    try:
        res = await http.get_json(url, params=params, max_attempts=st.retry_total + 1)
        items = res.get("items") or res.get("records") or []
        if items and items[0].get("id"):
            return items[0]["id"]
    except Exception:
        return None
    return None


async def get_default_zone(
    http: AsyncHTTP, st: Settings, cache: Dict[str, str]
) -> str | None:
    """Fallback: return first zone id; cached after first lookup."""
    if "default" in cache:
        return cache["default"]
    url = f"{st.pb_url.rstrip('/')}/api/collections/{st.pb_zone_collection}/records"
    params = {"page": 1, "perPage": 1}
    try:
        res = await http.get_json(url, params=params, max_attempts=st.retry_total + 1)
        items = res.get("items") or res.get("records") or []
        if items and items[0].get("id"):
            cache["default"] = items[0]["id"]
            return cache["default"]
    except Exception:
        return None
    return None


def find_zone_by_point(lat: float, lon: float, zones: List[Dict[str, Any]]) -> Optional[str]:
    """Return zone id whose bounding box contains the point."""
    for z in zones:
        try:
            if (
                z["min_lat"] <= lat <= z["max_lat"]
                and z["min_lon"] <= lon <= z["max_lon"]
            ):
                return z["id"]
        except Exception:
            continue
    return None


async def load_zones(http: AsyncHTTP, st: Settings) -> List[Dict[str, Any]]:
    """Load all zones with bounding boxes."""
    url = f"{st.pb_url.rstrip('/')}/api/collections/{st.pb_zone_collection}/records"
    page = 1
    per_page = 200
    zones: List[Dict[str, Any]] = []
    while True:
        params = {"page": page, "perPage": per_page}
        try:
            res = await http.get_json(url, params=params, max_attempts=st.retry_total + 1)
        except Exception:
            break
        items = res.get("items") or res.get("records") or []
        if not items:
            break
        for it in items:
            try:
                zones.append(
                    {
                        "id": it["id"],
                        "min_lat": float(it.get("min_lat") or 0),
                        "max_lat": float(it.get("max_lat") or 0),
                        "min_lon": float(it.get("min_lon") or 0),
                        "max_lon": float(it.get("max_lon") or 0),
                    }
                )
            except Exception:
                continue
        total_pages = res.get("totalPages")
        if total_pages and page >= total_pages:
            break
        if len(items) < per_page:
            break
        page += 1
    return zones
