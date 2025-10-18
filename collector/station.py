from typing import Any
import requests
import os


def get_station_response(
    URL: str = "https://bikeapp.tashu.or.kr:50041/v1/openapi/station",
) -> dict[str, Any]:
    headers = {
        "api-token": os.getenv("TASHU_KEY"),
    }
    res = requests.get(URL, headers=headers)
    if res.status_code == 200:
        return res.json()

    else:
        raise RuntimeError(
            {
                400: "토큰이 만료되었거나 잘못되었습니다.",
                404: "페이지를 찾을 수 없습니다.",
                500: "서버 내부 오류가 발생하였습니다.",
            }[res.status_code]
        )


def parse_station(res: dict[str, Any]) -> dict[str, Any]:
    data = res["results"]
    results = list(
        # id, name, lat, lon, address 순서
        map(lambda x: [x["id"], x["name"], x["x_pos"], x["y_pos"], x["address"]], data)
    )

    return results


def insert_station(data: list[list[Any]]) -> None:
    for d in data:
        record = {
            "id": d[0],
            "name": d[1],
            "lat": float(d[2]),
            "lon": float(d[3]),
            "address": d[4],
        }
        res = requests.post(
            "http://localhost:8090/api/collections/stations/records",
            json=record,
            headers={
                "Content-Type": "application/json",
            },
        )
