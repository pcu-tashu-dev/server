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
> python -m collector.cli --kind station --sink postgres
> ```

> [!NOTE] 
> **parking_count 정보 불러오는 커맨드**
>
> ```bash
> python -m collector.cli --kind parking_count --sink influx
> ```

> [!CAUTION]
> **주의 사항**
>
> 다음 코드 실행을 위해서는, Postgres 정보가 .env에 기입되어 있어야 합니다.
> 또한, station 테이블은 server 폴더에서 다음 명령어로 실행하여 생성합니다.
> ```bash
> python -m database.init_db
> ```
