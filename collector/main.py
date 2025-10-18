from station import get_station_response, parse_station, insert_station
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    insert_station(parse_station(get_station_response()))
