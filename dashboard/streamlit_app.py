import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

plt.rcParams['font.family'] = 'Malgun Gothic'  # 한글 폰트 설정
plt.rcParams['axes.unicode_minus'] = False

st.title("⚽ 축구 선수 분석 대시보드")

football_df = pd.read_csv('../data/football_eda.csv')

st.subheader("선수 데이터 미리보기")
st.dataframe(football_df.head())


# 포지션별 선수 수 계산
field_counts = football_df['Field'].value_counts().reset_index()
field_counts.columns = ['Field', 'Count']

st.subheader("포지션별 선수 수 시각화")

# 시각화
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(field_counts['Field'], field_counts['Count'], color='skyblue')
ax.set_title('포지션별 선수 수')
ax.set_xlabel('포지션(Field)')
ax.set_ylabel('선수 수')

# Streamlit에 그래프 출력
st.pyplot(fig)