import requests
from lxml import html
import pandas as pd
import random
from itertools import chain
import os
from fake_useragent import UserAgent
from tqdm import tqdm
import pickle
import time
import parmap
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import asyncio
from playwright.async_api import async_playwright

# 세션 설정 (재사용 및 재시도 설정)
def create_session():
    session = requests.Session()
    
    # 재시도 설정
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],  # method_whitelist -> allowed_methods
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

# 헤더 생성
def get_headers():
    ua = UserAgent(platforms='desktop')
    return {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

# Playwright 관련 함수들
async def create_page(playwright, user_agent, headless=True):
    """Playwright 페이지 생성"""
    browser = None
    try:
        browser = await playwright.chromium.launch(
            headless=headless,
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
        return page, browser
    except Exception as e:
        print(f'Playwright 페이지 생성 에러: {e}')
        return None, None

async def login_playwright(page):
    """Playwright로 로그인 처리"""
    await page.goto('https://series.naver.com/novel/categoryProductList.series?categoryTypeCode=all')
    
    # 로그인 버튼이 있는지 확인
    login_button = page.locator('xpath=//*[@id="gnb_login_button"]')
    if await login_button.count() > 0:
        await login_button.click()
        print("브라우저에서 로그인을 완료한 후 Enter를 눌러주세요...")
        input()  # 사용자가 수동으로 로그인 완료할 때까지 대기

async def extract_xpath_playwright(page, xpaths, attr_type='text'):
    """Playwright에서 XPath 추출"""
    for xpath in xpaths:
        try:
            element = page.locator(f'xpath={xpath}')
            if await element.count() > 0:
                if attr_type == 'text':
                    data = await element.first.inner_text()
                elif attr_type == 'src':
                    data = await element.first.get_attribute('src')
                elif attr_type == 'href':
                    data = await element.first.get_attribute('href')
                
                if data and data.strip():
                    if '_님로그아웃' in data:
                        continue
                    return data.strip()
        except Exception as e:
            continue
    return ''

async def get_data_playwright(page, url, age=19):
    """Playwright로 19금 소설 데이터 추출"""
    try:
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            response = await page.goto(url, timeout=30000)
            
            if response.status != 200:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"HTTP {response.status} 오류. 재시도 {retry_count}/{max_retries}")
                    await asyncio.sleep(random.uniform(1, 3))
                    continue
                else:
                    raise Exception(f'HTTP {response.status} 오류가 {max_retries}번 반복됨')
            break

        # 페이지 로딩 대기
        await asyncio.sleep(1)

        # 데이터 추출 (Playwright 방식)
        img_xpaths = [
            '/html/body/div[1]/div[2]/div[1]/span/img',
            '//*[@id="container"]/div[1]/a/img',
            '//*[@id="container"]/div[1]/span/img',
            '//*[@id="ct"]/div[1]/div[1]/div[1]/div[1]/a/img'
        ]
        img = await extract_xpath_playwright(page, img_xpaths, 'src')

        title_xpaths = [
            '//*[@id="content"]/div[1]/h2',
            '//*[@id="ct"]/div[1]/div[1]/div[1]/div[2]/strong',
            '//*[@id="content"]/div[2]',
            '//*[@id="content"]/div[2]/h2'
        ]
        title = await extract_xpath_playwright(page, title_xpaths)

        rating_xpaths = [
            '//*[@id="content"]/div[1]/div[1]/em',
            '//*[@id="content"]/div[2]/div[1]',
            '//*[@id="ct"]/div[1]/div[1]/div[1]/div[2]/div[1]/ul/li/span/span'
        ]
        rating = await extract_xpath_playwright(page, rating_xpaths)

        genre_xpaths = [
            '//*[@id="content"]/ul[1]/li/ul/li[2]/span/a',
            '//*[@id="ct"]/div[1]/div[1]/div[1]/div[2]/div[2]/ul/li[1]/dl/dd[2]'
        ]
        genre = await extract_xpath_playwright(page, genre_xpaths)

        serial_xpaths = [
            '//*[@id="content"]/ul[1]/li/ul/li[1]/span',
            '//*[@id="ct"]/div[1]/div[1]/div[1]/div[2]/div[2]/ul/li[1]/dl/dd[1]'
        ]
        serial = await extract_xpath_playwright(page, serial_xpaths)

        publisher_xpaths = ['//*[@id="content"]/ul[1]/li/ul/li[3]']
        author_xpaths = [
            '//*[@id="content"]/ul[1]/li/ul/li[4]/a',
            '//*[@id="content"]/ul[1]/li/ul/li[3]/a'
        ]
        publisher = await extract_xpath_playwright(page, publisher_xpaths)
        author = await extract_xpath_playwright(page, author_xpaths)

        # 설명 - "더보기" 버튼 클릭 처리
        more_button = page.locator('xpath=//*[@id="content"]/div[2]/div[1]/span/a')
        if await more_button.count() > 0:
            await more_button.click()
            await asyncio.sleep(0.5)

        summary_xpaths = [
            '//*[@id="content"]/div[2]/div[2]',
            '//*[@id="content"]/div[2]/div'
        ]
        summary = await extract_xpath_playwright(page, summary_xpaths)

        page_count_xpaths = ['//*[@id="content"]/h5/strong']
        page_count = await extract_xpath_playwright(page, page_count_xpaths)

        page_unit_xpaths = ['//*[contains(@class, "end_total_episode")]']
        page_unit = await extract_xpath_playwright(page, page_unit_xpaths)
        
        try:
            if page_unit:
                page_unit = page_unit.strip()[-1]
        except:
            print(f"페이지 단위 추출 실패: {page_unit}")

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
            'age': 19 if age == 19 else '전체',
            'platform': 'naver'
        }

        # 필수 데이터 체크
        if not all([title, rating, genre, serial, publisher, summary, page_count, page_unit]):
            print(f"데이터 누락: {url}")
            print(novel_data)
            raise Exception('데이터 누락 발생')

        await asyncio.sleep(random.uniform(1, 2))
        return novel_data

    except Exception as e:
        print(f"Playwright 데이터 추출 에러 {url}: {e}")
        return None

async def get_19(nineteen_links):
    """19금 소설 크롤링 (Playwright 사용)"""
    ua = UserAgent(platforms='desktop')
    all_results = []

    async with async_playwright() as playwright:
        page, browser = await create_page(playwright, ua.random, headless=False)
        if not page:
            print("Playwright 페이지 생성 실패")
            return []
            
        await login_playwright(page)
        await asyncio.sleep(1)
        
        with tqdm(nineteen_links, desc=f"현재 수집된 링크 수: {len(all_results)}", total=len(nineteen_links)) as pbar:
            for url in pbar:
                novel_data = await get_data_playwright(page, url, age=19)
                if novel_data:
                    all_results.append(novel_data)

                # tqdm 설명 동적 업데이트
                pbar.set_description(f"현재 수집된 링크 수: {len(all_results)}")
                await asyncio.sleep(random.uniform(1, 2))
                
        if browser:
            await browser.close()
    
    return all_results

def get_login_cookies_selenium():
    """Selenium을 사용해 로그인 후 쿠키 반환"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        
        try:
            # 로그인 페이지 이동
            driver.get('https://nid.naver.com/nidlogin.login')
            
            # 수동 로그인 대기
            print("브라우저에서 로그인을 완료한 후 Enter를 눌러주세요...")
            input()
            
            # 로그인 확인
            if 'series.naver.com' not in driver.current_url:
                driver.get('https://series.naver.com')
            
            # 쿠키 추출
            cookies = {}
            for cookie in driver.get_cookies():
                cookies[cookie['name']] = cookie['value']
            
            print(f"추출된 쿠키 수: {len(cookies)}개")
            return cookies
            
        finally:
            driver.quit()
            
    except ImportError:
        raise ImportError("Selenium이 설치되지 않았습니다. pip install selenium")
    except Exception as e:
        raise Exception(f"Selenium 로그인 실패: {e}")

# 데이터 나누기
def split_data(data, split_num):
    """리스트와 딕셔너리 모두 처리하는 범용 분할 함수"""
    if isinstance(data, list):
        new_data = []
        for i in range(0, len(data), split_num):
            new_data.append(data[i: i+split_num])
        return new_data
    elif isinstance(data, dict):
        items = list(data.items())
        new_data = []
        for i in range(0, len(items), split_num):
            batch_items = items[i: i+split_num]
            batch_dict = dict(batch_items)
            new_data.append(batch_dict)
        return new_data
    else:
        raise TypeError(f"지원하지 않는 타입입니다: {type(data)}")

# 링크 가져오기
def get_links(url):
    session = create_session()
    headers = get_headers()
    
    try:
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        tree = html.fromstring(response.content)
        links = []
        
        # h3 태그들 찾기
        h3_elements = tree.xpath('//*[@id="content"]/div/ul/li/div/h3')
        
        for h3_element in h3_elements:
            # 제목 가져오기
            page_title = h3_element.text_content().strip()
            
            # a 태그 찾기 (h3 내부에서)
            a_elements = h3_element.xpath('.//a[contains(@href, "/novel/detail")]')
            
            if a_elements:
                href = a_elements[0].get('href')
                link = 'https://series.naver.com' + href
                
                # 나이 제한 체크
                age = 19 if '19금' in page_title else 0
                
                links.append({
                    'url': link,
                    'age': age,
                })
        
        time.sleep(random.randint(1, 2))
        return links
        
    except Exception as e:
        print(f"링크 수집 에러 {url}: {e}")
        return []
    finally:
        session.close()

def get_last_page():
    session = create_session()
    headers = get_headers()
    
    try:
        url = 'https://series.naver.com/novel/categoryProductList.series?categoryTypeCode=all&page=100000'
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        tree = html.fromstring(response.content)
        page_elements = tree.xpath('//*[@id="content"]/p/a/text()')
        
        if page_elements:
            max_page_num = max(page_elements)
            return max_page_num
        return "1"
        
    except Exception as e:
        print(f"최대 페이지 수집 에러: {e}")
        return "1"
    finally:
        session.close()

# XPath 추출 함수
def extract_xpath(tree, xpaths, attr=None):
    for xpath in xpaths:
        try:
            elements = tree.xpath(xpath)
            if elements:
                if attr:
                    data = elements[0].get(attr)
                else:
                    data = elements[0].text_content()
                
                if data and data.strip():
                    if '_님로그아웃' in data:
                        continue
                    return data.strip()
        except Exception as e:
            continue
    return ''

# 이미지 추출
def get_img(tree):
    img_xpaths = [
        '/html/body/div[1]/div[2]/div[1]/span/img',
        '//*[@id="container"]/div[1]/a/img',
        '//*[@id="container"]/div[1]/span/img',
        '//*[@id="ct"]/div[1]/div[1]/div[1]/div[1]/a/img'
    ]
    return extract_xpath(tree, img_xpaths, attr='src')

# 제목 추출
def get_title(tree):
    title_xpaths = [
        '//*[@id="content"]/div[1]/h2',
        '//*[@id="ct"]/div[1]/div[1]/div[1]/div[2]/strong',
        '//*[@id="content"]/div[2]',
        '//*[@id="content"]/div[2]/h2'
    ]
    return extract_xpath(tree, title_xpaths)

# 평점 추출
def get_rating(tree):
    rating_xpaths = [
        '//*[@id="content"]/div[1]/div[1]/em',
        '//*[@id="content"]/div[2]/div[1]',
        '//*[@id="ct"]/div[1]/div[1]/div[1]/div[2]/div[1]/ul/li/span/span',
    ]
    return extract_xpath(tree, rating_xpaths)

# 장르 추출
def get_genre(tree):
    genre_xpaths = [
        '//*[@id="content"]/ul[1]/li/ul/li[2]/span/a',
        '//*[@id="ct"]/div[1]/div[1]/div[1]/div[2]/div[2]/ul/li[1]/dl/dd[2]'
    ]
    return extract_xpath(tree, genre_xpaths)

# 연재 상태 추출
def get_serial(tree):
    serial_xpaths = [
        '//*[@id="content"]/ul[1]/li/ul/li[1]/span',
        '//*[@id="ct"]/div[1]/div[1]/div[1]/div[2]/div[2]/ul/li[1]/dl/dd[1]'
    ]
    return extract_xpath(tree, serial_xpaths)

# 출판사 및 작가 추출
def get_publisher_author(tree):
    publisher_xpaths = [
        '//*[@id="content"]/ul[1]/li/ul/li[3]'
    ]
    author_xpaths = [
        '//*[@id="content"]/ul[1]/li/ul/li[4]/a',
        '//*[@id="content"]/ul[1]/li/ul/li[3]/a'
    ]
    publisher = extract_xpath(tree, publisher_xpaths)
    author = extract_xpath(tree, author_xpaths)
    return publisher, author

# 설명 추출
def get_summary(tree):
    summary_xpaths = [
        '//*[@id="content"]/div[2]/div[2]',
        '//*[@id="content"]/div[2]/div'
    ]
    return extract_xpath(tree, summary_xpaths)

# 화수 추출
def get_page_count(tree):
    page_count_xpaths = [
        '//*[@id="content"]/h5/strong'
    ]
    return extract_xpath(tree, page_count_xpaths)

# 단위 추출
def get_page_unit(tree):
    page_unit_xpaths = [
        '//*[contains(@class, "end_total_episode")]'
    ]
    page_unit = extract_xpath(tree, page_unit_xpaths)
    try:
        if page_unit:
            page_unit = page_unit.strip()[-1]
    except:
        print(f"페이지 단위 추출 실패: {page_unit}")
    return page_unit

# 연령 추출
def get_age(tree):
    age_xpaths = [
        '//*[@id="content"]/ul[1]/li/ul/li[5]'
    ]
    return extract_xpath(tree, age_xpaths)

def get_data_with_session(url_age_tuple, session=None):
    """세션을 사용한 단일 소설 데이터 추출 (19금용)"""
    url, age = url_age_tuple
    
    if session is None:
        session = create_session()
        should_close = True
    else:
        should_close = False
    
    headers = get_headers()
    
    max_retries = 3
    retry_count = 0
    
    try:
        while retry_count < max_retries:
            response = session.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"HTTP {response.status_code} 오류. 재시도 {retry_count}/{max_retries}")
                    time.sleep(random.uniform(1, 3))
                    continue
                else:
                    raise Exception(f'HTTP {response.status_code} 오류가 {max_retries}번 반복됨')
            break
        
        tree = html.fromstring(response.content)
        
        # 데이터 추출
        img = get_img(tree)
        title = get_title(tree)
        rating = get_rating(tree)
        genre = get_genre(tree)
        serial = get_serial(tree)
        publisher, author = get_publisher_author(tree)
        summary = get_summary(tree)
        page_count = get_page_count(tree)
        page_unit = get_page_unit(tree)
        
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
            'age': 19 if age == 19 else '전체',
            'platform': 'naver'
        }
        
        # 필수 데이터 체크
        if not all([title, rating, genre, serial, publisher, summary, page_count, page_unit]):
        #     print(f"데이터 누락: {url}")
            # print(novel_data)
            raise Exception('데이터 누락 발생')
        
        # 딜레이 추가 (서버 부하 방지)
        time.sleep(random.uniform(0.5, 1.5))
        return novel_data
        
    except Exception as e:
        # print(f"데이터 추출 에러 {url}: {e}")
        return {}
    finally:
        if should_close:
            session.close()

def get_data(url_age_tuple):
    """단일 소설 데이터 추출 (전체 이용가용)"""
    return get_data_with_session(url_age_tuple, session=None)

def flatten(lst):
    """중첩 리스트 평탄화"""
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(item)
        else:
            result.append(item)
    return result

# 데이터 불러오기
def open_files(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

# 데이터 저장하기
def save_files(path, data):
    with open(path, 'wb') as f:
        pickle.dump(data, f)

def main():
    print("🚀 네이버 소설 크롤링 시작!")
    
    # 데이터 디렉토리 생성
    os.makedirs('data', exist_ok=True)
    
    novel_data_path = 'data/naver_novel_data.data'
    novel_page_path = 'data/naver_page_links.link'
    
    # URL 수집
    if os.path.exists(novel_page_path):
        all_urls = open_files(novel_page_path)
        # print(f"기존 URL 데이터 로드: {len(all_urls)}개")
    else:
        print("URL 수집 시작...")
        all_urls = []
        
        # 최대 페이지 수 가져오기
        max_page_num = get_last_page()
        print(f"최대 페이지 수: {max_page_num}")
        
        # 모든 페이지 URL 생성
        page_urls = []
        for i in range(1, int(max_page_num.replace(',', '')) + 1):
            page_urls.append(f'https://series.naver.com/novel/categoryProductList.series?categoryTypeCode=all&page={i}')
        
        # parmap으로 병렬 처리하여 링크 수집
        print("페이지별 링크 수집 중...")
        all_links = parmap.map(get_links, page_urls, pm_pbar=True, pm_processes=4)
        
        # 결과 평탄화
        all_urls = flatten(all_links)
        
        # 저장
        save_files(novel_page_path, all_urls)
    
    # all_urls = all_urls[:50]
    print(f"총 수집된 URL: {len(all_urls)}개")

    while True:
        try:
            # 기존 데이터와 비교하여 새로운 URL만 필터링
            if os.path.exists(novel_data_path):
                old_data = open_files(novel_data_path)
                cache_urls = [data['url'] for data in old_data if data]
                filtered_urls = [url for url in all_urls if url['url'] not in cache_urls]
                print(f"새로 크롤링할 URL: {len(filtered_urls)}개")
            else:
                filtered_urls = all_urls
                old_data = []
            
            if not filtered_urls:
                print("크롤링할 새로운 URL이 없습니다.")
                break
            
            # 나이별로 분류
            not_nineteen_links = [link['url'] for link in filtered_urls if link['age'] == 0]
            nineteen_links = [link['url'] for link in filtered_urls if link['age'] == 19]
            
            all_results = []
            
            # not_nineteen_links = not_nineteen_links[:1000]
            print(f'전체 이용가: {len(not_nineteen_links)}개')
            print(f'19금: {len(nineteen_links)}개')
            
            # 1. 전체 이용가 소설 크롤링 (병렬 처리)
            if not_nineteen_links:
                print("전체 이용가 소설 크롤링 시작...")
                not_nineteen_tuples = [(url, 0) for url in not_nineteen_links]
                
                # 배치 단위로 나누어서 처리
                batches = split_data(not_nineteen_tuples, 20)  # 20개씩 배치 처리
                
                for batch in tqdm(batches, desc="전체 이용가 배치 처리"):
                    batch_results = parmap.map(
                        get_data,
                        batch,
                        pm_pbar=False,  # 배치별로는 진행률 표시 안함
                        pm_processes=5
                    )
                    
                    # None 값 제거하고 결과 추가
                    valid_batch_results = [result for result in batch_results if result is not None]
                    all_results.extend(valid_batch_results)
                    
                    # 배치 간 딜레이
                    time.sleep(random.uniform(1, 4))
                
                # print(f"전체 이용가 크롤링 완료: {len([r for r in all_results if r['url'] == '전체'])}개")
            
            # 2. 19금 소설 크롤링 (Playwright 사용)
            if nineteen_links:
                print("19금 소설 크롤링 시작...")
                print("Playwright를 사용하여 19금 콘텐츠를 크롤링합니다.")
                
                # 비동기 함수 호출
                nineteen_results = asyncio.run(get_19(nineteen_links))
                all_results.extend(nineteen_results)
                
                print(f"19금 크롤링 완료: {len(nineteen_results)}개")
            
            print(f"총 수집된 데이터: {len(all_results)}개")
            
            # 기존 데이터와 합치기
            all_data = old_data + all_results
            
            # 저장
            save_files(novel_data_path, all_data)
            print(f"총 {len(all_data)}개 데이터 저장 완료")
            break
            
        except Exception as e:
            print(f'데이터 추출 오류: {e}')
            print('현재까지의 데이터를 저장합니다.')
            
            # 부분 결과라도 저장
            if 'all_results' in locals() and all_results:
                if os.path.exists(novel_data_path):
                    existing_data = open_files(novel_data_path)
                    existing_data.extend(all_results)
                    save_files(novel_data_path, existing_data)
                else:
                    save_files(novel_data_path, all_results)
            break

if __name__ == "__main__":
    try:
        main()
        print("\n🎊 모든 작업이 완료되었습니다!")
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 실행 중 에러: {e}")
        import traceback
        traceback.print_exc()