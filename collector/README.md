# Tashu API Collector

해당 페이지는 빅데이터 분석 및 강화학습을 위한 Tashu API로 부터 데이터를 가져오기 위한 폴더입니다.
Tashu API로 부터 Station(정류장 정보), parking_count(대여 가능 바이크 수) 정보를 불러옵니다.

---

### 사용법

```bash
git clone https://github.com/pcu-tashu-dev/server # github로 부터 pcu-tashu-dev 내의 server 폴더를 복제합니다.
cd server # 복제한 server 폴더 내부로 이동합니다.
python -m collector --kind station # 정류장 정보를 불러옵니다.
python -m collector --kind parking_count # 대여 가능 바이크 수 정보를 불러옵니다.
```

---

### 해야 할 것

Database (PostgreSQL)과 연동 해야 하며, Docker나 Crontab을 통한 자동화가 진행되어야 합니다.
이를 위해서는 AWS EC2 인스턴스와 같은 클라우드 서비스를 빠르게 받아, 데이터베이스를 띄우고 데이터를 채워 넣어야 합니다.
