from typing import Any, List, Dict
from dotenv import load_dotenv
import requests
import os

PB_URL = os.getenv("PB_URL", "http://localhost:8090")
TASHU_URL = "https://bikeapp.tashu.or.kr:50041/v1/openapi/station"


def get_station_response(URL: str = TASHU_URL) -> Dict[str, Any]:
    headers = {"api-token": os.getenv("TASHU_KEY")}
    res = requests.get(URL, headers=headers, timeout=20)
    if res.status_code == 200:
        return res.json()
    raise RuntimeError(
        {
            400: "토큰이 만료되었거나 잘못되었습니다.",
            404: "페이지를 찾을 수 없습니다.",
            500: "서버 내부 오류가 발생하였습니다.",
        }.get(res.status_code, f"HTTP {res.status_code}")
    )


def parse_station(res: Dict[str, Any]) -> List[List[Any]]:
    data = res["results"]
    return list(
        map(lambda x: [x["id"], x["name"], x["y_pos"], x["x_pos"], x["address"]], data)
    )


def fetch_all_zones() -> List[Dict[str, Any]]:
    url = f"{PB_URL}/api/collections/daejeon_zones/records?page=1&perPage=200"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.json().get("items", [])


def find_zone_id(lat: float, lon: float, zones: List[Dict[str, Any]]) -> str | None:
    eps = 1e-9
    for z in zones:
        min_lat = float(z["min_lat"])
        max_lat = float(z["max_lat"])
        min_lon = float(z["min_lon"])
        max_lon = float(z["max_lon"])
        if (min_lat - eps) <= lat <= (max_lat + eps) and (min_lon - eps) <= lon <= (
            max_lon + eps
        ):
            return z["id"]
    return None


def pb_upsert_station(st: Dict[str, Any]) -> Dict[str, Any]:
    filter_q = f'id="{st["id"]}"'
    list_url = f"{PB_URL}/api/collections/stations/records?page=1&perPage=1&filter={requests.utils.quote(filter_q)}"
    r = requests.get(list_url, timeout=20)
    r.raise_for_status()
    data = r.json()
    if data.get("totalItems", 0) > 0:
        rec_id = data["items"][0]["id"]
        url = f"{PB_URL}/api/collections/stations/records/{rec_id}"
        rr = requests.patch(url, json=st, timeout=20)
        rr.raise_for_status()
        return rr.json()
    else:
        url = f"{PB_URL}/api/collections/stations/records"
        rr = requests.post(url, json=st, timeout=20)
        rr.raise_for_status()
        return rr.json()


def insert_station(rows: List[List[Any]]) -> None:
    zones = fetch_all_zones()

    for d in rows:
        sid, name, x_pos, y_pos, address = d

        lat = float(y_pos)
        lon = float(x_pos)

        z_id = find_zone_id(lat, lon, zones)
        if not z_id:
            print(f"[WARN] zone not found for station {sid} ({lat}, {lon})")

        record = {
            "id": str(sid),
            "name": str(name),
            "lat": lat,
            "lon": lon,
            "address": str(address or ""),
            "zone": [z_id] if z_id else [],
        }

        try:
            saved = pb_upsert_station(record)
            print(f"[OK] {sid} -> {saved.get('id')}")
        except requests.HTTPError as e:
            print(f"[ERR] {sid}: {e.response.status_code} {e.response.text}")


def get_zone_by_station_id(id: str) -> dict[str, Any]:
    response = requests.get(
        f"http://localhost:8090/stations/{id}",
        headers={"Content-Type": "application/json"},
    )
    data = response.json()

    if data["success"] == False:
        raise Exception("request is not reached")

    return data["zone"]


if __name__ == "__main__":
    load_dotenv()
    res = get_station_response()
    rows = parse_station(res)
    insert_station(rows)
