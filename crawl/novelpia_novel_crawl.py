import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import random
import os
from fake_useragent import UserAgent
from tqdm import tqdm
import pickle
from tqdm.asyncio import tqdm_asyncio
import traceback
from Crawl_Exception import PageRefreshException, DataExtractionException


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
            text = await n.inner_text()
            temp.append(text)
            temp.append(0)

        temp = [int(i) for i in temp if i]
        max_num = max(temp)
        print(f'마지막 번호: {max_num}')
        return max_num
        
    except Exception as e:
        print(f"최대 페이지 수집 에러: {e}")
        return 1   

# 데이터 불러오기
async def open_files(file):
    with open(file, 'rb') as f:
        cache_data = pickle.load(f)
        
    return cache_data

# 데이터 저장하기
async def save_files(file, data):
    with open(file, 'wb') as f:
        pickle.dump(data, f)

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

# 요소 가져오기
async def extract_element(page, xpaths, type='text'):
    # 추천 수
    try:
        for xpath in xpaths:
            if await page.locator(xpath).count() > 0:
                if type == 'img':
                    img = await page.locator(xpath).get_attribute('src')
                    return img
                data = await page.locator(xpath).inner_text()
                return data
    except Exception as e:
        print(xpath)
        print(e)

# 이미지 가져오기
async def get_img(page):
    img_xpaths = [
        'xpath=/html/body/div[6]/div[1]/div[1]/a/img',
        'xpath=/html/body/div[6]/div[1]/div[1]/img',
        '.conver_img',
        'body > div:nth-child(18) > div.epnew-wrapper.s_inv.side_padding > div.epnew-cover-box > a > img'
    ]
    img = await extract_element(page, img_xpaths, 'img')

    return img

# 제목 가져오기
async def get_title(page):
    title_xpaths = [
        'div.epnew-novel-title',
        'xpath=/html/body/div[6]/div[1]/div[2]/div[2]'
    ]
    title = await extract_element(page, title_xpaths)

    return title

# 작가 가져오기
async def get_author(page):
    author_xpaths = [
        'xpath=/html/body/div[6]/div[1]/div[2]/div[3]/p[1]/a',
        'div.writer-name'
    ]
    author = await extract_element(page, author_xpaths)

    return author

# 추천 수 가져오기
async def get_recommend(page):
    recommend_xpaths = [
        'xpath=/html/body/div[6]/div[1]/div[2]/div[4]/div[1]/p[2]/span[2]',
        'xpath=/html/body/div[6]/div[1]/div[2]/div[5]/div[1]/p[2]/span[2]'
    ]
    # 추천 수
    recommend = await extract_element(page, recommend_xpaths)

    return recommend

# 키워드, 태그, 장르 가져오기
async def get_keywords(page):
    keywords_xpaths = [
        'xpath=/html/body/div[6]/div[1]/div[2]/div[6]/div[1]/p[1]',
        'xpath=/html/body/div[6]/div[1]/div[2]/div[5]/div[1]/p[1]',
        '.writer-tag:nth-child(2)'
    ]
    keywords = await extract_element(page, keywords_xpaths)
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
async def get_serial(page):
    serial_element = await page.locator('.in-badge').inner_text()
    if '완결' in serial_element:
        serial = '완결'
    else:
        serial = '연재중'
    
    if '19' in serial_element:
        age = '19'
    else:
        age = '전체'

    return serial, age

# 출판사 가져오기
async def get_publisher(page):
    publisher = ''

    return publisher

# 연재 화수 확인
async def get_page_count(page):
    page_count_xpaths = [
        'xpath=/html/body/div[6]/div[1]/div[2]/div[6]/div[2]/div[1]/p[3]/span[2]',
        'xpath=/html/body/div[6]/div[1]/div[2]/div[5]/div[2]/div[1]/p[3]/span[2]',
    ]
    page_count = await page.locator('.writer-name').last.inner_text()
    page_unit = '화'
    
    return page_count, page_unit

# 조회수 확인
async def get_viewers(page):
    viewers_xpaths = [
        'xpath=/html/body/div[6]/div[1]/div[2]/div[4]/div[1]/p[1]/span[2]',
        'xpath=/html/body/div[6]/div[1]/div[2]/div[5]/div[1]/p[1]/span[2]'
    ]
    viewers = await page.locator('.counter-line-a p:first-child span:last-child').inner_text()

    return viewers

# 소설 소개 추출
async def get_summary(page):
    summary_xpaths = [
        'xpath=/html/body/div[6]/div[1]/div[2]/div[5]/div[2]/div[2]',
        'xpath=/html/body/div[6]/div[1]/div[2]/div[6]/div[2]/div[2]'
    ]
    summary = await page.locator('.synopsis').first.inner_text()

    return summary

# 각 url에서 소설 정보 가져오기
async def get_data(page, url): 
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        response = await page.goto(url, timeout=30000)  # 30초 타임아웃
        
        if response.status != 200:
            retry_count += 1
            if retry_count < max_retries:
                print(f"HTTP {response.status} 오류. 재시도 {retry_count}/{max_retries}")
                
                # VPN 재연결 (선택적)
                try:
                    os.system('nordvpn connect South_Korea')
                    await asyncio.sleep(120)  # 1분 대기
                except:
                    pass
                continue
            else:
                raise Exception(f'HTTP {response.status} 오류가 {max_retries}번 반복됨')
        
        break
    # 페이지 로드 완료 대기
    await page.wait_for_load_state('networkidle')
    
    # 데이터 추출
    novel_data = await extract_novel_info(page, url)
    
    return novel_data

async def extract_novel_info(page, url):
    img = await get_img(page)
    title = await get_title(page)
    author = await get_author(page)
    recommend = await get_recommend(page)
    keywords, genre = await get_keywords(page)
    serial, age = await get_serial(page)
    publisher = await get_publisher(page)
    page_count, page_unit = await get_page_count(page)
    viewers = await get_viewers(page)
    summary = await get_summary(page)
    
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

    if any(value is None for value in novel_data.values()):
        print(novel_data)
        raise Exception(f'데이터 추출 실패: ', url=url)

    return novel_data
        
async def main():
    # User Agent 설정
    ua = UserAgent(platforms='desktop')
    
    # 데이터 저장할 폴더 만들기
    os.makedirs('data', exist_ok=True)
    
    page_link_path = 'data/novelpia_page_links.link'
    novel_data_path = 'data/novelpia_novel_data.data'
    
    if not os.path.exists(page_link_path):
        # 최종 페이지 가져오기
        async with async_playwright() as playwright:
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
        await save_files(page_link_path, all_links)
    else:
        all_links = await open_files(page_link_path)
        print(f'총 URL: {len(all_links)}')

    # 소설 정보 가져오기
    while True:
        async with async_playwright() as playwright:
            if os.path.exists(novel_data_path):
                cache_urls = await open_files(novel_data_path)
                cache_urls = [url['url'] for url in cache_urls]
                urls = [link for link in all_links if link not in cache_urls]
                print(f'수집할 URL 개수: {len(urls)}')
            else:
                urls = all_links

            if not urls:
                print("크롤링할 새로운 URL이 없습니다.")
                break
            
            print(len(urls))

            datas = []
            page, browser = await create_page(playwright, ua.random)

            try:
                with tqdm(urls, desc=f"현재 수집된 링크 수: {len(datas)}", total=len(urls)) as pbar:
                    for url in pbar:
                        novel_data = await get_data(page, url)
                        datas.append(novel_data)

                        # tqdm 설명 동적 업데이트
                        pbar.set_description(f"현재 수집된 링크 수: {len(datas)}")
                        await asyncio.sleep(2, 4)
                if datas:
                    print('데이터 저장')
                    await save_files(novel_data_path, datas)
                    break
                
            except Exception as e:
                print('데이터 추출 오류')
                print(e)
                print('현재 상황을 저장합니다.')

                if os.path.exists(novel_data_path):
                    old_data = await open_files(novel_data_path)
                    old_data.extend(datas)
                    await save_files(novel_data_path, old_data)
                else:
                    await save_files(novel_data_path, datas)
            finally:
                await browser.close()
                continue

if __name__ == '__main__':
    asyncio.run(main())