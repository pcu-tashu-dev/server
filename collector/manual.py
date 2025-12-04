"""
모델 사용법 안내:

1. 이 코드의 목적
   - 'backend_predict_recent_data' 함수를 사용하여 미래 자전거 수를 예측
   - 입력: 현재 주차 데이터 리스트(future_input_list)
   - 출력: step에 해당하는 pred_parking_count의 예측값
   - 1 step은 10분 단위를 의미함.

예시) ST0970의 15:50:00 시간으로부터 10분 단위(0 step - 15:50:10, 1 step - 15:50:20, 2 step - 15:50:30, ... ) 예측

입력:
future_input_list = [
    {'_time':'2025-11-27 15:00:00','station_id':'ST0970','temp':16.0,'wind_speed':0.31,'parking_count':1},
    {'_time':'2025-11-27 15:10:00','station_id':'ST0970','temp':16.1,'wind_speed':0.21,'parking_count':1},
    {'_time':'2025-11-27 15:20:00','station_id':'ST0970','temp':16.2,'wind_speed':0.25,'parking_count':0},
    {'_time':'2025-11-27 15:30:00','station_id':'ST0970','temp':16.3,'wind_speed':0.28,'parking_count':2},
    {'_time':'2025-11-27 15:40:00','station_id':'ST0970','temp':16.4,'wind_speed':0.31,'parking_count':1},
    {'_time':'2025-11-27 15:50:00','station_id':'ST0970','temp':16.5,'wind_speed':0.31,'parking_count':1},
]

출력:
   step  pred_parking_count  actual_parking_count
0     0            2.231071                   NaN
1     1            4.254226                   NaN
2     2            6.150022                   NaN
3     3            7.958924                   NaN
4     4            9.729359                   NaN
5     5           11.498637                   NaN


2. 경로 설정
   - 현재 모델, 스케일러, station_dict 경로는 예시로 만든 구글 드라이브 기준으로 설정됨
   - 실제 경로에 맞게 다음 4개의 경로 수정 필요
     MODEL_PATH, SCALER_X_PATH, SCALER_Y_PATH, STATION_DICT_PATH

3. 입력 데이터 형식: '1개의 정류소'에 대해 대략 10분 간격(정확히 10분 아니어도 됨)으로 수집된 데이터베이스의 실제 값을 다음 형식에 맞춰 future_input_list에 입력

   - 반드시 데이터베이스로부터 다음 형식으로 가져와야 함
       _time              station_id   temp  wind_speed  parking_count
       2025-11-27 15:00   ST0970       16.0  31          101
       2025-11-27 15:10   ST0970       16.1  21          111
       2025-11-27 15:20   ST0970       16.2  25          110
   - 예시 데이터 개수가 6개보다 많아도 무방함. 과거 24시간의 데이터 입력 기준 24*6(144)열의 데이터 포함 가능
"""

# -------------------------
# 라이브러리
# -------------------------
import pandas as pd
import numpy as np
import joblib
import json
from tensorflow.keras.models import load_model
from influxdb_client import InfluxDBClient
from settings import load_settings

# -------------------------
# 저장된 모델/스케일러/딕셔너리 경로 설정
# -------------------------
MODEL_PATH = '../model/seq2seq_model3.h5'
SCALER_X_PATH = '../model/scaler_X3.save'
SCALER_Y_PATH = '../model/scaler_y3.save'
STATION_DICT_PATH = '../model/station_dict4.json'


model = load_model(MODEL_PATH, compile=False)  
scaler_X = joblib.load(SCALER_X_PATH)
scaler_y = joblib.load(SCALER_Y_PATH)
with open(STATION_DICT_PATH,'r') as f:
    station_dict = json.load(f)


def _station_vocab_size():
    """Return embedding input_dim; fallback to len(station_dict) or 1."""
    try:
        from tensorflow.keras.layers import Embedding

        for layer in model.layers:
            if isinstance(layer, Embedding):
                return getattr(layer, "input_dim", None) or len(station_dict) or 1
    except Exception:
        pass
    return len(station_dict) or 1


# -------------------------
# 예측 함수 정의
# -------------------------
def backend_predict_recent_data(future_input_list, feature_cols, timesteps=24, horizon=6):
    """
    입력: future_input_list: 데이터베이스로부터 가져올 실제 값
    반환: step별 예측값 DataFrame
    """
    future_df = pd.DataFrame(future_input_list)
    future_df['datetime'] = pd.to_datetime(future_df['_time'])
    future_df['hour'] = future_df['datetime'].dt.hour
    future_df['minute'] = future_df['datetime'].dt.minute
    future_df['dayofweek'] = future_df['datetime'].dt.dayofweek
    # station idx를 dict에서 찾지 못하면 0으로, vocab 범위를 넘어가면 클리핑
    vocab_size = _station_vocab_size()
    future_df['station_idx'] = future_df['station_id'].map(station_dict).fillna(0).astype(int)
    future_df['station_idx'] = future_df['station_idx'].clip(lower=0, upper=max(vocab_size - 1, 0))

    X_future_num = future_df[feature_cols + ['hour','minute','dayofweek']].values.astype(np.float32)
    X_future_scaled = scaler_X.transform(X_future_num)
    station_future = future_df['station_idx'].values.astype(np.int32)

    if len(X_future_scaled) < timesteps:
        pad = np.zeros((timesteps - len(X_future_scaled), X_future_scaled.shape[1]), dtype=np.float32)
        X_future_scaled = np.vstack([pad, X_future_scaled])
        station_future = np.hstack([np.zeros(timesteps-len(station_future),dtype=np.int32), station_future])
    elif len(X_future_scaled) > timesteps:
        X_future_scaled = X_future_scaled[-timesteps:]
        station_future = station_future[-timesteps:]

    X_future_scaled = X_future_scaled.reshape(1, timesteps, X_future_scaled.shape[1])
    station_future = station_future.reshape(1, timesteps)

    y_future_scaled = model.predict([X_future_scaled, station_future])
    y_future = scaler_y.inverse_transform(y_future_scaled.reshape(-1,1)).reshape(y_future_scaled.shape)

    future_list = []
    for h in range(horizon):
        future_list.append({
            'step': h,
            'pred_parking_count': float(y_future[0,h]),
            'actual_parking_count': np.nan
        })
    return pd.DataFrame(future_list)


# -------------------------
# InfluxDB에서 입력 데이터 가져오기
# -------------------------
def fetch_recent_from_influx(station_id: str, start: str = "-24h", limit: int = 144):
    """
    InfluxDB의 tashu_station(measurement)에서 지정 정류소의 최근 데이터를 읽어
    future_input_list 형태(list[dict])로 반환.

    start: Flux range start 값, 예) "-6h", "-1d"
    limit: 최대 레코드 개수
    """
    st = load_settings()
    if not (st.influx_url and st.influx_org and st.influx_token and st.influx_bucket):
        raise RuntimeError("InfluxDB 연결 정보가 env에 설정되어 있지 않습니다.")

    flux = f'''
from(bucket: "{st.influx_bucket}")
  |> range(start: {start})
  |> filter(fn: (r) => r["_measurement"] == "{st.influx_measurement}")
  |> filter(fn: (r) => r["station_id"] == "{station_id}")
  |> filter(fn: (r) => r["_field"] == "parking_count" or r["_field"] == "temp" or r["_field"] == "wind_speed")
  |> pivot(rowKey:["_time","station_id"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"])
  |> limit(n: {limit})
'''

    client = InfluxDBClient(
        url=st.influx_url,
        org=st.influx_org,
        token=st.influx_token,
        bucket=st.influx_bucket,
    )
    try:
        tables = client.query_api().query(flux, org=st.influx_org)
    finally:
        client.close()

    rows = []
    for table in tables:
        for record in table.records:
            values = record.values
            rows.append(
                {
                    "_time": record.get_time().strftime("%Y-%m-%d %H:%M:%S"),
                    "station_id": values.get("station_id"),
                    "temp": float(values.get("temp")) if values.get("temp") is not None else None,
                    "wind_speed": float(values.get("wind_speed")) if values.get("wind_speed") is not None else None,
                    "parking_count": int(values.get("parking_count")) if values.get("parking_count") is not None else None,
                }
            )
    return rows

# -------------------------
# 백엔드용 실행 예시
# future_input_list에 데이터베이스로부터 실제 데이터를 가져올것
# future_input_list 예시의 6개 데이터보다 많은 데이터 포함 가능
# -------------------------
if __name__ == "__main__":
    future_input_list = fetch_recent_from_influx(station_id="ST0970", start="-2h", limit=60)
    print(f"Fetched {len(future_input_list)} rows from InfluxDB")

    features = ['temp','wind_speed']
    future_result = backend_predict_recent_data(future_input_list, features, timesteps=10, horizon=6)

    print(" 미래 예측 ")
    print(future_result)
