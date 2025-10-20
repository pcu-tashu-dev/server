from typing import Any
import requests


def get_open_weather_response(API_KEY, lat, lon) -> dict[str, Any]:
    response = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=kr"
    )

    if response.status_code != 200:
        raise Exception(
            f"open weather refused request with status code: {response.status_code}"
        )

    return response.json()


def parse_weather_data(data: dict[str, Any]) -> dict[str, Any]:
    return_data = {}

    return_data["weather"] = list(map(lambda x: x["main"], data["weather"]))
    return_data["temp"] = data["main"]["temp"]
    return_data["wind_speed"] = data["wind"]["speed"]

    return return_data
