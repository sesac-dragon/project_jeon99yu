# ⚽ HiddenPlayer
게임 능력치와 시장가치와의 상관관계를 통한 저평가된 선수 탐색

## 📌 프로젝트 개요

이 프로젝트는 실제 축구 선수들의 (EA Sports FC Online)게임 능력치와 (Transfermarkt 기준)시장 가치를 비교 분석하여 **저평가된 선수**를 탐색하는 것을 목표로 합니다.  
`OVR`(Overall Rating) 기반 순위와 `MarketValue` 기반 순위의 차이를 `Rank Gap`으로 정의하고, 이 값을 기준으로 저평가 선수를 선별합니다.

선수들의 **포지션, 국가, 리그, 나이** 등의 분포와 특성을 다양한 시각화 기법으로 분석하며, 결과는 **Streamlit 대시보드**로 구현하였습니다.

---

## 🛠 사용 기술 스택 및 환경

- **언어 및 라이브러리**:  
  - `Python` (pandas, numpy, matplotlib, seaborn, plotly, streamlit)
  - `MySQL`

- **분석 및 시각화**:  
  - 능력치 및 시장 가치 통계 분석  
  - Rank Gap 계산 및 상관관계 분석  
  - 바 차트, 산점도, 파이 차트, 히트맵, 지리정보 시각화 등

- **대시보드 및 배포**:  
  - `Streamlit` 대시보드 구현  
  - `Docker`, `Docker Compose`를 활용한 컨테이너 기반 배포  
  - `.env` 파일을 통한 DB 정보 보안 처리
  - 보안 처리: `.env` 파일과 `${KEY}` 문법으로 환경변수 관리

---

## 💾 데이터 처리 흐름

1. EA FC 게임 능력치 및 Transfermarkt 시장가치 데이터 수집
2. 선수 이름 및 포지션 통일, 누락/이상값 처리
3. `OVR Rank` vs `MarketValue Rank` 차이를 기반으로 `Rank_Gap` 계산
4. 저평가 선수 TOP 10 및 고평가 선수 TOP 10 도출
5. Streamlit 대시보드에서 조건 필터링 및 시각적 탐색 기능 구현

---

## 📊 주요 기능 구성 (Streamlit 대시보드)

| 기능               | 설명                                          |
|--------------------|-----------------------------------------------|
| 선수 필터링        | 포지션 / 국가 / 리그별 조건 필터링           |
| 능력치 vs 시장가치 비교 | Scatter plot으로 시각화                     |
| 저평가 선수 TOP 10 | Rank Gap 기준으로 목록 제공                   |
| 능력치 분포        | 히스토그램 또는 커널 밀도                     |
| 선수 상세 조회     | 클릭 시 세부 능력치 및 정보 표시              |


## 🎯 주요 기능

- 포지션/국가/리그 필터를 통한 선수 목록 필터링
- OVR vs MarketValue 산점도 시각화
- 국가별/리그별 선수 분포 및 능력치 시각화
- 무소속 선수 데이터 분석
- 평균 시장가치 상위 리그 및 국가 분석
- 저평가 선수/고평가 선수 TOP 10 표 제공
- 주목할 만한 선수 조건 기반 강조 표시

---

## 🧪 DB 연동 및 배포

- `football_eda.csv`를 MySQL로 업로드 (`football` 테이블)
- `.env` 파일을 통한 환경변수로 `DB` 접속 정보 관리
- `Docker` + `Docker Compose` 환경으로 배포 자동화 구성

---

## 📈 주요 인사이트

- 일부 능력치가 높음에도 불구하고 나이나 포지션 등의 이유로 시장가치가 낮은 **잠재적 유망주** 존재
- 수비수 및 골키퍼는 능력치에 비해 저평가되는 경향
- 국가 및 리그별로 시장가치 책정 기준의 편차 존재

---

## 📁 폴더 구조
PROJECT_JEON99YU/
├── 📁 assets/
│ ├── 📁 icon/
│ └── 📁 plots/
│
├── 📁 crawlers/
│ ├── 📓 EAports_crawler.ipynb
│ ├── 🐍 EAports_crawler.py
│ ├── 📓 transfermarkt_crawler.ipynb
│ └── 🐍 transfermarkt_crawler.py
│
├── 📁 dashboard/
│ ├── 🐍 dashboard.py
│ ├── 📄 Dockerfile
│ ├── 🐍 football_db.py
│ └── 🐍 streamlit_app.py
│
├── 📁 data/
│ └── 📄 football_eda.csv ← 크롤링/전처리된 CSV 데이터 파일
│
├── 📁 db/
│ └── 📄 football_db.sql
│
├── 📁 notebooks/
│ ├── 📓 football_eda.ipynb
│ └── 📓 football_report.ipynb
│
├── 📁 preprocessing/
│ ├── 📓 EAsports_prep.ipynb
│ └── 📓 transfermarkt_prep.ipynb
│
├── 📄 .env
├── 📄 .gitignore
├── 📄 docker-compose.yml
├── 📄 folder.md
├── 📄 nginx.conf
├── 📄 README.md
└── 📄 requirements.txt