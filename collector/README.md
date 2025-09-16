# Tashu API Collector

해당 페이지는 빅데이터 분석 및 강화학습을 위한 Tashu API로 부터 데이터를 가져오기 위한 폴더입니다.
Tashu API로 부터 Station(정류장 정보), parking_count(대여 가능 바이크 수) 정보를 불러옵니다.

---

### 사용법

> [!TIP]
> **코드 불러오기**
>
> ```bash
> git clone https://github.com/pcu-tashu-dev/server
> ```

> [!NOTE]
> **station 정보 불러오는 커맨드**
>
> ```bash
> python -m collector --kind station   # 정류장 정보를 불러옵니다.
> ```

> [!NOTE] 
> **parking_count 정보 불러오는 커맨드**
>
> ```bash
> python -m collector --kind parking_count --sink influx --measurement parking_count --tag-keys station_id --time-key updated_at
> ```

> [!CAUTION]
> **주의 사항**
> 
> station 정보 불러오는 커맨드는 변경 예정 입니다.

---

### 해야 할 것

Database (PostgreSQL)과 Station 정보를 연동 해야 하며, parking_count 정보는 Docker나 Crontab을 통한 자동화가 진행되어야 합니다.
