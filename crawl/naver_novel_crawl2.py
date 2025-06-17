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

# 세션 설정 (재사용 및 재시도 설정)
def create_session():
    session = requests.Session()
    
    # 재시도 설정
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
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

def login_and_get_cookies():
    """Selenium을 사용해 로그인 및 성인 인증 후 쿠키 반환"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        try:
            # 네이버 로그인 페이지로 이동
            driver.get('https://nid.naver.com/nidlogin.login')
            
            print("=" * 60)
            print("🔐 네이버 로그인이 필요합니다.")
            print("=" * 60)
            print("브라우저에서 네이버 로그인을 완료한 후 Enter를 눌러주세요...")
            input()
            
            # 성인 인증 테스트를 위해 19금 소설 페이지로 이동
            test_url = 'https://series.naver.com/novel/detail.series?productNo=12340968'
            print(f"19금 콘텐츠 접근 테스트: {test_url}")
            driver.get(test_url)
            time.sleep(5)  # 페이지 로딩 대기 시간 증가
            
            # 성인 인증 상태 확인
            page_source = driver.page_source
            print("페이지 로딩 완료, 접근 상태 확인 중...")
            
            # 다양한 키워드로 접근 제한 확인
            restriction_keywords = [
                '성인인증', '19세 이상', '본인인증', '성인 콘텐츠',
                'adult_certification', '성인 작품', '연령 제한'
            ]
            
            is_restricted = any(keyword in page_source for keyword in restriction_keywords)
            
            if is_restricted:
                print("❌ 성인 콘텐츠 접근이 제한되어 있습니다.")
                print("다음 중 하나의 문제일 수 있습니다:")
                print("1. 성인 인증이 완료되지 않음")
                print("2. 계정 설정에서 성인 콘텐츠 보기가 비활성화됨")
                print("3. 브라우저에서 직접 19금 콘텐츠에 접근하여 인증을 완료해주세요")
                print("\n브라우저에서 성인 인증을 완료한 후 Enter를 누르세요...")
                input()
                
                # 다시 확인
                driver.refresh()
                time.sleep(3)
                page_source = driver.page_source
                
                if any(keyword in page_source for keyword in restriction_keywords):
                    print("⚠️ 여전히 접근이 제한됩니다. 그래도 쿠키를 저장하여 시도해보겠습니다.")
                else:
                    print("✅ 성인 콘텐츠 접근 성공!")
            else:
                print("✅ 성인 콘텐츠 접근 성공!")
            
            # 모든 도메인에서 쿠키 수집
            all_cookies = {}
            
            # 현재 페이지 쿠키
            for cookie in driver.get_cookies():
                all_cookies[cookie['name']] = cookie['value']
            
            # 네이버 메인으로 이동하여 추가 쿠키 수집
            driver.get('https://www.naver.com')
            time.sleep(2)
            for cookie in driver.get_cookies():
                all_cookies[cookie['name']] = cookie['value']
            
            # 네이버 시리즈 메인으로 이동하여 추가 쿠키 수집
            driver.get('https://series.naver.com')
            time.sleep(2)
            for cookie in driver.get_cookies():
                all_cookies[cookie['name']] = cookie['value']
            
            print(f"추출된 쿠키 수: {len(all_cookies)}개")
            
            # 중요 쿠키들이 있는지 확인
            important_cookies = ['NID_AUT', 'NID_SES', 'NACT', 'nx_ssl']
            found_important = [name for name in important_cookies if name in all_cookies]
            print(f"중요 쿠키 발견: {found_important}")
            
            return all_cookies
            
        finally:
            driver.quit()
            
    except ImportError:
        raise ImportError("Selenium이 설치되지 않았습니다. pip install selenium")
    except Exception as e:
        raise Exception(f"로그인 실패: {e}")

def get_data_with_selenium(url_age_tuple):
    """Selenium을 사용한 19금 데이터 추출 (각 프로세스에서 개별 브라우저 실행)"""
    url, age = url_age_tuple
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        # 헤드리스 Chrome 설정
        options = Options()
        options.add_argument('--headless')  # 백그라운드 실행
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-logging')
        options.add_argument('--disable-web-security')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("detach", False)
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        try:
            # 쿠키 파일에서 로그인 정보 로드
            cookies_path = 'data/naver_cookies.pickle'
            if os.path.exists(cookies_path):
                cookies = open_files(cookies_path)
                
                # 네이버 메인으로 이동 후 쿠키 설정
                driver.get('https://www.naver.com')
                
                # 쿠키 설정
                for name, value in cookies.items():
                    try:
                        driver.add_cookie({'name': name, 'value': value, 'domain': '.naver.com'})
                    except:
                        continue
                
                # 페이지 새로고침으로 쿠키 적용
                driver.refresh()
                time.sleep(1)
            else:
                print(f"쿠키 파일이 없습니다: {url}")
                return None
            
            # 19금 페이지로 이동
            driver.get(url)
            time.sleep(2)
            
            # 페이지 소스 가져오기
            page_source = driver.page_source
            
            # 접근 제한 확인
            if any(keyword in page_source.lower() for keyword in 
                   ['성인인증', '19세 이상', '본인인증', '로그인이 필요']):
                print(f"19금 접근 제한: {url}")
                return None
            
            # lxml로 파싱
            tree = html.fromstring(page_source)
            
            # 더보기 버튼 클릭 (요약 전체 보기)
            try:
                more_button = driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/span/a')
                driver.execute_script("arguments[0].click();", more_button)
                time.sleep(1)
                # 새로운 페이지 소스로 다시 파싱
                tree = html.fromstring(driver.page_source)
            except:
                pass  # 더보기 버튼이 없으면 무시
            
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
                'age': 19,
                'platform': 'naver'
            }
            
            # 필수 데이터 체크
            if not all([title, rating, genre, serial, publisher, summary, page_count, page_unit]):
                print(f"데이터 누락: {url} - {title}")
                return None
            
            print(f"✅ 19금 추출 성공: {title}")
            time.sleep(random.uniform(1, 2))
            return novel_data
            
        finally:
            driver.quit()
            
    except ImportError:
        print("Selenium이 설치되지 않았습니다.")
        return None
    except Exception as e:
        print(f"Selenium 데이터 추출 에러 {url}: {e}")
        return None
        
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
            print(f"데이터 누락: {url}")
            # print(novel_data)
            raise Exception('데이터 누락 발생')
        
        # 딜레이 추가 (서버 부하 방지)
        time.sleep(random.uniform(0.5, 1.5))
        return novel_data
        
    except Exception as e:
        print(f"데이터 추출 에러 {url}: {e}")
        return None
    finally:
        session.close()

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
    """세션을 사용한 단일 소설 데이터 추출 (전체 이용가용)"""
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
            # print(f"데이터 누락: {url}")
            # print(novel_data)
            raise Exception('데이터 누락 발생')
        
        # 딜레이 추가 (서버 부하 방지)
        time.sleep(random.uniform(0.5, 1.5))
        return novel_data
        
    except Exception as e:
        # print(f"데이터 추출 에러 {url}: {e}")
        return None
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
    cookies_path = 'data/naver_cookies.pickle'
    
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
            # if not_nineteen_links:
            #     print("전체 이용가 소설 크롤링 시작...")
            #     not_nineteen_tuples = [(url, 0) for url in not_nineteen_links]
                
            #     # 배치 단위로 나누어서 처리
            #     batches = split_data(not_nineteen_tuples, 20)  # 20개씩 배치 처리
                
            #     for batch in tqdm(batches, desc="전체 이용가 배치 처리"):
            #         batch_results = parmap.map(
            #             get_data,
            #             batch,
            #             pm_pbar=False,  # 배치별로는 진행률 표시 안함
            #             pm_processes=5
            #         )
                    
            #         # None 값 제거하고 결과 추가
            #         valid_batch_results = [result for result in batch_results if result is not None]
            #         all_results.extend(valid_batch_results)
                    
            #         # 배치 간 딜레이
            #         time.sleep(random.uniform(1, 4))
                
            #     print(f"전체 이용가 크롤링 완료: {len([r for r in all_results if r and r.get('age') == '전체'])}개")
            
            # 2. 19금 소설 크롤링 (Selenium 기반 병렬 처리)
            if nineteen_links:
                print("19금 소설 크롤링 시작...")
                print("각 프로세스에서 개별 Selenium 브라우저를 사용합니다.")
                
                # 먼저 로그인하여 쿠키 저장
                if not os.path.exists(cookies_path):
                    print("네이버 로그인이 필요합니다.")
                    try:
                        cookies = login_and_get_cookies()
                        save_files(cookies_path, cookies)
                        print("로그인 쿠키 저장 완료")
                    except Exception as login_error:
                        print(f"로그인 실패: {login_error}")
                        print("19금 크롤링을 건너뜁니다.")
                        break
                else:
                    print("기존 쿠키 파일 사용")
                
                # 19금 링크 튜플 생성 (쿠키 정보 없이)
                nineteen_tuples = [(url, 19) for url in nineteen_links]
                
                # 배치 단위로 나누어서 처리
                batches = split_data(nineteen_tuples, 3)  # 3개씩 처리 (Selenium은 리소스 많이 사용)
                
                for i, batch in enumerate(tqdm(batches, desc="19금 배치 처리")):
                    print(f"\n19금 배치 {i+1}/{len(batches)} 처리 중...")
                    batch_results = parmap.map(
                        get_data_with_selenium,  # Selenium 함수 사용
                        batch,
                        pm_pbar=False,
                        pm_processes=2  # Selenium은 2개 프로세스로 제한
                    )
                    
                    # 결과 확인 및 통계
                    valid_batch_results = [result for result in batch_results if result is not None]
                    failed_count = len(batch) - len(valid_batch_results)
                    
                    print(f"배치 결과: 성공 {len(valid_batch_results)}개, 실패 {failed_count}개")
                    
                    all_results.extend(valid_batch_results)
                    
                    # 배치 간 긴 딜레이 (리소스 정리 시간 확보)
                    if i < len(batches) - 1:  # 마지막 배치가 아니면
                        delay = random.uniform(5, 8)
                        print(f"다음 배치까지 {delay:.1f}초 대기 (브라우저 정리 시간)...")
                        time.sleep(delay)
                
                print(f"19금 크롤링 완료: {len([r for r in all_results if r and r.get('age') == 19])}개")
            
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