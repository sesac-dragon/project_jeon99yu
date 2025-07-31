import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from unidecode import unidecode

# 한글 → 영어 국가명 표준화 변환 사전작업
nation_kr2en = {
    '가나': 'Ghana', '가봉': 'Gabon', '가이아나': 'Guyana', '감비아': 'Gambia', '과테말라': 'Guatemala',
    '그레나다': 'Grenada', '그리스': 'Greece', '기니': 'Guinea', '기니비사우': 'Guinea-Bissau',
    '나이지리아': 'Nigeria', '남아프리카공화국': 'South Africa', '뉴질랜드': 'New Zealand',
    '대만': 'Chinese Taipei', '덴마크': 'Denmark', '도미니카공화국': 'Dominican Republic',
    '라이베리아': 'Liberia', '러시아': 'Russia', '루마니아': 'Romania', '룩셈부르크': 'Luxembourg',
    '리비아': 'Libya', '마다가스카르': 'Madagascar', '말라위': 'Malawi', '말리': 'Mali', '멕시코': 'Mexico',
    '모리타니아': 'Mauritania', '모잠비크': 'Mozambique', '몬테네그로': 'Montenegro',
    '몰도바': 'Moldova', '몰타': 'Malta', '바레인': 'Bahrain', '바누아투': 'Vanuatu',
    '방글라데시': 'Bangladesh', '베냉': 'Benin', '베네수엘라': 'Venezuela', '벨라루스': 'Belarus',
    '보스니아헤르체고비나': 'Bosnia-Herzegovina', '볼리비아': 'Bolivia', '부룬디': 'Burundi',
    '부르키나파소': 'Burkina Faso', '북마리아나 제도': 'Northern Mariana Islands',
    '북마케도니아': 'North Macedonia', '북아일랜드': 'Northern Ireland', '불가리아': 'Bulgaria',
    '사우디아라비아': 'Saudi Arabia', '산마리노': 'San Marino', '상투메 프린시페': 'São Tomé and Príncipe',
    '세르비아': 'Serbia', '세이셸': 'Seychelles', '소말리아': 'Somalia', '수단': 'Sudan',
    '수리남': 'Suriname', '스웨덴': 'Sweden', '스위스': 'Switzerland', '스코틀랜드': 'Scotland',
    '슬로바키아': 'Slovakia', '슬로베니아': 'Slovenia', '시에라리온': 'Sierra Leone',
    '시리아': 'Syria', '아랍에미리트': 'United Arab Emirates', '아르메니아': 'Armenia',
    '아제르바이잔': 'Azerbaijan', '아이슬란드': 'Iceland', '아이티': 'Haiti', '아일랜드': 'Ireland',
    '아프가니스탄': 'Afghanistan', '알바니아': 'Albania', '알제리': 'Algeria', '앙골라': 'Angola',
    '에리트레아': 'Eritrea', '에스토니아': 'Estonia', '에스와티니': 'Eswatini', '세인트키츠네비스': 'Saint Kitts and Nevis',
    '에콰도르': 'Ecuador', '오만': 'Oman', '오스트리아': 'Austria', '온두라스': 'Honduras',
    '요르단': 'Jordan', '우간다': 'Uganda', '우즈베키스탄': 'Uzbekistan', '우크라이나': 'Ukraine',
    '웨일스': 'Wales', '이라크': 'Iraq', '이란': 'Iran', '이스라엘': 'Israel', '이집트': 'Egypt',
    '이탈리아': 'Italy', '인도네시아': 'Indonesia', '일본': 'Japan', '자메이카': 'Jamaica',
    '잠비아': 'Zambia', '조지아': 'Georgia', '중국': 'China', '중앙아프리카공화국': 'Central African Republic',
    '짐바브웨': 'Zimbabwe', '체코': 'Czech Republic', '차드': 'Chad', '칠레': 'Chile',
    '카메룬': 'Cameroon', '카보베르데': 'Cape Verde', '카타르': 'Qatar', '캐나다': 'Canada',
    '캄보디아': 'Cambodia', '케냐': 'Kenya', '코모로': 'Comoros', '코소보': 'Kosovo',
    '코스타리카': 'Costa Rica', '코트디부아르': "Cote d'Ivoire", '콜롬비아': 'Colombia',
    '콩고': 'Congo', '쿠바': 'Cuba', '쿡 제도': 'Cookinseln', '쿠웨이트': 'Kuwait',
    '퀴라소': 'Curaçao', '키프로스': 'Cyprus', '키르기스스탄': 'Kyrgyzstan', '타지키스탄': 'Tajikistan',
    '탄자니아': 'Tanzania', '태국': 'Thailand', '터키': 'Turkey', '토고': 'Togo',
    '토켈라우': 'Tokelau', '투르크메니스탄': 'Turkmenistan', '튀니지': 'Tunisia',
    '트리니다드토바고': 'Trinidad and Tobago', '파나마': 'Panama', '파라과이': 'Paraguay',
    '파키스탄': 'Pakistan', '팔레스타인': 'Palestine', '페루': 'Peru', '포르투갈': 'Portugal',
    '폴란드': 'Poland', '프랑스': 'France', '핀란드': 'Finland', '필리핀': 'Philippines',
    '헝가리': 'Hungary', '호주': 'Australia', '홍콩': 'Hong Kong', '예멘': 'Yemen',
    '르완다': 'Rwanda', '레바논': 'Lebanon', '라트비아': 'Latvia', '리투아니아': 'Lithuania',
    '남수단': 'South Sudan', '괌': 'Guam', '나미비아': 'Namibia', '니제르': 'Niger',
    '리비아': 'Libya', '라이베리아': 'Liberia', '도미니카 연방': 'Dominica', '스리랑카': 'Sri Lanka',
    '적도 기니': 'Equatorial Guinea', '상투메 프린시페': 'São Tomé and Príncipe',
    '산마리노': 'San Marino', '세이셸': 'Seychelles', '인도': 'India','우루과이': 'Uruguay',
    '독일': 'Germany', '아르헨티나': 'Argentina', '네덜란드': 'Netherlands', '스페인': 'Spain',
    '노르웨이': 'Norway', '벨기에': 'Belgium', '크로아티아': 'Croatia', '모로코': 'Morocco',
    '세네갈': 'Senegal', '잉글랜드': 'England', '대한민국': 'Korea, South', '북한': 'Korea, North',
    '브라질': 'Brazil', '우루과이': 'Uruguay', '세네갈': 'Senegal', '미국': 'United States' , 
    '엘살바도르': 'El Salvador', '카보베르데': 'Cape Verde', '푸에르토리코': 'Puerto Rico'
}

# FC 온라인 크롤링코드 

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

fifa25_data = []

for page in range(1, 161):  
    url = f'https://www.ea.com/ko/games/ea-sports-fc/ratings?gender=0&orderBy=rank&page={page}'
    res = requests.get(url, headers=headers)
    time.sleep(1)  # 이미지 alt 누락 방지
    
    soup = BeautifulSoup(res.content, 'html.parser')
    players = soup.select('tbody tr')

    for p in players:
        tds = p.find_all('td')
        if len(tds) < 12:
            continue

        profile = p.select_one('div.Table_profileContent__0t2_u')
        name = re.sub(r'^#\d+', '', profile.text.strip()) if profile else ''
        name = unidecode(name)  # <- 라틴 문자 제거하여 영어 ASCII 표기로 변환

        # 국가명 추출 및 영문변환
        nation_img = tds[2].select_one('img')
        nation_kr = nation_img['alt'].strip().replace(' ', '') if nation_img and 'alt' in nation_img.attrs else ''
        nation = nation_kr2en.get(nation_kr, nation_kr)
        
        club_img = tds[3].select_one('img')
        club = club_img['alt'].strip() if club_img and 'alt' in club_img.attrs else ''

        # 능력치 표기 통일 함수
        def stats(td):
            stat_span = td.select_one('span.Table_statCellValue__zn5Cx')
            if stat_span: 
                return stat_span.text.strip()[:2] # 능력치에서 라이브 스텟 제거
            return ''

        fifa25_data.append({
            'name': name,
            'nation': nation,
            'club': club,
            'position': tds[4].text.strip(),
            'OVR': stats(tds[5]),
            'PAC': stats(tds[6]),
            'SHO': stats(tds[7]),
            'PAS': stats(tds[8]),
            'DRI': stats(tds[9]),
            'DEF': stats(tds[10]),
            'PHY': stats(tds[11]),
        })

fc25_df = pd.DataFrame(fifa25_data)
fc25_df.to_csv('../data/fc25_playerdata.csv', index=False, encoding='utf-8-sig')
fc25_df



