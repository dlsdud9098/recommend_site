from playwright.sync_api import sync_playwright
import json

def debug_all_requests():
    all_requests = []
    all_responses = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # 모든 요청 캐치
        def handle_request(request):
            all_requests.append({
                'url': request.url,
                'method': request.method,
                'resource_type': request.resource_type
            })
            print(f'요청: {request.method} {request.url}')
        
        # 모든 응답 캐치
        def handle_response(response):
            all_responses.append({
                'url': response.url,
                'status': response.status,
                'content_type': response.headers.get('content-type', '')
            })
            print(f'응답: {response.status} {response.url}')
        
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        print("페이지 로딩 중...")
        page.goto('https://novelpia.com/plus')
        page.wait_for_load_state('networkidle')
        
        print(f"\n초기 로딩 완료. 요청: {len(all_requests)}개, 응답: {len(all_responses)}개")
        
        # 수동 스크롤로 추가 요청 확인
        print("5초 후 스크롤 시작...")
        page.wait_for_timeout(5000)
        
        for i in range(5):
            print(f"스크롤 {i+1}/5")
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            page.wait_for_timeout(3000)
        
        browser.close()
    
    print(f"\n=== 전체 결과 ===")
    print(f"총 요청: {len(all_requests)}개")
    print(f"총 응답: {len(all_responses)}개")
    
    # JSON 요청들만 필터링
    json_requests = [r for r in all_responses if 'json' in r.get('content_type', '').lower()]
    print(f"JSON 응답: {len(json_requests)}개")
    
    return all_requests, all_responses

# 실행
requests, responses = debug_all_requests()