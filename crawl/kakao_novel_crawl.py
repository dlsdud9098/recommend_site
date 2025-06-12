from playwright.sync_api import sync_playwright
import json
import requests
import time
import os
import json
from fake_useragent import UserAgent
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio
from playwright.async_api import async_playwright
import random
import asyncio
import pandas as pd
from itertools import chain

def get_session_info():
    """페이지 방문해서 세션 정보 가져오기"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        page.goto('https://page.kakao.com/menu/10011/screen/84')
        page.wait_for_load_state('networkidle')
        
        cookies = page.context.cookies()
        user_agent = page.evaluate('navigator.userAgent')
        
        browser.close()
    
    return cookies, user_agent

def crawl_novels_with_requests():
    """requests를 사용해서 직접 GraphQL API 호출"""
    print("세션 정보 가져오는 중...")
    cookies, user_agent = get_session_info()
    
    session = requests.Session()
    
    # 쿠키 설정
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    
    headers = {
        'User-Agent': user_agent,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Referer': 'https://page.kakao.com/',
        'Origin': 'https://page.kakao.com',
        'sec-ch-ua': '"Not.A/Brand";v="99", "Chromium";v="136"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"'
    }
    
    # GraphQL 쿼리 (원본에서 추출)
    query = """
    query staticLandingGenreSection($sectionId: ID!, $param: StaticLandingGenreParamInput!) {
      staticLandingGenreSection(sectionId: $sectionId, param: $param) {
        ...Section
      }
    }
    
    fragment Section on Section {
      id
      uid
      type
      title
      ... on StaticLandingGenreSection {
        isEnd
        totalCount
        param {
          categoryUid
          subcategory {
            name
            param
          }
          sortType {
            name
            param
          }
          page
          isComplete
          screenUid
        }
      }
      groups {
        ...Group
      }
    }
    
    fragment Group on Group {
      id
      type
      dataKey
      items {
        ...Item
      }
    }
    
    fragment Item on Item {
      id
      type
      ...PosterViewItem
      ...CardViewItem
    }
    
    fragment PosterViewItem on PosterViewItem {
      id
      type
      scheme
      title
      altText
      thumbnail
      badgeList
      ageGradeBadge
      statusBadge
      subtitleList
      rank
      rankVariation
      ageGrade
      selfCensorship
      seriesId
      showDimmedThumbnail
      discountRate
      discountRateText
    }
    
    fragment CardViewItem on CardViewItem {
      title
      altText
      thumbnail
      scheme
      badgeList
      ageGradeBadge
      statusBadge
      ageGrade
      selfCensorship
      subtitleList
      caption
      rank
      rankVariation
      isEventBanner
      categoryType
      discountRate
      discountRateText
      backgroundColor
      isBook
      isLegacy
    }
    """
    
    all_novels = []
    page_num = 1
    
    # ===============================================
    # 🔧 여기서 최대 페이지 수정하세요!
    # ===============================================
    max_pages = None     # None = 자동 계산 (전체)
    # max_pages = 50     # 50페이지만 수집
    # max_pages = 100    # 100페이지만 수집  
    # max_pages = 500    # 500페이지만 수집
    
    # 사용자 확인 받을 임계값 (이 페이지 수 이상이면 확인 요청)
    confirmation_threshold = 100
    
    failed_requests = 0
    max_failures = 3  # 연속 실패 허용 횟수
    
    print("소설 데이터 수집 시작...")
    print("⚠️  안전한 크롤링을 위해 각 요청 사이에 2-5초씩 대기합니다.")
    
    while (max_pages is None or page_num <= max_pages) and failed_requests < max_failures:
    
    # while page_num <= max_pages:
        variables = {
            "sectionId": "static-landing-Genre-section-Layout-11-0-update-false-84",
            "param": {
                "categoryUid": 11,
                "subcategoryUid": "0",
                "sortType": "update",
                "isComplete": False,
                "screenUid": 84,
                "page": page_num
            }
        }
        
        payload = {
            "query": query,
            "variables": variables
        }
        
        try:
            response = session.post(
                'https://bff-page.kakao.com/graphql',
                json=payload,
                headers=headers,
                timeout=30
            )
            
            # 상태 코드 확인
            if response.status_code == 429:
                print(f"⚠️  Rate limit 감지. 30초 대기 후 재시도...")
                time.sleep(30)
                continue
            elif response.status_code == 403:
                print(f"❌ 접근 거부 (403). IP 차단 가능성.")
                break
            elif response.status_code != 200:
                print(f"❌ HTTP {response.status_code} 오류")
                failed_requests += 1
                continue
            
            if response.status_code == 200:
                data = response.json()
                
                # 디버깅: 응답 구조 확인
                print(f"응답 키들: {list(data.keys()) if isinstance(data, dict) else 'Not dict'}")
                if 'data' in data:
                    print(f"data 키들: {list(data['data'].keys()) if data['data'] else 'data is None'}")
                
                # 전체 응답을 파일로 저장 (첫 번째 페이지만)
                if page_num == 1:
                    with open(f'debug_response_page_{page_num}.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print(f"디버깅용 응답이 debug_response_page_{page_num}.json 파일로 저장됨")
                
                if 'data' in data and data['data'] and 'staticLandingGenreSection' in data['data']:
                    section = data['data']['staticLandingGenreSection']
                    
                    # 총 개수 확인 및 최대 페이지 계산
                    total_count = section.get('totalCount', 0)
                    is_end = section.get('isEnd', False)
                    
                    # 첫 번째 페이지에서 최대 페이지 계산
                    if page_num == 1 and total_count and max_pages is None:
                        items_per_page = 24  # 관찰된 페이지당 아이템 수
                        import math
                        calculated_max_pages = math.ceil(total_count / items_per_page)
                        print(f"📊 총 소설 개수: {total_count:,}개")
                        print(f"📊 예상 총 페이지: {calculated_max_pages:,}페이지")
                        print(f"📊 예상 소요시간: {calculated_max_pages * 3.5 / 60:.1f}분")
                        
                        # 사용자 확인
                        if calculated_max_pages > confirmation_threshold:
                            user_input = input(f"\n⚠️  총 {calculated_max_pages}페이지를 수집하시겠습니까? (y/n/숫자): ")
                            if user_input.lower() == 'n':
                                print("수집을 중단합니다.")
                                break
                            elif user_input.isdigit():
                                max_pages = min(int(user_input), calculated_max_pages)
                                print(f"최대 {max_pages}페이지까지 수집합니다.")
                            else:
                                max_pages = calculated_max_pages
                        else:
                            max_pages = calculated_max_pages
                    
                    print(f"페이지 {page_num}/{max_pages or '?'}: 총 {total_count}개 중 수집 중...")
                    print(f"섹션 키들: {list(section.keys())}")
                    
                    # 아이템들 추출
                    if 'groups' in section:
                        print(f"그룹 개수: {len(section['groups'])}")
                        for group_idx, group in enumerate(section['groups']):
                            print(f"그룹 {group_idx} 키들: {list(group.keys())}")
                            if 'items' in group:
                                print(f"그룹 {group_idx} 아이템 개수: {len(group['items'])}")
                                
                                # 아이템 타입들 확인
                                item_types = [item.get('type') for item in group['items']]
                                print(f"아이템 타입들: {set(item_types)}")
                                
                                # 첫 번째 페이지에서 샘플 아이템 구조 확인
                                if page_num == 1 and group['items']:
                                    print(f"첫 번째 아이템 키들: {list(group['items'][0].keys())}")
                                    print(f"첫 번째 아이템 샘플: {group['items'][0]}")
                                
                                for item in group['items']:
                                    item_type = item.get('type')
                                    print(f"처리 중인 아이템 타입: {item_type}")
                                    
                                    # 모든 타입의 아이템을 일단 수집해보자
                                    if item_type and 'title' in item:  # 제목이 있는 모든 아이템
                                        novel_info = {
                                            'id': item.get('id'),
                                            'title': item.get('title'),
                                            'thumbnail': item.get('thumbnail'),
                                            'scheme': item.get('scheme'),
                                            'subtitleList': item.get('subtitleList', []),
                                            'badgeList': item.get('badgeList', []),
                                            'ageGrade': item.get('ageGrade'),
                                            'rank': item.get('rank'),
                                            'type': item.get('type')
                                        }
                                        all_novels.append(novel_info)
                                        print(f"아이템 추가됨: {item.get('title', 'No title')}")
                                    else:
                                        print(f"아이템 스킵됨 - 타입: {item_type}, 키들: {list(item.keys())}")
                    else:
                        print("groups 키가 없음")
                    
                    print(f"페이지 {page_num} 완료. 현재까지 {len(all_novels)}개 수집됨")
                    
                    # 마지막 페이지인지 확인
                    if is_end:
                        print(f"마지막 페이지 도달 (페이지 {page_num})")
                        break
                    
                    page_num += 1
                    
                    # 안전한 요청 간격 (랜덤하게 2-5초)
                    import random
                    wait_time = random.uniform(1,3)
                    print(f"다음 요청까지 {wait_time:.1f}초 대기 중...")
                    time.sleep(wait_time)
                    
                else:
                    print(f"페이지 {page_num}: 데이터 구조가 예상과 다름")
                    if 'errors' in data:
                        print(f"GraphQL 오류: {data['errors']}")
                    break
                    
            else:
                print(f"요청 실패: {response.status_code}")
                print(f"응답: {response.text[:500]}")
                break
                
        except Exception as e:
            print(f"오류 발생 (페이지 {page_num}): {e}")
            break
    
    return all_novels

def crawl_novels_with_playwright():
    """playwright 브라우저 컨텍스트에서 직접 호출"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        page.goto('https://page.kakao.com/menu/10011/screen/84')
        page.wait_for_load_state('networkidle')
        
        print("브라우저 컨텍스트에서 GraphQL 호출 시작...")
        
        all_novels = page.evaluate("""
            async () => {
                const results = [];
                let page_num = 1;
                const max_pages = 50;
                
                const query = `
                    query staticLandingGenreSection($sectionId: ID!, $param: StaticLandingGenreParamInput!) {
                      staticLandingGenreSection(sectionId: $sectionId, param: $param) {
                        isEnd
                        totalCount
                        groups {
                          id
                          type
                          dataKey
                          items {
                            id
                            type
                            ... on PosterViewItem {
                              title
                              thumbnail
                              scheme
                              subtitleList
                              badgeList
                              rank
                            }
                            ... on CardViewItem {
                              title
                              thumbnail
                              scheme
                              subtitleList
                              badgeList
                              rank
                            }
                          }
                        }
                      }
                    }
                `;
                
                while (page_num <= max_pages) {
                    try {
                        const variables = {
                            "sectionId": "static-landing-Genre-section-Layout-11-0-update-false-84",
                            "param": {
                                "categoryUid": 11,
                                "subcategoryUid": "0",
                                "sortType": "update",
                                "isComplete": false,
                                "screenUid": 84,
                                "page": page_num
                            }
                        };
                        
                        const response = await fetch('https://bff-page.kakao.com/graphql', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'Accept': 'application/json'
                            },
                            body: JSON.stringify({
                                query: query,
                                variables: variables
                            })
                        });
                        
                        const data = await response.json();
                        
                        if (data.data && data.data.staticLandingGenreSection) {
                            const section = data.data.staticLandingGenreSection;
                            
                            console.log(`페이지 ${page_num}: 총 ${section.totalCount}개`);
                            
                            if (section.groups) {
                                for (const group of section.groups) {
                                    if (group.items) {
                                        for (const item of group.items) {
                                            if (item.type === 'PosterViewItem' || item.type === 'CardViewItem') {
                                                results.push({
                                                    id: item.id,
                                                    title: item.title,
                                                    thumbnail: item.thumbnail,
                                                    scheme: item.scheme,
                                                    subtitleList: item.subtitleList || [],
                                                    badgeList: item.badgeList || [],
                                                    rank: item.rank,
                                                    type: item.type
                                                });
                                            }
                                        }
                                    }
                                }
                            }
                            
                            console.log(`페이지 ${page_num} 완료. 현재까지 ${results.length}개 수집`);
                            
                            if (section.isEnd) {
                                console.log(`마지막 페이지 도달`);
                                break;
                            }
                            
                            page_num++;
                            
                            // 잠깐 대기
                            await new Promise(resolve => setTimeout(resolve, 500));
                        } else {
                            console.log(`페이지 ${page_num}: 데이터 없음`);
                            break;
                        }
                        
                    } catch (error) {
                        console.error(`페이지 ${page_num} 오류:`, error);
                        break;
                    }
                }
                
                return results;
            }
        """)
        
        browser.close()
        return all_novels

def save_novels_to_file(novels, filename='kakao_novels.json'):
    """소설 데이터를 파일로 저장"""
    with open('data/'+filename, 'w', encoding='utf-8') as f:
        json.dump(novels, f, ensure_ascii=False, indent=2)
    print(f"결과가 '{filename}' 파일로 저장되었습니다.")

# 데이터 나누기
def split_data(data, split_num):
    """리스트와 딕셔너리 모두 처리하는 범용 분할 함수"""
    
    if isinstance(data, list):
        # 리스트인 경우 (기존 로직)
        new_data = []
        for i in range(0, len(data), split_num):
            new_data.append(data[i: i+split_num])
        return new_data
    
    elif isinstance(data, dict):
        # 딕셔너리인 경우
        items = list(data.items())  # (key, value) 튜플들의 리스트
        new_data = []
        
        for i in range(0, len(items), split_num):
            batch_items = items[i: i+split_num]
            batch_dict = dict(batch_items)  # 다시 딕셔너리로 변환
            new_data.append(batch_dict)
        
        return new_data
    
    else:
        raise TypeError(f"지원하지 않는 타입입니다: {type(data)}")

# 소설 데이터 가져오기
async def crawl_data(playwright, url, user_agent, age='All'):
    if age == '19':
        # 19금 인 경우에 로그인하기
        pass
    try:
        # print(url)
        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--no-first-run',
                '--disable-extensions',
                '--disable-default-apps',
                '--disable-gpu'
            ]
        )
        context = await browser.new_context(
            user_agent=user_agent,
            is_mobile=False,
            has_touch=False,
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        await page.goto(url)
        await page.wait_for_load_state('networkidle')
        # time.sleep(100)
        
        # print("브라우저 컨텍스트에서 GraphQL 호출 시작...")
        
        img_xpaths = [
            'xpath=//*[@id="__next"]/div/div[2]/div[1]/div/div[1]/div[1]/div/div[1]/div[2]/div/div/div/img',
            # 'xpath=//*[@id="__next"]/div/div[2]/div[1]/div/div[1]/div[1]/div/div[1]/div[2]/div/div/div[2]/img',
        ]
        # for xpath in img_xpaths:
        # 개선된 방법
        img_locator = page.locator('xpath=//*[@id="__next"]/div/div[2]/div[1]/div/div[1]/div[1]/div/div[1]/div[2]/div/div/div/img')
        if await img_locator.count() > 1:
            img = await img_locator.last.get_attribute('src')
        else:
            img = await img_locator.first.get_attribute('src')  # 또는 그냥 img_locator.get_attribute('src')
        
        title = await page.locator('xpath=//*[@id="__next"]/div/div[2]/div[1]/div/div[1]/div[1]/div/div[2]/a/div/span[1]').inner_text()
        author = await page.locator('xpath=//*[@id="__next"]/div/div[2]/div[1]/div/div[1]/div[1]/div/div[2]/a/div/span[2]').inner_text()
        if await page.locator('xpath=//*[@id="__next"]/div/div[2]/div[1]/div/div[1]/div[1]/div/div[2]/a/div/div[1]/div[3]/span').count() > 0:
            rating = await page.locator('xpath=//*[@id="__next"]/div/div[2]/div[1]/div/div[1]/div[1]/div/div[2]/a/div/div[1]/div[3]/span').inner_text()
        else:
            rating = None
        genre = await page.locator('xpath=//*[@id="__next"]/div/div[2]/div[1]/div/div[1]/div[1]/div/div[2]/a/div/div[1]/div[1]/div').inner_text()
        serial = await page.locator('xpath=//*[@id="__next"]/div/div[2]/div[1]/div/div[1]/div[1]/div/div[2]/a/div/div[2]/span').inner_text()
        publisher = await page.locator('xpath=//*[@id="__next"]/div/div[2]/div[1]/div/div[1]/div[1]/div/div[2]/a/div/span[2]').inner_text()

        page_count = await page.locator('xpath=//*[@id="__next"]/div/div[2]/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[1]/span').inner_text()

        if '단행본' in title:
            page_unit = '권'
        else:
            page_unit = '화'
        
        if '19세 완전판' in title:
            age = '19'
        else:
            age = '전체'
        # age = page.locator('xpath=//*[@id="__next"]/div/div[2]/div[1]/div/div[1]/div[1]/div/div[2]/a/div/span[2]').inner_text()

        viewers = await page.locator('xpath=//*[@id="__next"]/div/div[2]/div[1]/div/div[1]/div[1]/div/div[2]/a/div/div[1]/div[2]/span').inner_text()

        # 정보 보기
        await page.locator('xpath=//*[@id="__next"]/div/div[2]/div[1]/div/div[2]/div[1]/div/div/div[2]/a').click()
        await page.wait_for_selector('xpath=//*[@id="__next"]/div/div[2]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[2]/div/div[1]/span')
        await asyncio.sleep(.5)
        summary = await page.locator('xpath=//*[@id="__next"]/div/div[2]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[2]/div/div[1]/span').inner_text()
        
        if await page.locator('xpath=//*[@id="__next"]/div/div[2]/div[1]/div/div[2]/div[2]/div/div/div[2]/div[2]/div').count() == 1:
            keywords = page.locator('xpath=//*[@id="__next"]/div/div[2]/div[1]/div/div[2]/div[2]/div/div/div[2]/div[2]/div').inner_text()
        elif await page.locator('xpath=//*[@id="__next"]/div/div[2]/div[1]/div/div[2]/div[2]/div/div/div[2]/div[2]/div').count() > 1:
            keywords = page.locator('xpath=//*[@id="__next"]/div/div[2]/div[1]/div/div[2]/div[2]/div/div/div[2]/div[2]/div').last.inner_text()
        else:
             keywords = ''

        
        novel_data = {
            'url': url,
            'img': img,
            'title': title,
            'author': author,
            'rating': rating,
            'genre': genre,
            'serial': serial,
            'publisher': publisher,
            'summary': summary,
            'page_count': page_count,
            'page_unit': page_unit,
            'age': age,
            'platform': 'kakao',
            'keywords': keywords,
            'viewers': viewers
        }
        await asyncio.sleep(random.uniform(1, 2))
        # time.sleep(100)
        return novel_data
        
    except Exception as e:
        print(f"[ERROR] {url}")
        print(e)
    finally:
        if browser:
            try:
                await browser.close()
            except:
                pass

async def save_data(data):
    df = pd.DataFrame(data)
    df.to_csv('data/kakao_novel_data.csv', encoding='utf-8', index=False)
    print('데이터 저장')

async def main():
    if os.path.exists('data/kakao_novels.json'):
        with open('data/kakao_novels.json', 'r') as f:
            datas = json.load(f)
    else:
        print("=== 카카오페이지 소설 크롤링 (스크롤 없이) ===")
        print()
        
        method = input("크롤링 방법을 선택하세요 (1: requests, 2: playwright): ")
        
        if method == "1":
            novels = crawl_novels_with_requests()
        else:
            novels = crawl_novels_with_playwright()
        
        print(f"\n=== 수집 완료 ===")
        print(f"총 {len(novels)}개의 소설 정보를 수집했습니다.")
        
        if novels:
            # 결과 샘플 출력
            print("\n=== 수집된 데이터 샘플 ===")
            for i, novel in enumerate(novels[:5]):
                print(f"{i+1}. {novel.get('title', 'N/A')}")
                if novel.get('subtitleList'):
                    print(f"   작가: {', '.join(novel['subtitleList'])}")
                print(f"   ID: {novel.get('id', 'N/A')}")
                print()
            
            # 파일로 저장
            save_novels_to_file(novels)
            
            # 통계 출력
            print("=== 통계 ===")
            print(f"PosterViewItem: {len([n for n in novels if n.get('type') == 'PosterViewItem'])}개")
            print(f"CardViewItem: {len([n for n in novels if n.get('type') == 'CardViewItem'])}개")
            
            # 랭킹이 있는 작품들
            ranked_novels = [n for n in novels if n.get('rank')]
            if ranked_novels:
                print(f"랭킹 정보가 있는 작품: {len(ranked_novels)}개")
        datas = novels.copy()


    ua = UserAgent(platforms='desktop')
    not_nineteen_links = []
    nineteen_links = []
    for data in datas:
        # 19금 분리
        if data['ageGrade'] != 'Nineteen':
            link = data['scheme'].replace('kakaopage://open/', 'https://page.kakao.com/')
            link = link.replace('?series_id=', '/')
            link += '?tab_type=overview'
            not_nineteen_links.append(link)
        else:
            nineteen_links.append(link)

    # 전체 이용가 크롤링
    not_nineteen_links = split_data(not_nineteen_links, 5)
    all_results = []
    async with async_playwright() as playwright:
        # 링크 수집 진행상황 표시
        for url_list in tqdm(not_nineteen_links, desc="📄 페이지별 링크 수집", unit="배치"):
            tasks = [crawl_data(playwright, url, ua.random, age='all') for url in url_list]
            
            # tqdm_asyncio로 각 배치 내 태스크 진행상황 표시
            batch_results = await tqdm_asyncio.gather(
                *tasks, 
                desc=f"URL 처리 ({len(url_list)}개)", 
                unit="페이지",
                # return_exceptions=True
            )
            all_results.append(batch_results)

    # 19금 작품 크롤링
    nineteen_links = split_data(nineteen_links, 5)
    async with async_playwright() as playwright:
        # 링크 수집 진행상황 표시
        for url_list in tqdm(nineteen_links, desc="📄 페이지별 링크 수집", unit="배치"):
            tasks = [crawl_data(playwright, url, ua.random, age='19') for url in url_list]
            
            # tqdm_asyncio로 각 배치 내 태스크 진행상황 표시
            batch_results = await tqdm_asyncio.gather(
                *tasks, 
                desc=f"URL 처리 ({len(url_list)}개)", 
                unit="페이지",
                # return_exceptions=True
            )
            all_results.append(batch_results)

    all_results = list(chain.from_iterable(all_results))

    await save_data(all_results)




if __name__ == "__main__":
    asyncio.run(main())