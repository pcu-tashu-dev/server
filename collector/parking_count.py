from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import Point
from typing import Any
import influxdb_client
import requests
import os


def get_parking_count_response(
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


def parse_parking_count(res: dict[str, Any]) -> dict[str, Any]:
    data = res["results"]
    results = list(map(lambda x: [x["id"], x["parking_count"]], data))
    return results


def insert_parking_count(data: list[list[Any]]) -> None:
    url = os.getenv("INFLUXDB_URL")
    org = os.getenv("INFLUXDB_ORG")
    token = os.getenv("INFLUXDB_ADMIN_TOKEN")
    bucket = os.getenv("INFLUXDB_BUCKET")
    parking_count_measurement = "tashu_station"
    client = influxdb_client.InfluxDBClient(
        url=url, org=org, token=token, bucket=bucket
    )
    write_api = client.write_api(write_options=SYNCHRONOUS)
    points = [
        Point(parking_count_measurement)
        .tag("station_id", d[0])
        .field("parking_count", d[1])
        for d in data
    ]

    write_api.write(bucket=bucket, org=org, record=points)
