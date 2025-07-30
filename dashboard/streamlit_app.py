import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os


plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

load_dotenv()  # .env 파일 로드

username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
database = 'football_db'

#### DB 연결 확인용 #####

# MySQL 연결
engine = create_engine("mysql+mysqlconnector://root:test1234@localhost:3306/football_db")
df = pd.read_sql("SELECT * FROM football", con=engine)

st.set_page_config(page_title="⚽ 축구선수 분석", layout="wide")
st.title("⚽ 축구 선수 분석 대시보드")

# 1.멀티 선택 필터
positions = sorted(df['Position'].dropna().unique())
nations = sorted(df['Nation'].dropna().unique())

selected_positions = st.multiselect("포지션 선택", positions, default=positions[:3])
selected_nations = st.multiselect("국가 선택", nations, default=nations[:5])

# 2. 조건에 따라 데이터 필터링
filtered_df = df[
    df['Position'].isin(selected_positions) &
    df['Nation'].isin(selected_nations)
]

st.subheader(f"📋 필터링된 선수 목록 (총 {len(filtered_df)}명)")
st.dataframe(filtered_df)

# 3. 국가별 선수 수 시각화 (GroupBy + Plotly)
st.subheader("🌍 국가별 선수 수 분포")

nation_counts = filtered_df['Nation'].value_counts().reset_index()
nation_counts.columns = ['Nation', 'Player Count']

fig = px.bar(nation_counts, x='Nation', y='Player Count',
             title='선택된 국가의 선수 수',
             labels={'Nation': '국가', 'Player Count': '선수 수'})

st.plotly_chart(fig, use_container_width=True)



#### 여기서 부터는 EDA 불러온 기존 코드 #####

st.subheader("선수 데이터 미리보기")
football_df = pd.read_csv('../data/football_eda.csv')
st.dataframe(football_df)

st.subheader("필드 포지션별 선수 수")
field_counts = football_df['Field'].value_counts().reset_index()
field_counts.columns = ['Field', 'Count']

colors = plt.cm.tab10.colors[:len(field_counts)]
fig1, ax1 = plt.subplots(figsize=(8, 5))
bars1 = ax1.bar(field_counts['Field'], field_counts['Count'], color=colors)

for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, height + 3, f'{int(height)}', ha='center', va='bottom', fontsize=10)

ax1.set_title('포지션(Field)별 선수 수', fontsize=14)
ax1.set_xlabel('Field')
ax1.set_ylabel('단위 (명)')
plt.tight_layout()
st.pyplot(fig1)

st.subheader("세부 포지션별 선수 수")
position_counts = football_df['Position'].value_counts().reset_index()
position_counts.columns = ['Position', 'Count']

fig2, ax2 = plt.subplots(figsize=(8, 6))
bars2 = ax2.barh(position_counts['Position'], position_counts['Count'], color='teal')

for bar in bars2:
    width = bar.get_width()
    ax2.text(width + 5, bar.get_y() + bar.get_height()/2, f'{int(width)}', va='center', fontsize=10)

ax2.set_title('세부 포지션(Position)별 선수 수')
ax2.set_xlabel('단위 (명)')
ax2.invert_yaxis()
plt.tight_layout()
st.pyplot(fig2)

st.subheader("필드 포지션에서 세부 포지션 분포확인")

grouped_fp = football_df.groupby(['Field', 'Position']).size().reset_index(name='Count')

ordered_fields = ['FW', 'MF', 'DF', 'GK']
colors = plt.cm.tab20.colors

fig3, axes = plt.subplots(2, 2, figsize=(10, 8))
axes = axes.flatten()
fig3.suptitle('Field별 세부 포지션 분포', fontsize=18)

def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        count = int(round(pct * total / 100.0))
        return f'{pct:.1f}%\n({count}명)'
    return my_autopct

for i, field in enumerate(ordered_fields):
    data = grouped_fp[grouped_fp['Field'] == field]
    counts = data['Count'].values
    explode = [0.08 if j == counts.argmax() else 0.05 for j in range(len(counts))]

    wedges, texts, autotexts = axes[i].pie(
        counts,
        labels=data['Position'],
        autopct=make_autopct(counts),
        colors=colors[:len(counts)],
        explode=explode,
        wedgeprops={'width': 0.7, 'edgecolor': 'w'},
        startangle=90,
        textprops={'fontsize': 11}
    )
    axes[i].set_title(field, fontsize=14)

plt.tight_layout()
plt.subplots_adjust(top=0.90)
st.pyplot(fig3)

st.subheader("국가별 등록 선수 수 Top 10 시각화")

nation_counts10 = football_df['Nation'].value_counts().head(10).reset_index()
nation_counts10.columns = ['Nation', 'Count']

fig4, ax4 = plt.subplots(figsize=(8, 5))
bars = ax4.barh(nation_counts10['Nation'], nation_counts10['Count'], color='orange')

for bar in bars:
    width = bar.get_width()
    ax4.text(width - 3, bar.get_y() + bar.get_height() / 2,
             f'{int(width)}', va='center', ha='right', fontsize=10, color='white')

ax4.set_xlabel('단위 (명)')
ax4.set_title('국가별 등록 선수 수 (Top 10)')
ax4.invert_yaxis()
plt.tight_layout()
st.pyplot(fig4)

st.subheader("국가별 등록 선수 분포 시각화 (Plotly 지도 기반 버블 차트)")

nation_counts = football_df['Nation'].value_counts().reset_index()
nation_counts.columns = ['Nation', 'Count']

fig5 = px.scatter_geo(
    nation_counts,
    locations='Nation',
    locationmode='country names',
    size='Count',
    color='Count',
    size_max=50,
    projection='natural earth',
    title='국가별 선수 분포 (Bubble Chart on Map)',
    color_continuous_scale='Plasma'
)

fig5.update_traces(hovertemplate='<b>%{location}</b><br>선수 수: %{marker.size}명')
fig5.update_layout(geo=dict(showframe=False, showcoastlines=True))
st.plotly_chart(fig5)


st.subheader("대륙(연맹)별 등록 선수 수")

confederation_counts = football_df['Confederation'].value_counts().reset_index()
confederation_counts.columns = ['Confederation', 'Count']

labels = confederation_counts['Confederation']
sizes = confederation_counts['Count']
colors = plt.cm.Set2.colors

max_index = sizes.idxmax()
explode = [0.07 if i == max_index else 0 for i in range(len(sizes))]
custom_labels = [f'{name} ({count}명)' for name, count in zip(labels, sizes)]
wedgeprops = {'width': 0.7, 'edgecolor': 'w', 'linewidth': 2}

fig6, ax6 = plt.subplots()
ax6.pie(
    sizes,
    labels=custom_labels,
    colors=colors[:len(labels)],
    autopct='%.1f%%',
    startangle=180,
    wedgeprops=wedgeprops,
    explode=explode
)
ax6.set_title('연맹(Confederation)별 등록 선수 비율', fontsize=14)
plt.tight_layout()
st.pyplot(fig6)


st.subheader("등록 선수가 가장 많은 리그 TOP 10")

league_counts20 = football_df['League'].value_counts().head(20).reset_index()
league_counts20.columns = ['League', 'Count']

Set2 = plt.cm.Set2.colors

fig7, ax7 = plt.subplots(figsize=(10, 6))
bars = ax7.barh(league_counts20['League'], league_counts20['Count'], color=Set2)

for bar in bars:
    width = bar.get_width()
    ax7.text(width + 13, bar.get_y() + bar.get_height()/2, f'{int(width)}', va='center', ha='right', color='black')

ax7.set_xlabel('단위 (명)')
ax7.set_title('리그별 등록 선수 수 (Top 20)')
ax7.invert_yaxis()
plt.tight_layout()
st.pyplot(fig7)

st.subheader("등록 선수가 가장 많은 팀 TOP 10")

club_counts10 = football_df['Club'].value_counts().head(10).reset_index()
club_counts10.columns = ['Club', 'Count']

tab10 = plt.cm.tab10.colors

fig8, ax8 = plt.subplots(figsize=(10, 6))
bars = ax8.barh(club_counts10['Club'], club_counts10['Count'], color=tab10)

for bar in bars:
    ax8.text(bar.get_width() + 0.3,
             bar.get_y() + bar.get_height()/2,
             f'{int(bar.get_width())}',
             va='center', ha='left', color='black', fontsize=10)

ax8.set_xlabel('단위 (명)')
ax8.set_title('등록 선수가 가장 많은 클럽 TOP 10')
ax8.invert_yaxis()
plt.tight_layout()
st.pyplot(fig8)


st.subheader("나이 데이터 분포 시각화")

fig9, ax9 = plt.subplots()

ax9.hist(football_df['Age'], bins=15, color='skyblue', edgecolor='black')

mean_age = football_df['Age'].mean()
median_age = football_df['Age'].median()

ax9.axvline(mean_age, color='red', linewidth=1, label=f'평균: {mean_age:.1f}세')
ax9.axvline(median_age, color='green', linewidth=1, linestyle='--', label=f'중앙값: {median_age:.1f}세')
ax9.legend()

ax9.set_title('선수 나이 분포', fontsize=14)
ax9.set_xlabel('나이 (만 나이 기준) ')
ax9.set_ylabel('단위 (명)')
ax9.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
st.pyplot(fig9)


st.subheader("무소속 선수 정보 상관관계")
# 무소속 선수만 추출
nonclub_df = football_df[football_df['Club'] == 'Without Club']
nonclub_df[['Name', 'Age', 'Position', 'Nation', 'Club', 'MarketValue','OVR']]

nonclub_df = football_df[football_df['Club'] == 'Without Club']

fig10, ax10 = plt.subplots(figsize=(7, 5))
sc = ax10.scatter(
    nonclub_df['Age'],
    nonclub_df['MarketValue'],
    s=100,
    c=nonclub_df['OVR'],
    cmap='viridis',
    edgecolors='black'
)

cbar = plt.colorbar(sc, ax=ax10)
cbar.set_label('OVR (능력치)', fontsize=12)

for age in nonclub_df['Age'].unique():
    same_age_players = nonclub_df[nonclub_df['Age'] == age]

    if len(same_age_players) == 1:
        row = same_age_players.iloc[0]
        ax10.text(row['Age'] + 0.3, row['MarketValue'], row['Name'], fontsize=9)
    else:
        sorted_players = same_age_players.sort_values(by='OVR', ascending=False).reset_index(drop=True)
        if len(sorted_players) >= 1:
            top = sorted_players.iloc[0]
            ax10.text(top['Age'] + 0.3, top['MarketValue'] - 4, top['Name'], fontsize=9)
        if len(sorted_players) >= 2:
            bottom = sorted_players.iloc[-1]
            ax10.text(bottom['Age'] + 0.3, bottom['MarketValue'] - 12, bottom['Name'], fontsize=9)

ax10.set_xlim(nonclub_df['Age'].min() - 1, 43)
ax10.set_title('무소속 선수 정보 상관관계 (나이 vs 시장 가치 vs 능력치) ', fontsize=14)
ax10.set_xlabel('나이', fontsize=12)
ax10.set_ylabel('시장 가치 (단위: 억 원)', fontsize=12)
ax10.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
st.pyplot(fig10)

st.subheader("OVR과 각 능력치 간 상관계수 계산")

stat_cols = ['PAC', 'SHO', 'PAS', 'DRI', 'DEF', 'PHY', 'OVR']
corr = football_df[stat_cols].corr()

fig11, ax11 = plt.subplots(figsize=(8, 6))
sns.heatmap(corr[['OVR']].sort_values(by='OVR', ascending=False), annot=True, cmap='coolwarm', ax=ax11)
ax11.set_title('OVR과 다른 능력치 간 상관관계')
st.pyplot(fig11)


st.subheader("필드 포지션에 따른 OVR과 세부 능력치 상관관계")

stats_cols = ['PAC', 'SHO', 'PAS', 'DRI', 'DEF', 'PHY']
positions = ['FW', 'MF', 'DF', 'GK']

fig12, axes = plt.subplots(2, 2, figsize=(12, 8), sharey=True)
axes = axes.flatten()

for idx, pos in enumerate(positions):
    sub_df = football_df[football_df['Field'] == pos]
    corr = sub_df[stats_cols + ['OVR']].corr()['OVR'].drop('OVR')
    axes[idx].plot(corr.index, corr.values, marker='o', linewidth=2)
    axes[idx].set_ylim(0, 1)
    axes[idx].set_title(f'{pos} 포지션', fontsize=13)
    axes[idx].set_ylabel('상관계수')

fig12.suptitle('필드 포지션에 따른 OVR과 세부 능력치 상관관계', fontsize=16)
plt.tight_layout()
st.pyplot(fig12)


st.subheader("주요 리그별 OVR 분포")

top_leagues = football_df['League'].value_counts().nlargest(6).index

fig13, ax13 = plt.subplots(figsize=(8, 5))

sns.boxplot(
    data=football_df[football_df['League'].isin(top_leagues)],
    x='League',
    y='OVR',
    hue='League',
    palette='Set2',
    showfliers=False,
    dodge=False,
    legend=False,
    ax=ax13
)

sns.stripplot(
    data=football_df[football_df['League'].isin(top_leagues)],
    x='League',
    y='OVR',
    color='black',
    size=2,
    jitter=True,
    alpha=0.4,
    ax=ax13
)

ax13.set_title('리그별 OVR 분포 (박스+스트립)', fontsize=14)
plt.tight_layout()
st.pyplot(fig13)

st.subheader("필드 포지션별 OVR(능력치) 분포")

fig14, ax14 = plt.subplots()

sns.boxplot(
    data=football_df,
    x='Field',
    y='OVR',
    hue='Field',
    palette='tab10',
    showfliers=False,
    ax=ax14
)

sns.stripplot(
    data=football_df,
    x='Field',
    y='OVR',
    color='black',
    size=1.5,
    jitter=True,
    alpha=0.3,
    ax=ax14
)

ax14.set_title('필드 포지션별 OVR(능력치) 분포')
ax14.set_ylabel('OVR')
plt.tight_layout()
st.pyplot(fig14)

st.subheader("필드 포지션별 PAC(속도)능력치 분포")

fig15, ax15 = plt.subplots()

sns.boxplot(
    data=football_df,
    x='Field',
    y='PAC',
    hue='Field',
    palette='tab10',
    showfliers=False,
    ax=ax15
)

sns.stripplot(
    data=football_df,
    x='Field',
    y='PAC',
    color='black',
    size=1.5,
    jitter=True,
    alpha=0.3,
    ax=ax15
)

ax15.set_title('필드 포지션별 PAC(속도) 능력치 분포')
ax15.set_ylabel('PAC (속도)')
plt.tight_layout()
st.pyplot(fig15)


st.subheader("필드 포지션별 PHY(몸싸움) 능력치 분포")

fig16, ax16 = plt.subplots()

sns.boxplot(
    data=football_df,
    x='Field',
    y='PHY',
    hue='Field',
    palette='tab10',
    showfliers=False,
    ax=ax16
)

sns.stripplot(
    data=football_df,
    x='Field',
    y='PHY',
    color='black',
    size=1.5,
    jitter=True,
    alpha=0.3,
    ax=ax16
)

ax16.set_title('필드 포지션별 PHY(몸싸움) 능력치 분포')
ax16.set_ylabel('PHY(몸싸움)')
plt.tight_layout()
st.pyplot(fig16)


st.subheader("국가별 평균 MarketValue 계산")

nation_value = football_df.groupby('Nation')['MarketValue'].mean().reset_index()
nation_value.columns = ['Nation', 'AvgMarketValue']

fig17 = px.scatter_geo(
    nation_value,
    locations='Nation',
    locationmode='country names',
    size='AvgMarketValue',
    color='AvgMarketValue',
    size_max=50,
    projection='natural earth',
    title='국가 별 선수 평균 시장 가치 (Transfermarkt 기준)',
    color_continuous_scale='Viridis'
)

fig17.update_traces(hovertemplate='<b>%{location}</b><br>선수 평균가치: 약 %{marker.size:.2f}억 원')
fig17.update_layout(geo=dict(showframe=False, showcountries=True, showcoastlines=True))
st.plotly_chart(fig17)

st.subheader("국가별 선수 총 시장 누적가치 (Transfermarkt 기준)")

nation_value_sum = football_df.groupby('Nation')['MarketValue'].sum().reset_index()
nation_value_sum.columns = ['Nation', 'TotalMarketValue']
nation_value_sum['TotalMarketValue_str'] = nation_value_sum['TotalMarketValue'].apply(lambda x: f"{x:,.2f}")

fig18 = px.scatter_geo(
    nation_value_sum,
    locations='Nation',
    locationmode='country names',
    size='TotalMarketValue',
    color='TotalMarketValue',
    size_max=60,
    projection='natural earth',
    title='국가별 선수 총 시장 누적가치 (Transfermarkt 기준)',
    color_continuous_scale='Turbo'
)

fig18.update_traces(
    customdata=nation_value_sum[['TotalMarketValue_str']],
    hovertemplate='<b>%{location}</b><br>총 시장 가치: %{customdata[0]}억 원'
)

fig18.update_layout(geo=dict(showframe=False, showcountries=True, showcoastlines=True))
st.plotly_chart(fig18)


st.subheader("평균 MarketValue 상위 5개 리그 선택")

league_value_avg = football_df.groupby('League')['MarketValue'].mean().reset_index()
league_value_avg.columns = ['League', 'AvgMarketValue']
top_avg_leagues = league_value_avg.sort_values(by='AvgMarketValue', ascending=False).head(5)

fig19, ax19 = plt.subplots(figsize=(10, 6))
sns.barplot(
    data=top_avg_leagues,
    x='League',
    y='AvgMarketValue',
    hue='League',
    palette='tab10',
    dodge=False,
    legend=False,
    ax=ax19
)

ax19.set_title('리그별 평균 시장 가치 TOP 5 (Transfermarkt 기준)', fontsize=16)
ax19.set_xlabel('리그')
ax19.set_ylabel('평균 시장 가치 (억 원)')
plt.tight_layout()
st.pyplot(fig19)

st.subheader("나이별 평균 MarketValue 계산")

age_value_avg = football_df.groupby('Age')['MarketValue'].mean().reset_index()

fig21, ax21 = plt.subplots(figsize=(10, 6))
ax21.plot(age_value_avg['Age'], age_value_avg['MarketValue'], marker='o', linewidth=2, label='평균 시장 가치')
ax21.scatter(age_value_avg['Age'], age_value_avg['MarketValue'], color='orange', s=40)

ax21.set_title('나이별 평균 시장 가치 (Transfermarkt 기준)', fontsize=14)
ax21.set_xlabel('나이 (만 나이 기준)')
ax21.set_ylabel('평균 시장 가치 (억 원)')
ax21.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
st.pyplot(fig21)


st.subheader("포지션 (Field)별 평균 선수가치")

fig22, ax22 = plt.subplots(figsize=(8, 6))
sns.barplot(data=football_df, x='Field', y='MarketValue', estimator='mean', ax=ax22)

ax22.set_title('포지션 (Field)별 평균 선수가치')
ax22.set_xlabel('필드 포지션')
ax22.set_ylabel('이적료 (억원)')
st.pyplot(fig22)


st.subheader("포지션별 평균 시장 가치 및 선수 수 계산")

custom_order = [
    'Striker', 'Right_Winger', 'Left_Winger', 'Attacking_Midfielder',
    'Central_Midfielder', 'Side_Midfielder', 'Defensive_Midfielder',
    'Centre_Back', 'Right_Back', 'Left_Back', 'Goalkeeper'
]

position_value = football_df.groupby('Position').agg(
    AvgMarketValue=('MarketValue', 'mean'),
    PlayerCount=('MarketValue', 'count')
).reset_index()

position_value['Position'] = pd.Categorical(position_value['Position'], categories=custom_order, ordered=True)
position_value = position_value.sort_values('Position')

fig23 = px.scatter(
    position_value,
    x='Position',
    y='AvgMarketValue',
    size='PlayerCount',
    color='Position',
    hover_name='Position',
    size_max=60,
    title='포지션별 평균 시장 가치 (Transfermarkt 기준)'
)

fig23.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
fig23.update_layout(
    xaxis_title='포지션',
    yaxis_title='평균 시장 가치 (억 원)',
    title_font_size=16,
    showlegend=False
)

st.plotly_chart(fig23)


st.subheader("1. 산점도로 OVR vs MarketValue 비교")

plot_df = football_df[['Name', 'Position', 'Age', 'Nation', 'Club', 'OVR', 'MarketValue']].copy()
plot_df['customdata'] = plot_df[['Name', 'Position', 'Age', 'Nation', 'Club']].values.tolist()

fig25 = px.scatter(
    plot_df,
    x='OVR',
    y='MarketValue',
    color='Position',
    title='시장가치 vs 종합능력치 산점도 (Transfermarkt 기준)',
    labels={'OVR': 'OVR (종합 능력치)', 'MarketValue': 'MarketValue (억 원)'},
    opacity=0.6,
    width=900,
    height=600
)

fig25.update_traces(
    marker=dict(size=8, line=dict(width=0.5, color='DarkSlateGrey')),
    customdata=plot_df[['Name', 'Position', 'Age', 'Nation', 'Club']],
    hovertemplate=(
        '<b>%{customdata[0]}</b><br>' +
        '나이: %{customdata[2]}<br>' +
        '국적: %{customdata[3]}<br>' +
        '소속 클럽: %{customdata[4]}<br>' +
        '포지션: %{customdata[1]}<br>' +
        'OVR: %{x}<br>' +
        '시장가치: 약 %{y}억 원<extra></extra>'
    )
)

fig25.update_layout(title_font_size=16, showlegend=False)
st.plotly_chart(fig25)


st.subheader("2. OVR 순위 vs MarketValue 순위 비교하여 랭킹 차이 계산")

st.markdown("""
- **RANK_GAP > 0**: OVR이 높지만 MarketValue가 낮은 선수 → **저평가 선수 (undervalued)**  
- **RANK_GAP < 0**: MarketValue가 OVR보다 높은 선수 → **고평가 선수 (overvalued)**  
""")

ranked_df = football_df.copy()

ranked_df['OVR_Rank'] = ranked_df['OVR'].rank(method='min', ascending=False).astype(int)
ranked_df['Value_Rank'] = ranked_df['MarketValue'].rank(method='min', ascending=False).astype(int)

ranked_df['Rank_Gap'] = ranked_df['Value_Rank'] - ranked_df['OVR_Rank']
ranked_df['Status'] = ranked_df['Rank_Gap'].apply(lambda x: 'under-valued' if x > 0 else ('over-valued' if x < 0 else 'suitable'))

overvalued_df = ranked_df.sort_values(by='Rank_Gap', ascending=True)
undervalued_df = ranked_df.sort_values(by='Rank_Gap', ascending=False)

fig26, ax26 = plt.subplots(figsize=(10, 5))
sns.histplot(ranked_df['Rank_Gap'], bins=30, kde=True, color='skyblue', ax=ax26)
ax26.axvline(0, color='red', linestyle='--')
ax26.set_title('[FC25 온라인 종합능력치(OVR) vs Transfermarkt기준 시장가치] 간격 차이 분포 (=Rank Gap)', fontsize=14)
ax26.set_xlabel('시장가치 고평가 선수                  Rank_Gap                  시장가치 저평가 선수')
ax26.set_ylabel('인원 (명)')
plt.tight_layout()
st.pyplot(fig26)

st.subheader("고평가 선수 TOP 10 (Rank_Gap 가장 낮은 선수)")

overvalued_top10 = ranked_df.sort_values(by='Rank_Gap').head(10)
st.dataframe(overvalued_top10[['Name', 'Age', 'Club', 'Field', 'OVR', 'MarketValue',
                               'OVR_Rank', 'Value_Rank', 'Rank_Gap', 'Status']])

st.subheader("저평가 선수 TOP 10 (Rank_Gap 가장 높은 선수)")

undervalued_top10 = ranked_df.sort_values(by='Rank_Gap', ascending=False).head(10)
st.dataframe(undervalued_top10[['Name', 'Age', 'Club', 'Field', 'OVR', 'MarketValue',
                                 'OVR_Rank', 'Value_Rank', 'Rank_Gap', 'Status']])


st.subheader("OVR 상위/하위 50명의 고평가·저평가 상태 분포")

high_value_players = ranked_df.sort_values('MarketValue', ascending=False).head(50)
low_value_players = ranked_df.sort_values('MarketValue', ascending=True).head(50)

high_counts = high_value_players['Status'].value_counts().reset_index()
high_counts.columns = ['Status', 'Count']
high_counts['Group'] = 'OVR 상위 50명'

low_counts = low_value_players['Status'].value_counts().reset_index()
low_counts.columns = ['Status', 'Count']
low_counts['Group'] = 'OVR 하위 50명'

status_compare_df = pd.concat([high_counts, low_counts])

fig27, ax27 = plt.subplots(figsize=(8, 6))
sns.barplot(data=status_compare_df, x='Group', y='Count', hue='Status', palette='Set2', ax=ax27)

ax27.set_title('OVR 상위/하위 50명의 고평가·저평가 상태 분포', fontsize=14)
ax27.set_xlabel('선수 그룹')
ax27.set_ylabel('선수 수')
ax27.legend(title='평가 상태')
plt.tight_layout()
st.pyplot(fig27)


st.subheader("주목할 만한 선수 조건")

ovr_top_20 = ranked_df['OVR_Rank'].quantile(0.2)
value_top_20 = ranked_df['Value_Rank'].quantile(0.2)

notable_df = ranked_df[
    (ranked_df['OVR_Rank'] <= ovr_top_20) &
    (ranked_df['Value_Rank'] <= value_top_20) &
    (ranked_df['Rank_Gap'] >= 100)
]

hover_template = (
    '<b>%{customdata[0]}</b><br>' +
    '나이: %{customdata[2]}<br>' +
    '국적: %{customdata[3]}<br>' +
    '소속 클럽: %{customdata[4]}<br>' +
    '포지션: %{customdata[1]}<br>' +
    'OVR: %{x}<br>' +
    '시장가치: 약 %{y}억 원<br>' +
    '랭크 차이: %{customdata[5]}<extra></extra>'
)

fig29 = px.scatter(
    ranked_df,
    x='OVR',
    y='MarketValue',
    size='MarketValue',
    color='Status',
    custom_data=ranked_df[['Name', 'Position', 'Age', 'Nation', 'Club', 'Rank_Gap']],
    title='Rank_Gap 주목할 선수 시각화',
    opacity=0.5,
)

fig29.update_traces(
    hovertemplate=hover_template,
    hoverlabel=dict(
        bgcolor='black',
        font=dict(color='white', size=13)
    )
)

notable_scatter = px.scatter(
    notable_df,
    x='OVR',
    y='MarketValue',
    custom_data=notable_df[['Name', 'Position', 'Age', 'Nation', 'Club', 'Rank_Gap']]
)

notable_scatter.update_traces(
    marker=dict(size=12, color='red', line=dict(width=2, color='darkred')),
    hovertemplate=hover_template,
    showlegend=False
)

fig29.add_trace(notable_scatter.data[0])

fig29.update_layout(
    xaxis_title='OVR (종합 능력치)',
    yaxis_title='시장 가치 (억 원)',
    title_font_size=16
)

st.plotly_chart(fig29)
st.markdown(""" 
- **OVR과 MarketValue가 모두 상위권인데 Rank_Gap이 크다면?**  
  → 잠재적으로 시장에서 충분히 반영되지 않은 **주목할 선수**로 간주할 수 있음
   
  **🔍 상위권인데도 Rank_Gap이 큰 경우의 특징**
  - 나이 많음 → 시장 가치가 떨어짐
  - 포지션 특성상 가치가 낮게 책정됨 (예: GK, 수비수)
  - 계약 기간이 얼마 안 남음
  - 부상 이력 등 비정량적 요소 존재 가능  
""")