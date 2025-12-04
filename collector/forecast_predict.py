from __future__ import annotations
import os, sys, asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# parent 디렉토리(manual.py)도 import 경로에 추가
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from settings import Settings
from http_client import AsyncHTTP

# 재사용: 모델 로드 및 예측 함수는 manual.py에 이미 정의됨
from manual import (
    backend_predict_recent_data,
    fetch_recent_from_influx,
)


def _pb_base(st: Settings) -> str:
    base = (st.pb_url or "").rstrip("/")
    if not base:
        raise RuntimeError("PB_URL is not set")
    if not base.endswith("/api"):
        base = base + "/api"
    return base


def _auth_headers(st: Settings) -> Dict[str, str]:
    h = {"Content-Type": "application/json"}
    if st.pb_admin_token:
        h["Authorization"] = f"Bearer {st.pb_admin_token}"
    return h


async def _upsert_forecast_records(
    http: AsyncHTTP,
    st: Settings,
    station_id: str,
    items: List[Dict],
) -> None:
    """
    station_forecasts 컬렉션에 target_time 기준 upsert.
    """
    base = _pb_base(st)
    headers = _auth_headers(st)
    col_url = f"{base}/collections/station_forecasts/records"

    async def save_one(item: Dict):
        target_time = item["target_time"]
        filter_q = f'station="{station_id}" && target_time="{target_time}"'
        existing_id = None
        try:
            res = await http.get_json(
                col_url,
                headers=headers,
                params={"filter": filter_q, "perPage": 1},
                max_attempts=st.retry_total + 1,
            )
            items_arr = res.get("items") or []
            if items_arr:
                existing_id = items_arr[0].get("id")
        except Exception:
            pass

        payload = {
            "station": station_id,
            "target_time": target_time,
            "horizon_minutes": item.get("horizon_minutes"),
            "predicted_count": item.get("predicted_count"),
            "model_version": item.get("model_version") or "",
        }

        try:
            if existing_id:
                await http.patch_json(
                    f"{col_url}/{existing_id}",
                    headers=headers,
                    json_body=payload,
                    max_attempts=st.retry_total + 1,
                )
            else:
                await http.post_json(
                    col_url,
                    headers=headers,
                    json_body=payload,
                    max_attempts=st.retry_total + 1,
                )
        except Exception as e:
            print({"forecast_upsert_error": str(e), "station": station_id, "target_time": target_time})

    await asyncio.gather(*(save_one(it) for it in items))


async def predict_and_store_for_stations(
    station_counts: List[Tuple[str, int]], st: Settings
) -> None:
    """
    station_counts: [(station_id, parking_count), ...]
    """
    if not st.predict_enabled:
        return
    if not st.pb_url:
        print({"forecast_skip": "PB_URL not set"})
        return
    has_influx = (
        st.influx_url and st.influx_org and st.influx_token and st.influx_bucket
    )
    if not has_influx:
        print({"forecast_skip": "Influx env missing"})
        return

    http = AsyncHTTP(st)
    sem = asyncio.Semaphore(max(1, st.predict_concurrency))
    # station id 정규화 + 중복 제거 (order 유지)
    norm = []
    seen = set()
    for sid, _ in station_counts:
        s = str(sid).strip().upper()
        if s and s not in seen:
            seen.add(s)
            norm.append(s)
    if st.predict_max_stations > 0 and len(norm) > st.predict_max_stations:
        norm = norm[: st.predict_max_stations]

    async def one_station(sid: str):
        async with sem:
            try:
                recent = await asyncio.to_thread(
                    fetch_recent_from_influx,
                    sid,
                    "-6h",
                    max(40, st.predict_timesteps + 8),
                )
                if not recent:
                    return

                features = ["temp", "wind_speed"]
                df = backend_predict_recent_data(
                    recent,
                    feature_cols=features,
                    timesteps=st.predict_timesteps,
                    horizon=st.predict_horizon,
                )
                last_ts = max(
                    datetime.strptime(r["_time"], "%Y-%m-%d %H:%M:%S")
                    for r in recent
                    if r.get("_time")
                )
                items = []
                max_rows = max(1, st.predict_save_steps)
                for _, row in df.head(max_rows).iterrows():
                    step = int(row["step"])
                    minutes = st.predict_step_minutes * (step + 1)
                    target_time = last_ts + timedelta(minutes=minutes)
                    items.append(
                        {
                            "target_time": target_time.isoformat(),
                            "horizon_minutes": minutes,
                            "predicted_count": float(row["pred_parking_count"]),
                            "model_version": "seq2seq_v3",
                        }
                    )
                if items:
                    await _upsert_forecast_records(http, st, sid, items)
            except Exception as e:
                print({"forecast_error": str(e), "station": sid})

    try:
        await asyncio.gather(*(one_station(sid) for sid in norm))
    finally:
        await http.close()
