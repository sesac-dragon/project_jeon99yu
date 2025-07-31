import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from unidecode import unidecode

### 카테고리 별 크롤링 코드 시작 ###

# 1. 포지션별 선수가치

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

position_urls = {
    'forwards': 'Sturm',
    'midfielders': 'Mittelfeld',
    'defenders': 'Abwehr',
    'goalkeepers': 'Torwart'
}

all_positions = []

for position_key, position_value in position_urls.items():
    for page in range(1, 21): 
        url = f'https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop/plus/ausrichtung/{position_value}/spielerposition_id/alle/altersklasse/alle/jahrgang/0/land_id/0/kontinent_id/0/yt0/Anzeigen/0//page/{page}?ajax=yw1'
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        player_info = soup.find_all('tr', {'class': ['odd', 'even']})

        for info in player_info:
            player = info.find_all('td')
            all_positions.append({
                'name': unidecode(player[3].text.strip()),
                'position': player[4].text.strip(),
                'age': player[5].text.strip(),
                'nation': player[6].img['alt'] if player[6].find('img') else '',
                'club': player[7].img['alt'] if player[7].find('img') else '',
                'value': player[8].text.strip()
                })

positions_df = pd.DataFrame(all_positions)
positions_df = positions_df.drop_duplicates()

positions_df.to_csv('../data/tfm_positions.csv', index=False, encoding='utf-8-sig')
positions_df


# 2. 연령대별 선수가치

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

age_groups = ['u21', '23-30', 'o34']
all_players = []

for age_group in age_groups:
    for page in range(1, 21):
        url = f'https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop/plus/ausrichtung/alle/spielerposition_id/alle/altersklasse/{age_group}/jahrgang/0/land_id/0/kontinent_id/0/yt0/Anzeigen/0//page/{page}?ajax=yw1'
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        player_info = soup.find_all('tr', {'class': ['odd', 'even']})

        for info in player_info:
            player = info.find_all('td')
            if len(player) < 9:
                continue

            all_players.append({
                'name': unidecode(player[3].text.strip()),
                'position': player[4].text.strip(),
                'age': player[5].text.strip(),
                'nation': player[6].img['alt'] if player[6].find('img') else '',
                'club': player[7].img['alt'] if player[7].find('img') else '',
                'value': player[8].text.strip()
            })

        time.sleep(1) 

age_group_df = pd.DataFrame(all_players)
age_group_df = age_group_df.drop_duplicates(subset=['name', 'club']) 

age_group_df.to_csv('../data/tfm_age.csv', index=False, encoding='utf-8-sig')
age_group_df


# 3. 대륙(연맹) 별 선수가치

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

confederation_ids = {
    'UEFA': 1, # 유럽 축구 연맹
    'AFC': 2, # 아시아 축구 연맹
    'CAF': 3, # 아프리카 축구 연맹
    'CONCACAF': 4, # 북중미 축구 연맹
    'CONMEBOL': 5, # 남미 축구 연맹
    'OFC': 6 # 오세아니아 축구 연맹
}

confederation = []

for confederation_key, kontinent_id in confederation_ids.items():
    for page in range(1, 21):
        url = f'https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop/plus/ausrichtung/alle/spielerposition_id/alle/altersklasse/alle/jahrgang/0/land_id/0/kontinent_id/{kontinent_id}/yt0/Anzeigen/0//page/{page}?ajax=yw1'
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        player_info = soup.find_all('tr', {'class': ['odd', 'even']})

        for info in player_info:
            player = info.find_all('td')
            confederation.append({
                'name': unidecode(player[3].text.strip()),
                'position': player[4].text.strip(),
                'age': player[5].text.strip(),
                'nation': player[6].find('img').get('alt') if player[6].find('img') else '',
                'club': player[7].find('img').get('alt') if player[7].find('img') else '',
                'value': player[8].text.strip(),
                'confederation': confederation_key
                })

confederation_df = pd.DataFrame(confederation)
confederation_df = confederation_df.drop_duplicates()

confederation_df.to_csv('../data/tfm_confederation.csv', index=False, encoding='utf-8-sig')
confederation_df


# 4. 기타리그 별 선수가치

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

league_codes = {
    'MLS': 'MLS1',  # 미국 리그
    'Championship': 'GB2', # 잉글랜드 2부리그
    'Eredivisie': 'NL1',  # 네덜란드 리그
    'SuperLig': 'TR1',  # 튀르키예 리그
    'Scottish_Premiership': 'SC1',  # 스코틀랜드 리그
    'Swiss_SuperLeague': 'C1',  # 스위스 리그
    'Austria_Bundesliga': 'A1',  # 오스트리아 리그
    'Danish_Superligaen': 'DK1',  # 덴마크 리그
    'Saudi_ProLeague': 'SA1',  # 사우디아라비아 리그
    'Liga_Portugal': 'PO1',  # 포르투갈 리그
    'Russian_PremierLiga': 'RU1',  # 러시아 리그
    'Brasileiro_SerieA': 'BRA1',  # 브라질 리그
    'Liga_Profesional': 'ARGC',  # 아르헨티나 리그
    'Liga_MX': 'MEXA',  # 멕시코 리그
    'Jupiler_ProLeague': 'BE1',  # 벨기에 리그
    'SuperLeague1': 'GR1',  # 그리스 리그
    'A_League': 'AUS1',  # 호주 리그
    'J1_League': 'JAP1',  # 일본 리그
    'K_League1': 'RSK1',  # K리그
    'Chinese_SuperLeague': 'CSL'  # 중국 리그
}

other_leagues = []

for league_name, code in league_codes.items():
    for page in range(1, 5):
        url = f'https://www.transfermarkt.com/jumplist/marktwerte/wettbewerb/{code}/page/{page}?ajax=yw1'
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        player_info = soup.find_all('tr', class_=['odd', 'even'])

        for info in player_info:
            try:
                inline_table = info.find('table', class_='inline-table')
                name = position = ''
                
                if inline_table:
                    trs = inline_table.find_all('tr')
                    name_tag = trs[0].find('a') if len(trs) > 0 else None
                    name = name_tag.text.strip() if name_tag else ''
                    name = unidecode(name)
                    
                    position_td = trs[1].find('td') if len(trs) > 1 else None
                    position = position_td.text.strip() if position_td else ''

                tds = info.find_all('td', class_='zentriert')
                age = nation = club = ''
                
                for td in tds:
                    if td.text.strip().isdigit():
                        age = td.text.strip()
                    elif td.find('img') and 'flaggenrahmen' in td.find('img').get('class', []):
                        nation_img = td.find('img')
                        nation = nation_img['alt'] if nation_img and nation_img.has_attr('alt') else ''
                    elif td.find('img'):
                        club_img = td.find('img')
                        club = club_img['alt'] if club_img and club_img.has_attr('alt') else ''

                value_td = info.find('td', class_='rechts hauptlink')
                value_tag = value_td.find('a') if value_td else None
                value = value_tag.text.strip() if value_tag else value_td.text.strip() if value_td else ''

                other_leagues.append({
                    'name': name,
                    'position': position,
                    'age': age,
                    'nation': nation,
                    'club': club,
                    'value': value,
                    'league': league_name
                })

            except Exception as e:
                print(f"[Error] {e}")

        time.sleep(1)

other_leagues_df = pd.DataFrame(other_leagues)
other_leagues_df = other_leagues_df[other_leagues_df['name'].str.strip() != '']

other_leagues_df.to_csv('../data/tfm_otherleagues.csv', index=False, encoding='utf-8-sig')
other_leagues_df

### 카테고리 별 크롤링 코드 종료 ###

### 최종 병합과정 시작 ###

# 1차 병합. positions_df + age_group_df 병합과정

merged1_df = pd.concat([positions_df, age_group_df], ignore_index=True)
duplicate_rows = pd.merge(positions_df, age_group_df, on=['name', 'position', 'age', 'nation', 'club', 'value'])
print(f'positions_df 수: {len(positions_df)}, age_group_df 수: {len(age_group_df)}, 중복 데이터 수: {len(duplicate_rows)}')

merged1_df = merged1_df.drop_duplicates()
merged1_df

# 2차 병합. (positions_df + age_group_df) + confederation_df 병합과정

confederation_df = confederation_df.reset_index(drop=True) # 인덱스 초기화
merged1_df = merged1_df.reset_index(drop=True)

key_cols = ['name', 'position', 'age', 'nation', 'club', 'value']
for col in key_cols:
    if col in confederation_df.columns and col in merged1_df.columns:
        if col == 'age':
            confederation_df[col] = pd.to_numeric(confederation_df[col], errors='coerce')
            merged1_df[col] = pd.to_numeric(merged1_df[col], errors='coerce')
        else:
            confederation_df[col] = confederation_df[col].astype(str)
            merged1_df[col] = merged1_df[col].astype(str)

columns_order = ['name', 'position', 'age', 'nation', 'club', 'value', 'confederation', 'league'] # 컬럼 순서 이거로 정렬
for col in columns_order: 
    if col not in confederation_df.columns:
        confederation_df[col] = None
    if col not in merged1_df.columns:
        merged1_df[col] = None
confederation_df = confederation_df[columns_order]

merged1_df = merged1_df[columns_order]
merged2_df = pd.concat([confederation_df, merged1_df], ignore_index=True)


duplicate2_rows = pd.merge(confederation_df, merged1_df, on=key_cols) # 중복 데이터 찾기
print(f'confederation_df 수: {len(confederation_df)}, pos+ages수: {len(merged1_df)}, 중복 데이터 수: {len(duplicate2_rows)}')

merged2_df = merged2_df.sort_values(by='confederation', ascending=False)
merged2_df = merged2_df.drop_duplicates(subset=key_cols)

merged2_df

# 3차 병합. (positions_df + age_group_df + confederation_df) + other_leagues_df 병합과정

other_leagues_df = other_leagues_df.reset_index(drop=True) # 인덱스 초기화
merged2_df = merged2_df.reset_index(drop=True)

key_cols = ['name', 'position', 'age', 'nation', 'club', 'value'] # 병합 기준 key 컬럼
for col in key_cols:
    if col in merged2_df.columns and col in other_leagues_df.columns:
        if col == 'age':
            merged2_df[col] = pd.to_numeric(merged2_df[col], errors='coerce')
            other_leagues_df[col] = pd.to_numeric(other_leagues_df[col], errors='coerce')
            
            merged2_df = merged2_df.dropna(subset=['age'])
            other_leagues_df = other_leagues_df.dropna(subset=['age'])
            merged2_df['age'] = merged2_df['age'].astype(int)
            other_leagues_df['age'] = other_leagues_df['age'].astype(int)
        else:
            merged2_df[col] = merged2_df[col].astype(str)
            other_leagues_df[col] = other_leagues_df[col].astype(str)

duplicate3_rows = pd.merge(merged2_df, other_leagues_df, on=key_cols)
print(f'other_leagues_df 수: {len(other_leagues_df)}, (pos+ages+confs) 수: {len(merged2_df)}, 중복 데이터 수: {len(duplicate3_rows)}')

transfermarkt_df = pd.concat([merged2_df, other_leagues_df], ignore_index=True)
transfermarkt_df = transfermarkt_df.drop_duplicates(subset=key_cols)

transfermarkt_df.to_csv('../data/tfm_totaldata.csv', index=False, encoding='utf-8-sig')
transfermarkt_df

### 최종 병합과정 종료 ###

