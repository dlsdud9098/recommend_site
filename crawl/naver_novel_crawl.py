import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import random
from itertools import chain
import os
from fake_useragent import UserAgent
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio
from datetime import datetime
import pickle

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
                # links[(page_title, '19금')] = link
                links.append({
                    'age': '19',
                    'url': link
                })
            else:
                links.append({
                    'age': '전체',
                    'url': link
                })
        
        await asyncio.sleep(random.randint(1, 2))
        return links
    
    except Exception as e:
        print(f"링크 수집 에러 {url}: {e}")
        return []
    finally:
        await browser.close()

# 태그 확인
async def extrac_xpath(page, xpaths, type='text'):
    for xpath in xpaths:
        try:
            # 빈 XPath 체크
            if not xpath or xpath.strip() == '' or xpath == 'xpath=':
                continue
                
            element = page.locator(xpath)
            if await element.count() > 0:
                if type == 'text':
                    data = await element.first.inner_text()
                elif type == 'src':
                    data = await element.first.get_attribute('src')
                
                if data and data.strip():
                    return data.strip()
        except Exception as e:
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
    if age == 'all':
        page, browser = await create_page(playwright, user_agent)

    response = await page.goto(url, timeout=30000)


    if response.status >= 400:
        return {'url': url, 'status': f'HTTP_{response.status}', 'error': 'HTTP Error'}
    
    # 페이지 로딩 대기
    await asyncio.sleep(2)
    
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
        'xpath=//*[@id="ct"]/div[1]/div[1]/div[1]/div[2]/strong'
    ]
    title = await extrac_xpath(page, title_xpaths)        

    # 평점
    rating_xpaths = [
        'xpath=//*[@id="ct"]/div[1]/div[1]/div[1]/div[2]/div[1]/ul/li/span/span',
        'xpath=//*[@id="content"]/div[1]/div[1]/em'
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
        'xpath=//*[@id="content"]/h5'
    ]
    page_unit = await extrac_xpath(page, page_unit_xpaths)
    page_unit = page_unit.strip()[-1]

    age_xpaths = [
        'xpath=//*[@id="content"]/ul[1]/li/ul/li[5]'
    ]
    age = await extrac_xpath(page, age_xpaths)

    author = await extrac_xpath(page, 'xpath=//*[@id="content"]/ul[1]/li/ul/li[3]/a')
    
    novel_data = {
        'url': url,
        'img': img,
        'title': title,
        'athor': author,
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
        data_fields = ['img', 'title', 'rating', 'genre', 'serial', 'publisher', 'summary', 'page_count', 'page_unit', 'age']
        filled_fields = sum(1 for field in data_fields if novel_data.get(field) and novel_data[field] != '')
        print(f"수집된 필드: {filled_fields}/{len(data_fields)}개")
    
    await asyncio.sleep(random.uniform(1, 2))

    if browser:
        try:
            await browser.close()
        except:
            pass

    return novel_data

# 파일 저장하기
async def save_data(results):
    """결과 저장 함수"""
    if not results:
        print("저장할 데이터가 없습니다.")
        return
    
    # 데이터 디렉토리 생성
    os.makedirs('data', exist_ok=True)
    
    # 전체 결과 저장
    df = pd.DataFrame(results)
    filename = f'data/naver_novel_data.csv'
    df.to_csv(filename, encoding='utf-8', index=False)
    
    
    print(f'📁 전체 데이터 저장: {filename} ({len(results)}개)')

# 로그인하기
async def login(page):
    """로그인 처리"""
    await page.goto('https://nid.naver.com/nidlogin.login')
    
    print("로그인을 완료한 후 Enter를 눌러주세요...")
    input()  # 사용자가 수동으로 로그인 완료할 때까지 대기


async def main():
    print("🚀 네이버 소설 크롤링 시작!")
    
    # 데이터 디렉토리 생성
    os.makedirs('data', exist_ok=True)
    
    # 이미 준비되어있는 url이 있는지 확인
    if os.path.exists('data/naver_novel_page_link_data.data'):
        print("📂 기존 링크 파일 로드 중...")
        with open('data/naver_novel_page_link_data.data', 'rb') as f:
            all_urls = pickle.load(f)
        
        all_urls = list(chain.from_iterable(all_urls))

    else:
        print("🔍 링크 수집 시작...")
        page_urls = []
        for i in range(1, 4232):  # 테스트용으로 5페이지만
            page_urls.append(f'https://series.naver.com/novel/categoryProductList.series?categoryTypeCode=all&page={i}')
        

        # page_urls = page_urls[:20]
        # print(len(page_urls))
        urls = split_data(page_urls, 5)

        ua = UserAgent(platforms='desktop')
        print(f"📄 {len(page_urls)}개 페이지에서 링크 수집 중...")
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
                    # return_exceptions=True
                )
                all_links.append(batch_results)

        # 하나로 합치기
        all_urls = list(chain.from_iterable(all_links))
        print(all_urls)
        # 중복 제거 및 저장
        # unique_links = list(set(all_links))
        print(f"🔗 수집된 고유 링크: {len(all_urls)}개")

        
        with open('data/naver_novel_page_link_data.data', 'wb') as f:
            pickle.dump(all_urls, f)

    not_nineteen_links = [link['url'] for link in all_urls if link['age'] != 19]
    nineteen_links = [link['url'] for link in all_urls if link['age'] != 19]

    # 데이터 수집 시작
    total_urls = sum(len(url_list) for url_list in all_urls)
    print(f"\n📊 데이터 수집 시작 - 총 {total_urls}개 URL")
    
    all_results = []
    # print(urls[0])
    
    ua = UserAgent(platforms='desktop')
    
    not_nineteen_links = split_data(not_nineteen_links, 5)
    # 전체 이용가 소설
    async with async_playwright() as playwright:
        # 링크 수집 진행상황 표시
        for url_list in tqdm(not_nineteen_links, desc="📄 페이지별 링크 수집", unit="배치"):
            tasks = [get_data(playwright=playwright, url=url, user_agent=ua.random) for url in url_list]
            
            # tqdm_asyncio로 각 배치 내 태스크 진행상황 표시
            batch_results = await tqdm_asyncio.gather(
                *tasks, 
                desc=f"URL 처리 ({len(url_list)}개)", 
                unit="페이지",
                # return_exceptions=True
            )
            all_results.append(batch_results)
    
    nineteen_links = split_data(nineteen_links, 5)
    # 19세 이용가 소설
    async with async_playwright() as playwright:
        # 단일 브라우저 및 페이지 생성
        browser = await playwright.chromium.launch(
            headless=False,
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
            user_agent=ua.random,
            is_mobile=False,
            has_touch=False,
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()

        try:
            # 로그인 처리
            await login(page)

            # 각 페이지에서 순차적으로 링크 수집
            all_links = []
            print(len(nineteen_links))
            for url in tqdm(nineteen_links, desc="📄 페이지별 링크 수집"):
                links = await get_links(playwright=None, page=page, url=url)
                all_links.extend(links)
                print(f"수집된 링크 수: {len(links)}")
            
        except Exception as e:
            print(f"❌ 메인 실행 중 에러: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()
    
    all_results = list(chain.from_iterable(all_links))
    
    # 데이터 저장
    print(f"\n💾 데이터 저장 중...")
    await save_data(all_results)
    
    return all_results

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