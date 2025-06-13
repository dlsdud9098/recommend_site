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
        
        await page.wait_for_selector('.col-next')
        # 클릭 대기 및 실행
        await page.locator('.col-next').click()

        # 페이지 번호 요소들 가져오기
        await page.wait_for_selector('xpath=//*[@id="NOVELOUS-CONTENTS"]/section[4]/ul')
        page_num = await page.locator('.col-xs-2').all()
        temp = []
        for n in page_num:
            text = await n.inner_text()
            if text.isdigit():
                temp.append(text)
            # temp.append(0)

        temp = [int(i) for i in temp if i]
        max_num = max(temp)
        return max_num
        
    except Exception as e:
        print(f"최대 페이지 수집 에러: {e}")
        print(page.content())
        return 1

# 링크 가져오기
async def get_links(page, url):
    """단일 페이지에서 링크 수집"""
    try:
        await page.goto(url)
        # await page.wait_for_load_state('networkidle')

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


async def main():
    print("🚀 노벨피아 소설 크롤링 시작!")
    
    # User Agent 설정
    ua = UserAgent()
    user_agent = ua.random
    # 데이터 디렉토리 생성
    os.makedirs('data', exist_ok=True)
    
    async with async_playwright() as playwright:
        # 단일 브라우저 및 페이지 생성
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

        try:

            # 링크 데이터 확인 또는 수집
            if os.path.exists('data/munpia_novel_page_link_data.data'):
                print("📂 기존 링크 데이터 로드 중...")
                with open('data/munpia_novel_page_link_data.data', 'rb') as f:
                    all_links = pickle.load(f)
            else:
                print("🔍 새로운 링크 데이터 수집 중...")
                
                # 최대 페이지 수 가져오기
                last_page_num = await get_last_page(page, 'https://novel.munpia.com/page/hd.platinum/group/pl.serial/view/serial')
                print(f"총 페이지 수: {last_page_num}")
                
                # # URL 생성 (테스트용으로 처음 2페이지만)
                # urls = [f"https://novelpia.com/plus/all/date/{i}/?main_genre=&is_please_write=" for i in range(1, last_page_num)]  # 테스트용
                
                # # 각 페이지에서 순차적으로 링크 수집
                # all_links = []
                # for url in tqdm(urls, desc="📄 페이지별 링크 수집"):
                #     links = await get_links(page, url)
                #     all_links.extend(links)
                #     print(f"수집된 링크 수: {len(links)}")
                
                # # 링크 데이터 저장
                # with open('data/novelpia_novel_page_link_data.data', 'wb') as f:
                #     pickle.dump(all_links, f)
                # print(f"📁 총 {len(all_links)}개 링크 저장 완료")

        except Exception as e:
            print(f"❌ 메인 실행 중 에러: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

            # 데이터 저장
            # if all_results:
            #     print(f"\n💾 데이터 저장 중... ({len(all_results)}개)")
            #     await save_data(all_results)
            # else:
            #     print("❌ 저장할 데이터가 없습니다.")


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