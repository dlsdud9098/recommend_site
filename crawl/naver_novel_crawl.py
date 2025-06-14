import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import random
from itertools import chain
import os
from fake_useragent import UserAgent
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio
import pickle
import time

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

# 링크 가져오기
async def get_links(playwright, url):
    browser = await playwright.chromium.launch(headless=True)  # headless로 변경
    context = await browser.new_context()
    page = await context.new_page()
    
    try:
        await page.goto(url, timeout=30000)

        # 다양한 url 패턴
        xpath_patterns = [
            '//*[@id="content"]/div/ul/li/div/h3'
        ]

        # 링크 가져오기
        links = []

        page_list = await page.locator('xpath=//*[@id="content"]/div/ul/li/div/h3').all()
        for page_tag in page_list:
            page_title = await page_tag.inner_text()
            link = 'https://series.naver.com' + await page_tag.locator('xpath=//a[contains(@href, "/novel/detail")]').get_attribute('href')
            if '19금' in page_title:    
                age = 19
            else:
                age = 0
            links.append({
                'url': link,
                'age': age,
            })
            
        await asyncio.sleep(random.randint(1, 2))
        return links
    
    except Exception as e:
        print(f"링크 수집 에러 {url}: {e}")
        return []
    finally:
        await browser.close()

async def get_last_page(page):
    await page.goto('https://series.naver.com/novel/categoryProductList.series?categoryTypeCode=all&page=100000')
    page_elements = await page.locator('xpath=//*[@id="content"]/p/a').all()
    page_list = []
    for element in page_elements:
        page_list.append(await element.inner_text())
    max_page_num = max(page_list)
    return max_page_num

# 태그 확인
async def extrac_xpath(page, xpaths, type='text'):
    for xpath in xpaths:
        try:                
            element = page.locator(xpath)
            if await element.count() > 0:
                if type == 'text':
                    data = await element.first.inner_text()
                elif type == 'src':
                    data = await element.first.get_attribute('src')
                
                if data and data.strip():
                    return data.strip()
        except Exception as e:
            print(e)
            continue
    return ''

# 소설 데이터 가져오기
async def create_page(playwright, user_agent):
    browser = None
    try:
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
        
        return page, browser
        
    except Exception as e:
        print(f'에러: {e}')

async def get_data(playwright=None, page=None, url=None, user_agent=None, age='all'):
    try:
        if age == 0:
            page, browser = await create_page(playwright, user_agent)
        else:
            page, browser = await create_page(playwright, user_agent)

        error_page_count = 0
        response_max_error_count = 3
        while True:
            if error_page_count == response_max_error_count:
                raise Exception(f'페이지 새로고침 {response_max_error_count}번 실패했습니다.')
            if response.status != 200:
                error_page_count += 1
                
                os.system('nordvpn connect South_Korea')
                await asyncio.sleep(120)
                response = await page.goto(url, timeout=50000)
            else:
                break
        # 페이지 로딩 대기
        await asyncio.sleep(1)
        
        # 이미지
        img_xpaths = [
            'xpath=/html/body/div[1]/div[2]/div[1]/span/img',
            'xpath=//*[@id="container"]/div[1]/a/img',
            'xpath=//*[@id="container"]/div[1]/span/img',
            'xpath=//*[@id="ct"]/div[1]/div[1]/div[1]/div[1]/a/img'
        ]
        img = await extrac_xpath(page, img_xpaths, type='src')

        # 제목
        title_xpaths = [
            'xpath=//*[@id="content"]/div[1]/h2',
            'xpath=//*[@id="ct"]/div[1]/div[1]/div[1]/div[2]/strong',
            'xpath=//*[@id="content"]/div[2]',
            'xpath=//*[@id="content"]/div[2]/h2'
        ]
        title = await extrac_xpath(page, title_xpaths)        

        # 평점
        rating_xpaths = [
            'xpath=//*[@id="content"]/div[2]/div[1]',
            'xpath=//*[@id="ct"]/div[1]/div[1]/div[1]/div[2]/div[1]/ul/li/span/span',
            'xpath=//*[@id="content"]/div[1]/div[1]/em',
        ]
        rating = await extrac_xpath(page, rating_xpaths)

        # 장르
        genre_xpaths = [
            'xpath=//*[@id="content"]/ul[1]/li/ul/li[2]/span/a',
            'xpath=//*[@id="ct"]/div[1]/div[1]/div[1]/div[2]/div[2]/ul/li[1]/dl/dd[2]'
        ]
        genre = await extrac_xpath(page, genre_xpaths)

        # 연재상태
        serial_xpaths = [
            'xpath=//*[@id="content"]/ul[1]/li/ul/li[1]/span',
            'xpath=//*[@id="ct"]/div[1]/div[1]/div[1]/div[2]/div[2]/ul/li[1]/dl/dd[1]'
        ]
        serial = await extrac_xpath(page, serial_xpaths)

        # 출판사
        publisher_xpaths = [
            'xpath=//*[@id="content"]/ul[1]/li/ul/li[4]/a'
        ]
        publisher = await extrac_xpath(page, publisher_xpaths)
        author = await extrac_xpath(page, 'xpath=//*[@id="content"]/ul[1]/li/ul/li[3]/a')

        # 소설 설명글
        summary_xpaths = [
            'xpath=//*[@id="content"]/div[2]'
        ]

        if await page.locator('xpath=//*[@id="content"]/div[2]/div[1]/span/a').count() > 0:
            await page.locator('xpath=//*[@id="content"]/div[2]/div[1]/span/a').click()

        summary = await extrac_xpath(page, summary_xpaths)

        # 총 화수
        page_count_xpaths = [
            'xpath=//*[@id="content"]/h5/strong'
        ]
        page_count = await extrac_xpath(page, page_count_xpaths)

        # 단위(화, 권)
        page_unit_xpaths = [
            '.end_total_episode'
        ]
        page_unit = await extrac_xpath(page, page_unit_xpaths)
        try:
            page_unit = page_unit.strip()[-1]
        except:
            print(page_unit)
            

        age_xpaths = [
            'xpath=//*[@id="content"]/ul[1]/li/ul/li[5]'
        ]
        age = await extrac_xpath(page, age_xpaths)

        
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
            'platform': 'naver'
        }


        # 디버깅 정보
        if not all([title, rating, genre, serial, publisher, summary, page_count, page_unit, age]):
            print(f"데이터 누락: {page.url}")
            print(novel_data)
            raise Exception('데이터 누락 발생')
        

        if browser:
            try:
                await browser.close()
            except:
                pass

        return novel_data
    except Exception as e:
        print(url, e)

# 로그인하기
async def login(page):
    """로그인 처리"""
    await page.goto('https://nid.naver.com/nidlogin.login')
    
    print("로그인을 완료한 후 Enter를 눌러주세요...")
    input()  # 사용자가 수동으로 로그인 완료할 때까지 대기

# 데이터 불러오기
async def open_files(path):
    with open(path, 'rb') as f:
        links = pickle.load(f)
    return links

# 데이터 저장하기
async def save_files(path, data):
    with open(path, 'wb') as f:
        pickle.dump(data, f)

async def main():
    print("🚀 네이버 소설 크롤링 시작!")
    
    # 데이터 디렉토리 생성
    os.makedirs('data', exist_ok=True)

    novel_data_path = 'data/naver_novel_data.data'
    novel_page_path = 'data/naver_page_links.link'
    ua = UserAgent(platforms='desktop')
    
    # 이미 준비되어있는 url이 있는지 확인
    if os.path.exists(novel_page_path):
        all_urls = await open_files(novel_page_path)
        all_urls = [url['url'] for url in all_urls]

    all_urls = []

    async with async_playwright() as playwright:
        page, browser = await create_page(playwright, ua.random)
        max_page_num = await get_last_page(page)

        # max_page_num = '1'
        for i in range(1, int(max_page_num.replace(',', '')) + 1):  # 테스트용으로 5페이지만
            all_urls.append(f'https://series.naver.com/novel/categoryProductList.series?categoryTypeCode=all&page={i}')
        await browser.close()

    all_urls = all_urls[:5]
    urls = split_data(all_urls, 5)
    all_links = []
    async with async_playwright() as playwright:
        # 링크 수집 진행상황 표시
        for url_list in tqdm(urls, desc="📄 페이지별 링크 수집", unit="배치"):
            tasks = [get_links(playwright, url) for url in url_list]
            
            # tqdm_asyncio로 각 배치 내 태스크 진행상황 표시
            batch_results = await tqdm_asyncio.gather(
                *tasks, 
                desc=f"URL 처리 ({len(url_list)}개)", 
                unit="페이지",
            )
            all_links.extend(batch_results)

    # 하나로 합치기
    all_urls = list(chain.from_iterable(all_links))
    await save_files(novel_page_path, all_urls)
        

    ua = UserAgent(platforms='desktop')
    while True:
        # 기존에 크롤링 했던 데이터 목록과 비교해서 없는 url만 가져오기
        if os.path.exists(novel_data_path):
            old_urls = await open_files(novel_data_path)
            old_urls = [url['url'] for url in old_urls]

            all_urls = [url for url in all_urls if url['url'] not in old_urls]

        # 나이별 분류
        not_nineteen_links = [link for link in all_urls if link['age'] == 0]
        nineteen_links = [link for link in all_urls if link['age'] == 19]

        not_nineteen_links = split_data(not_nineteen_links, 5)
        all_results = []
        # 전체 이용가 소설 데이터 수집
        try:
            async with async_playwright() as playwright:
                for url_list in tqdm(not_nineteen_links, desc="📄 페이지별 링크 수집", unit="배치"):
                    tasks = [get_data(playwright=playwright, url=url['url'], user_agent=ua.random, age = url['age']) for url in url_list]
                    
                    # tqdm_asyncio로 각 배치 내 태스크 진행상황 표시
                    batch_results = await tqdm_asyncio.gather(
                        *tasks, 
                        desc=f"URL 처리 ({len(url_list)}개)", 
                        unit="페이지",
                    )
                    all_results.append(batch_results)
                    await asyncio.sleep(random.uniform(1, 2))
            if all_results:
                print('데이터 저장')
                all_results = list(chain.from_iterable(all_links))
                await save_files(novel_data_path, all_results)
                break
        except Exception as e:
            print('데이터 추출 오류')
            print(e)
            print('현재 상황을 저장합니다.')

            old_data = await open_files(novel_data_path)
            old_data.extend(all_results)
            await save_files(novel_data_path, old_data)
        
if __name__ == "__main__":
    try:
        results = asyncio.run(main())
        print("\n🎊 모든 작업이 완료되었습니다!")
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 실행 중 에러: {e}")
        import traceback
        traceback.print_exc()