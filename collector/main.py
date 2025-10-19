from station import get_station_response, parse_station, insert_station
from parking_count import (
    get_parking_count_response,
    parse_parking_count,
    insert_parking_count,
)
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    insert_parking_count(parse_parking_count(get_parking_count_response()))
