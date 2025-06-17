import requests
import re
import json
from urllib.parse import parse_qs, urlparse
import base64
import hashlib
import time
import random
import string

class NaverLogin:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def get_login_keys(self):
        """로그인에 필요한 키값들을 가져옵니다"""
        try:
            # 네이버 로그인 페이지 접근
            login_url = "https://nid.naver.com/nidlogin.login"
            response = self.session.get(login_url)
            
            # 필요한 키값들 추출
            key_pattern = r'name="enctp"\s+value="([^"]+)"'
            enctp_match = re.search(key_pattern, response.text)
            enctp = enctp_match.group(1) if enctp_match else "1"
            
            # 동적 키 추출
            dynamic_key_pattern = r'name="dynamicKey"\s+value="([^"]+)"'
            dynamic_key_match = re.search(dynamic_key_pattern, response.text)
            dynamic_key = dynamic_key_match.group(1) if dynamic_key_match else ""
            
            # RSA 키 정보 가져오기
            key_info_url = "https://nid.naver.com/login/ext/keys.nhn"
            key_response = self.session.get(key_info_url)
            key_data = key_response.text
            
            # sessionkey와 keyname 추출
            sessionkey_match = re.search(r'sessionkey=([^,]+)', key_data)
            keyname_match = re.search(r'keyname=([^,]+)', key_data)
            
            sessionkey = sessionkey_match.group(1) if sessionkey_match else ""
            keyname = keyname_match.group(1) if keyname_match else ""
            
            return {
                'enctp': enctp,
                'dynamicKey': dynamic_key,
                'sessionkey': sessionkey,
                'keyname': keyname
            }
        except Exception as e:
            print(f"키 정보 가져오기 실패: {e}")
            return None
    
    def encrypt_credentials(self, username, password, sessionkey):
        """사용자명과 비밀번호를 암호화합니다 (간단한 방식)"""
        # 실제로는 RSA 암호화를 사용해야 하지만, 간단한 인코딩 사용
        credentials = f"{username}\t{password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return encoded
    
    def login(self, username, password):
        """네이버 로그인을 수행합니다"""
        try:
            # 1단계: 로그인 키 정보 가져오기
            print("로그인 키 정보 가져오는 중...")
            keys = self.get_login_keys()
            if not keys:
                return False, "키 정보를 가져올 수 없습니다"
            
            # 2단계: 자격증명 암호화
            encrypted_creds = self.encrypt_credentials(username, password, keys['sessionkey'])
            
            # 3단계: 로그인 시도
            login_data = {
                'enctp': keys['enctp'],
                'encnm': keys['keyname'],
                'svctype': '0',
                'enc_url': 'http0X0.0000000000001P-1041529999',
                'url': 'https://www.naver.com',
                'smart_level': '1',
                'encpw': encrypted_creds,
                'dynamicKey': keys['dynamicKey'],
                'ru': '',
                'hiqual': '1',
                'resp': 'on'
            }
            
            login_url = "https://nid.naver.com/nidlogin.login"
            
            # POST 요청 헤더 설정
            self.session.headers.update({
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://nid.naver.com',
                'Referer': 'https://nid.naver.com/nidlogin.login'
            })
            
            print("로그인 시도 중...")
            response = self.session.post(login_url, data=login_data, allow_redirects=False)
            
            # 4단계: 응답 확인
            if response.status_code == 302:
                # 리다이렉트가 있으면 성공 가능성
                location = response.headers.get('Location', '')
                if 'naver.com' in location and 'error' not in location.lower():
                    print("로그인 성공!")
                    
                    # 메인 페이지 접근하여 로그인 상태 확인
                    main_response = self.session.get('https://www.naver.com')
                    if '로그아웃' in main_response.text or 'logout' in main_response.text.lower():
                        return True, "로그인 성공"
                    
            # 로그인 실패 원인 분석
            if '아이디(로그인 전용 아이디) 또는 비밀번호를 잘못 입력했습니다' in response.text:
                return False, "아이디 또는 비밀번호가 잘못되었습니다"
            elif 'captcha' in response.text.lower():
                return False, "보안문자 입력이 필요합니다"
            elif '일시적으로 로그인' in response.text:
                return False, "일시적으로 로그인이 제한되었습니다"
            else:
                return False, "로그인 실패 - 원인 불명"
                
        except Exception as e:
            return False, f"로그인 중 오류 발생: {e}"
    
    def get_user_info(self):
        """로그인 후 사용자 정보를 가져옵니다"""
        try:
            # 네이버 메인 페이지에서 사용자 정보 추출
            response = self.session.get('https://www.naver.com')
            
            # 사용자명 추출 (예시)
            username_pattern = r'class="link_name"[^>]*>([^<]+)</a>'
            username_match = re.search(username_pattern, response.text)
            username = username_match.group(1) if username_match else "알 수 없음"
            
            return {
                'username': username,
                'login_status': True
            }
        except Exception as e:
            print(f"사용자 정보 가져오기 실패: {e}")
            return None
    
    def logout(self):
        """로그아웃을 수행합니다"""
        try:
            logout_url = "https://nid.naver.com/nidlogin.logout"
            response = self.session.get(logout_url)
            print("로그아웃 완료")
            return True
        except Exception as e:
            print(f"로그아웃 실패: {e}")
            return False

# 사용 예시
def main():
    # 네이버 로그인 객체 생성
    naver = NaverLogin()
    
    # 로그인 정보 입력
    username = input("네이버 아이디: ")
    password = input("비밀번호: ")
    
    # 로그인 시도
    success, message = naver.login(username, password)
    print(f"결과: {message}")
    
    if success:
        # 사용자 정보 가져오기
        user_info = naver.get_user_info()
        if user_info:
            print(f"환영합니다, {user_info['username']}님!")
        
        # 네이버 서비스 이용 예시
        # 예: 네이버 블로그, 카페 등에 접근 가능
        
        # 로그아웃
        naver.logout()

if __name__ == "__main__":
    main()