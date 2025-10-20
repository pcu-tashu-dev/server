from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import Point
from dotenv import load_dotenv
from typing import Any
import influxdb_client
import requests
import sys, os

sys.path.append(os.path.dirname(__file__))

from fetch_weather import get_open_weather_response, parse_weather_data
from station import get_zone_by_station_id


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


def insert_parking_count(data: list[list[Any]], weather_data: list[list[Any]]) -> None:
    url = os.getenv("INFLUXDB_URL")
    org = os.getenv("INFLUXDB_ORG")
    token = os.getenv("INFLUXDB_ADMIN_TOKEN")
    bucket = os.getenv("INFLUXDB_BUCKET")

    measurement = "tashu_station"  # 기존 measurement 유지
    client = influxdb_client.InfluxDBClient(
        url=url, org=org, token=token, bucket=bucket
    )
    write_api = client.write_api(write_options=SYNCHRONOUS)

    points: list[Point] = []
    for station_id, parking_count in data:
        wd = weather_data.get(station_id, {})
        p = (
            Point(measurement)
            .tag("station_id", str(station_id))
            .tag("weather_main", str(wd.get("weather") or ""))
            .field("parking_count", int(parking_count))
            .field("temp", float(wd["temp"]))
            if wd.get("temp") is not None
            else Point(measurement)
        )

        p = (
            Point(measurement)
            .tag("station_id", str(station_id))
            .tag("weather_main", str(wd.get("weather") or ""))
        )
        p.field("parking_count", int(parking_count))
        if wd.get("temp") is not None:
            p.field("temp", float(wd["temp"]))
        if wd.get("wind_speed") is not None:
            p.field("wind_speed", float(wd["wind_speed"]))

        points.append(p)

    if points:
        write_api.write(bucket=bucket, org=org, record=points)


if __name__ == "__main__":
    load_dotenv()
    res = get_parking_count_response()
    rows = parse_parking_count(res)
    weather_by_station: dict[str, dict[str, Any]] = {}
    ow_key = os.getenv("OPENWEATHER_API_KEY")
    for station_id, _count in rows:
        zone = get_zone_by_station_id(station_id)
        ow_json = get_open_weather_response(
            ow_key, zone["center_lat"], zone["center_lon"]
        )
        weather_by_station[station_id] = parse_weather_data(ow_json)
    insert_parking_count(rows, weather_by_station)
