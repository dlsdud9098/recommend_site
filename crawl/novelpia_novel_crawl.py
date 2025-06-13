import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import random
import os
from fake_useragent import UserAgent
from tqdm import tqdm
import pickle
from tqdm.asyncio import tqdm_asyncio
from fake_useragent import UserAgent

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

# 최대 페이지 가져오기
async def get_last_page(page, url):
    """가장 기본적인 단일 페이지 크롤링 - 페이지 재사용"""
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
        return max_num
        
    except Exception as e:
        print(f"최대 페이지 수집 에러: {e}")
        return 1

# 링크 가져오기
async def get_links(page, url):
    """단일 페이지에서 링크 수집"""
    try:
        await page.goto(url)
        await page.wait_for_load_state('networkidle')

        links = []
        elements = await page.locator('xpath=/html/body/div[8]/div[3]/div[6]/div/table/tbody/tr[1]/td[1]').all()
        
        for element in elements:
            onclick_value = await element.get_attribute('onclick')
            # print(onclick_value)
            if onclick_value:
                # onclick="location='/novel/25974';" 에서 URL 부분 추출
                if "location='" in onclick_value:
                    url_part = onclick_value.split("location='")[1].split("'")[0]
                    full_url = f"https://novelpia.com{url_part}"
                    links.append(full_url)
                    
                    # 제목도 함께 추출
                    title = await element.inner_text()
                    # print(f"제목: {title}, URL: {full_url}")
        
        await asyncio.sleep(random.uniform(4, 15))
        return links
        
    except Exception as e:
        print(f"링크 수집 에러 {url}: {e}")
        return []

async def login(page):
    """로그인 처리"""
    await page.goto('https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id=A8OQVi3byB1jFOckQ0RZ&redirect_uri=https%3A%2F%2Fnovelpia.com%2Fproc%2Flogin_naver%3Fredirectrurl%3D&state=e52d643d7eca539840bb97c0f697b16c')
    
    print("로그인을 완료한 후 Enter를 눌러주세요...")
    input()  # 사용자가 수동으로 로그인 완료할 때까지 대기

async def save_data(results):
    """결과 저장 함수"""
    if not results:
        print("저장할 데이터가 없습니다.")
        return
    
    # 데이터 디렉토리 생성
    os.makedirs('data', exist_ok=True)
    
    # 전체 결과 저장
    df = pd.DataFrame(results)
    filename = f'data/novelpia_novel_data.csv'
    df.to_csv(filename, encoding='utf-8', index=False)
    
    print(f'📁 전체 데이터 저장: {filename} ({len(results)}개)')

async def extract_element(page, xpaths, type='text'):
    # 추천 수
    for xpath in xpaths:
        if await page.locator(xpath).count() > 0:
            if type == 'img':
                img = await page.locator(xpath).get_attribute('src')
                return img
            data = await page.locator(xpath).inner_text()
            return data

async def get_data(playwright, url, user_agent):
    """단일 페이지에서 소설 데이터 수집"""
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

        while True:
            response = await page.goto(url)
            if response.status != 200:
                print('페이지 새로고침')
                os.system('nordvpn connect South_Korea')
                await asyncio.sleep(10)
                response = await page.goto(url, timeout=30000)
            else:
                break
        # await page.wait_for_load_state('networkidle')
        
        # 요소들이 로드될 때까지 대기
        # await page.wait_for_selector('.epnew-novel-title', timeout=15000)
        
        img_xpaths = [
            'xpath=/html/body/div[6]/div[1]/div[1]/a/img',
            'xpath=/html/body/div[6]/div[1]/div[1]/img',
            '.conver_img',
            'body > div:nth-child(18) > div.epnew-wrapper.s_inv.side_padding > div.epnew-cover-box > a > img'
            # 'img.s_inv:nth-child(5)'
        ]   
        img = await extract_element(page, img_xpaths, type='img')
        title_xpaths = [
            'div.epnew-novel-title',
            'xpath=/html/body/div[6]/div[1]/div[2]/div[2]'
        ]
        # title = await page.locator('.ep-info-line.epnew-novel-title').inner_text()
        title = await extract_element(page, title_xpaths)
        
        author_xpaths = [
            'xpath=/html/body/div[6]/div[1]/div[2]/div[3]/p[1]/a',
            'div.writer-name'
        ]
        author = await extract_element(page, author_xpaths)
        # author = await page.locator('.writer-name').inner_text()
        
        recommend_xpaths = [
            'xpath=/html/body/div[6]/div[1]/div[2]/div[4]/div[1]/p[2]/span[2]',
            'xpath=/html/body/div[6]/div[1]/div[2]/div[5]/div[1]/p[2]/span[2]'
        ]
        
        # 추천 수
        recommend = await extract_element(page, recommend_xpaths)
        # recommend = await page.locator('.counter-line-a p:last-child span:last-child').inner_text()
        keywords_xpaths = [
            'xpath=/html/body/div[6]/div[1]/div[2]/div[6]/div[1]/p[1]',
            'xpath=/html/body/div[6]/div[1]/div[2]/div[5]/div[1]/p[1]',
            '.writer-tag:nth-child(2)'
        ]
        keywords = await extract_element(page, keywords_xpaths)
        # keywords = await page.locator('p.writer-tag').first.inner_text()
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
        genre = None
        for key, value in keywords_items.items():
            if key in keywords:
                genre = value
                break
        
        serial_element = await page.locator('.in-badge').inner_text()
        # serial_element = await page.locator('xpath=/html/body/div[6]/div[1]/div[2]/div[3]/p[2]').inner_text()
        if '완결' in serial_element:
            serial = '완결'
        else:
            serial = '연재중'
        
        publisher = ''
        page_count_xpaths = [
            'xpath=/html/body/div[6]/div[1]/div[2]/div[6]/div[2]/div[1]/p[3]/span[2]',
            'xpath=/html/body/div[6]/div[1]/div[2]/div[5]/div[2]/div[1]/p[3]/span[2]',
        ]
        # page_count = await extract_element(page, page_count_xpaths)
        page_count = await page.locator('.writer-name').last.inner_text()
        page_unit = '화'
        
        if '19' in serial_element:
            age = '19'
        else:
            age = '전체'

        viewers_xpaths = [
            'xpath=/html/body/div[6]/div[1]/div[2]/div[4]/div[1]/p[1]/span[2]',
            'xpath=/html/body/div[6]/div[1]/div[2]/div[5]/div[1]/p[1]/span[2]'
        ]
        # viewers = await extract_element(page, viewers_xpaths)
        viewers = await page.locator('.counter-line-a p:first-child span:last-child').inner_text()
        summary_xpaths = [
            'xpath=/html/body/div[6]/div[1]/div[2]/div[5]/div[2]/div[2]',
            'xpath=/html/body/div[6]/div[1]/div[2]/div[6]/div[2]/div[2]'
        ]
        # summary = await extract_element(page, summary_xpaths)
        summary = await page.locator('.synopsis').first.inner_text()
        
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
        
        # 랜덤 대기 시간
        await asyncio.sleep(random.uniform(10,30))
        return novel_data
        
    except Exception as e:
        print(f"[ERROR] {url}: {e}")
        page_source = await page.content()
        with open('page.html', 'w') as f:
            f.write(page_source)
        return None

async def main():
    print("🚀 노벨피아 소설 크롤링 시작!")
    
    # User Agent 설정
    ua = UserAgent()
    user_agent = ua.random
    # 데이터 디렉토리 생성
    os.makedirs('data', exist_ok=True)
    if os.path.exists('data/novelpia_novel_page_link_data.data'):
        with open('data/novelpia_novel_page_link_data.data', 'rb') as f:
            all_links = pickle.load(f)
    else:
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
                user_agent=user_agent,
                is_mobile=False,
                has_touch=False,
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()

            try:
                # 로그인 처리
                await login(page)

                # 링크 데이터 확인 또는 수집
                if os.path.exists('data/novelpia_novel_page_link_data.data'):
                    print("📂 기존 링크 데이터 로드 중...")
                    with open('data/novelpia_novel_page_link_data.data', 'rb') as f:
                        all_links = pickle.load(f)
                else:
                    print("🔍 새로운 링크 데이터 수집 중...")
                    
                    # 최대 페이지 수 가져오기
                    last_page_num = await get_last_page(page, 'https://novelpia.com/plus/all/date/1/?main_genre=&is_please_write=')
                    print(f"총 페이지 수: {last_page_num}")
                    
                    # URL 생성 (테스트용으로 처음 2페이지만)
                    urls = [f"https://novelpia.com/plus/all/date/{i}/?main_genre=&is_please_write=" for i in range(1, last_page_num)]  # 테스트용
                    
                    # 각 페이지에서 순차적으로 링크 수집
                    all_links = []
                    for url in tqdm(urls, desc="📄 페이지별 링크 수집"):
                        links = await get_links(page, url)
                        all_links.extend(links)
                        print(f"수집된 링크 수: {len(links)}")
                    
                    # 링크 데이터 저장
                    with open('data/novelpia_novel_page_link_data.data', 'wb') as f:
                        pickle.dump(all_links, f)
                    print(f"📁 총 {len(all_links)}개 링크 저장 완료")

            except Exception as e:
                print(f"❌ 메인 실행 중 에러: {e}")
                import traceback
                traceback.print_exc()
            
            finally:
                await browser.close()

    # all_links = all_links[:10]
    all_links = split_data(all_links, 5)

    all_results = []
    async with async_playwright() as playwright:
        # 링크 수집 진행상황 표시
        for url_list in tqdm(all_links, desc="📄 페이지별 링크 수집", unit="배치"):
            tasks = [get_data(playwright, url, ua.random) for url in url_list]
            
            # tqdm_asyncio로 각 배치 내 태스크 진행상황 표시
            batch_results = await tqdm_asyncio.gather(
                *tasks, 
                desc=f"URL 처리 ({len(url_list)}개)", 
                unit="페이지",
                # return_exceptions=True
            )
            all_results.extend(batch_results)

    # 데이터 저장
    if all_results:
        print(f"\n💾 데이터 저장 중... ({len(all_results)}개)")
        await save_data(all_results)
    else:
        print("❌ 저장할 데이터가 없습니다.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
        print("\n🎊 모든 작업이 완료되었습니다!")
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 실행 중 에러: {e}")
        import traceback
        traceback.print_exc()