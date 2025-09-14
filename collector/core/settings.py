import os
from dataclasses import dataclass

@dataclass
class Settings:
    BASE_URL: str = os.getenv("TASHU_BASE_URL", "https://bikeapp.tashu.or.kr:50041")
    TIMEOUT: float = float(os.getenv("HTTP_TIMEOUT", "10"))
    API_TOKEN: str = os.getenv("TASHU_KEY", "")
