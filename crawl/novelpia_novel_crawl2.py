
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
from lxml import html
from fake_useragent import UserAgent
import parmap
import pickle
import re
import time
import random
import os
import asyncio
from playwright.async_api import async_playwright
from tqdm import tqdm
from itertools import chain

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

# 페이지 링크들 수집
async def get_links(page, url):
    await page.goto(url)
    
    links = []
    elements = await page.locator('xpath=/html/body/div[8]/div[3]/div[6]/div/table/tbody/tr[1]/td[1]').all()
    
    for element in elements:
        onclick_value = await element.get_attribute('onclick')
        if onclick_value:
            # url 추출
            if "location='" in onclick_value:
                url_part = onclick_value.split("location='")[1].split("'")[0]
                full_url = f"https://novelpia.com{url_part}"
                links.append(full_url)
    
    return links

# 데이터 평탄화
def flatten_results(results):
    """중첩된 리스트를 평탄화"""
    flattened = []
    for result in results:
        if isinstance(result, list):
            flattened.extend(result)
        else:
            flattened.append(result)
    return flattened

# 데이터 불러오기
def open_files(file):
    with open(file, 'rb') as f:
        cache_data = pickle.load(f)
        
    return cache_data

# 데이터 저장하기
def save_files(file, data):
    with open(file, 'wb') as f:
        pickle.dump(data, f)

def extract_element(tree, xpaths, type='text'):
    for xpath in xpaths:
        if xpath.startswith('xpath='):
            xpath = xpath[6:]
        element = tree.xpath(xpath)
        if len(element) > 0:
            if type == 'text':
                return element[0].text_content().strip()
            elif type == 'img':
                return element[0].get('src').strip()

# 이미지 가져오기
def get_img(tree):
    img_xpaths = [
        'xpath=/html/body/div[6]/div[1]/div[1]/a/img',
        'xpath=/html/body/div[6]/div[1]/div[1]/img',
        '//*[@class="conver_img"]',
    ]
    img = extract_element(tree, img_xpaths, 'img')

    return img

# 제목 가져오기
def get_title(tree):
    title_xpaths = [
        '//*[@class="epnew-novel-title"]',
        'xpath=/html/body/div[6]/div[1]/div[2]/div[2]'
    ]
    title = extract_element(tree, title_xpaths)

    return title

# 작가 가져오기
def get_author(tree):
    author_xpaths = [
        'xpath=/html/body/div[6]/div[1]/div[2]/div[3]/p[1]/a',
        '//*[@class="writer-name"]'
    ]
    author = extract_element(tree, author_xpaths)

    return author

# 추천 수 가져오기
def get_recommend(tree):
    recommend_xpaths = [
        'xpath=/html/body/div[6]/div[1]/div[2]/div[4]/div[1]/p[2]/span[2]',
        'xpath=/html/body/div[6]/div[1]/div[2]/div[5]/div[1]/p[2]/span[2]'
    ]
    # 추천 수
    recommend = extract_element(tree, recommend_xpaths)

    return recommend

# 키워드, 태그, 장르 가져오기
def get_keywords(tree):
    keywords_xpaths = [
        'xpath=/html/body/div[6]/div[1]/div[2]/div[6]/div[1]/p[1]',
        'xpath=/html/body/div[6]/div[1]/div[2]/div[5]/div[1]/p[1]',
        '//*[contains(@class, "writer-tag") and position()=2]'
    ]
    keywords = extract_element(tree, keywords_xpaths)
    keywords_items = {
        '로맨스': '로맨스',
        '무협': '무협',
        '라이트노벨':'라이트노벨',
        '공포':'공포',
        'SF':'SF',
        '스포츠':'스포츠',
        '대체역사':'대체역사',
        '현대판타지':'현대판타지',
        '현대':'현대',
        '판타지':'판타지'
    }

    genre = '기타'
    for key, value in keywords_items.items():
        if key in keywords:
            genre = value
            break

    return keywords, genre
    
# 완결, 연재 여부 확인, 나이 제한 확인
def get_serial(tree):
    serial_elements = tree.xpath('//*[@class="in-badge"]')
    if serial_elements:
        serial_element = serial_elements[0].text_content()
        serial = '완결' if '완결' in serial_element else '연재중'
        age = '19' if '19' in serial_element else '전체'
    else:
        serial, age = '연재중', '전체'  # 기본값
    return serial, age

# 출판사 가져오기
def get_publisher(tree):
    publisher = ''

    return publisher

# 연재 화수 확인
def get_page_count(tree):
    page_count_xpaths = [
        'xpath=/html/body/div[6]/div[1]/div[2]/div[6]/div[2]/div[1]/p[3]/span[2]',
        'xpath=/html/body/div[6]/div[1]/div[2]/div[5]/div[2]/div[1]/p[3]/span[2]',
    ]
    page_counts = tree.xpath('//*[@class="writer-name"]')
    page_count = page_counts[-1].text_content()
    page_unit = '화'
    
    return page_count, page_unit

# 조회수 확인
def get_viewers(tree):
    viewers_xpaths = [
        'xpath=/html/body/div[6]/div[1]/div[2]/div[4]/div[1]/p[1]/span[2]',
        'xpath=/html/body/div[6]/div[1]/div[2]/div[5]/div[1]/p[1]/span[2]'
    ]
    viewers = tree.xpath('//div[contains(@class, "counter-line-a")]//p[1]//span[last()]')
    viewer = viewers[0].text_content()

    return viewer

# 소설 소개 추출
def get_summary(tree):
    summary_xpaths = [
        'xpath=/html/body/div[6]/div[1]/div[2]/div[5]/div[2]/div[2]',
        'xpath=/html/body/div[6]/div[1]/div[2]/div[6]/div[2]/div[2]'
    ]
    summarys = tree.xpath('//*[@class="synopsis"]')
    summary = summarys[0].text_content()

    return summary

# 소설 데이터 가져오기
def get_novel_data(url):
    session = create_session()
    headers = get_headers()
    
    response = session.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    tree = html.fromstring(response.content)
    
    img = get_img(tree)
    title = get_title(tree)
    author = get_author(tree)
    recommend = get_recommend(tree)
    keywords, genre = get_keywords(tree)
    serial, age = get_serial(tree)
    publisher = get_publisher(tree)
    page_count, page_unit = get_page_count(tree)
    viewers = get_viewers(tree)
    summary = get_summary(tree)
    
    novel_data = {
        'url': url,
        'img': img,
        'title': title,
        'author': author,
        'recommend': recommend,
        'genre': genre,
        'serial': serial,
        'publisher': publisher,
        'summary': summary,
        'page_count': page_count,
        'page_unit': page_unit,
        'age': age,
        'platform': 'novelpia',
        'keywords': keywords,
        'viewers': viewers
    }

    # print(novel_data)

    if any(value is None for value in novel_data.values()):
        print(novel_data)
        raise Exception(f'데이터 추출 실패: ', url=url)

    return novel_data

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

# 마지막 번호 추출하기
def get_last_page_num():
    session = create_session()
    headers = get_headers()
    
    response = session.get('https://novelpia.com/plus/all/date/10000/?main_genre=&is_please_write=', headers=headers, timeout=30)
    response.raise_for_status()
    
    tree = html.fromstring(response.content)
    elements = tree.xpath('/html/body/div[8]/div[3]/div[7]/nav/ul/li')
    temp = []
    for element in elements:
        temp.append(element.text_content())
    max_num = max(temp)
    return max_num

# 각 소설 링크들 가져오기
async def get_links(page, url):
    await page.goto(url)
    
    links = []
    elements = await page.locator('xpath=/html/body/div[8]/div[3]/div[6]/div/table/tbody/tr[1]/td[1]').all()
    
    for element in elements:
        onclick_value = await element.get_attribute('onclick')
        if onclick_value:
            # url 추출
            if "location='" in onclick_value:
                url_part = onclick_value.split("location='")[1].split("'")[0]
                full_url = f"https://novelpia.com{url_part}"
                links.append(full_url)
    
    return links

# 로그인하기
async def login(page):
    """로그인 처리"""
    await page.goto('https://novelpia.com/')
    # await page.goto('https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id=A8OQVi3byB1jFOckQ0RZ&redirect_uri=https%3A%2F%2Fnovelpia.com%2Fproc%2Flogin_naver%3Fredirectrurl%3D&state=e52d643d7eca539840bb97c0f697b16c')

    await page.locator('xpath=//*[@id="toggle-menu"]/div/img').click()
    await page.locator('xpath=//*[@id="pc-sidemenu"]/div[2]/div[1]/div[2]/div[1]').click()
    await page.locator('xpath=//*[@id="member_login_modal"]/div/div/div[2]/div[2]/div[2]/a[1]').click()
    
    print("로그인을 완료한 후 Enter를 눌러주세요...")
    input()  # 사용자가 수동으로 로그인 완료할 때까지 대기

# 최대 페이지 가져오기
async def get_last_page(page, url):
    """가장 기본적인 단일 페이지 크롤링 - 페이지 재사용"""
    # 페이지 열기
    try:
        # 페이지 방문
        await page.goto(url)
        
        await page.wait_for_selector('xpath=/html/body/div[8]/div[3]/div[7]/nav/ul/li[9]/a')
        # 클릭 대기 및 실행
        await page.locator('xpath=/html/body/div[8]/div[3]/div[7]/nav/ul/li[9]/a').click()

        # 페이지 번호 요소들 가져오기
        await page.wait_for_selector('xpath=/html/body/div[8]/div[3]/div[7]/nav/ul/li')
        page_num = await page.locator('xpath=/html/body/div[8]/div[3]/div[7]/nav/ul/li').all()
        temp = []
        for n in page_num:
            text = await n.text_content()
            temp.append(text.replace('\n', '').replace(' ',''))
            # temp.append(0)
        # print(temp)
        temp = [int(i) for i in temp if i]
        max_num = max(temp)
        print(f'마지막 번호: {max_num}')
        return max_num
        
    except Exception as e:
        print(f"최대 페이지 수집 에러: {e}")
        return 1   

# 새 페이지 만들기
async def create_page(playwright, user_agent, headless=True):
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

async def start_get_links():
    # 최종 페이지 가져오기
    async with async_playwright() as playwright:
        ua = UserAgent(platforms='desktop')
        page, browser = await create_page(playwright, ua.random, headless=False)
        # 로그인하기
        await login(page)
        print('마지막 번호 가져오기')
        last_page_num = await get_last_page(page, 'https://novelpia.com/plus/all/date/1/?main_genre=&is_please_write=')
    
        # URL 생성
        urls = [f"https://novelpia.com/plus/all/date/{i}/?main_genre=&is_please_write=" for i in range(1, last_page_num)]
        # urls = urls[:1]
        # 각 페이지에서 순차적으로 링크 수집
        all_links = []

            # tqdm 프로그레스 바 생성 
        with tqdm(urls, desc=f"현재 수집된 링크 수: {len(all_links)}", total=len(urls)) as pbar:
            for url in pbar:
                # 링크 수집
                links = await get_links(page, url)
                all_links.extend(links)
                
                # tqdm 설명 동적 업데이트
                pbar.set_description(f"현재 수집된 링크 수: {len(all_links)}")
                
                await asyncio.sleep(random.uniform(4, 10))
        await browser.close()
    return all_links

if __name__ == '__main__':
    page_path = 'data/novelpia_page_links.link'
    data_path = 'data/novelpia_novel_data.data'
    
    os.makedirs('data', exist_ok=True)
    try:
        if os.path.exists(page_path):
            print('데이터가 존재합니다. 기존의 데이터를 가져옵니다.')
            urls = open_files(page_path)
        else:
            # 소설 링크들 가져오기
            urls = asyncio.run(start_get_links())
            # save_files(page_path, urls)
        print(f'가져온 총 URL 개수: {len(urls)}')
        # print()
        all_results = []
        
        while True:
            try:
                if os.path.exists(data_path):
                    cache_urls = open_files(data_path)
                    cache_url = [url['url'] for url in cache_urls]
                    # print(cache_urls)
                    urls = [url for url in urls if url not in cache_url]
                    
                print(f'크롤링할 URL 개수: {len(urls)}')
                
                # urls = urls[:10]
                urls = split_data(urls, 20)
                print('링크 수집 중...')
                for url in urls:
                    results = parmap.map(
                        get_novel_data,
                        url,
                        pm_pbar = True,
                        pm_processes = 5,
                        pm_chunksize=1
                    )

                    time.sleep(random.uniform(2, 10))
                    
                    # links = flatten_results(results)
                    # links = list(chain.from_iterable(results))

                    all_results.extend(results)
                

                # all_results = list(chain.from_iterable(all_results))
                # print(all_results)
                print('크롤링 종료 데이터 저장 시작')
                if os.path.exists(data_path):
                    old_urls = open_files(data_path)
                    old_urls.extend(all_results)
                    save_files(data_path, old_urls)
                else:
                    save_files(data_path, all_results)
                print('데이터 저장 완료')
                break
            except Exception as e:
                # print('크롤링 중 오류 발생', e)
                print('현재 상황을 저장합니다.')
                
                if os.path.exists(data_path):
                    old_urls = open_files(data_path)
                    old_urls.extend(all_results)
                    save_files(data_path, old_urls)
                else:
                    save_files(data_path, all_results)
                print('저장 완료')
    except:
        pass