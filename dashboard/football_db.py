import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
football_df = pd.read_csv('../data/football_eda.csv', encoding='utf-8-sig')

# MySQL 접속 정보
username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
database = 'football_db'

# SQLAlchemy 엔진 생성
engine = create_engine(f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}")

# 테이블 생성 및 데이터 삽입
football_df.to_sql(name='football', con=engine, if_exists='replace', index=False)
print("football 테이블이 MySQL에 성공적으로 저장되었습니다.")
