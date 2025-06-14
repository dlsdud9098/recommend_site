import json
import time
import requests
from datetime import datetime
from typing import List, Dict, Any
import pickle
import os

# 커스텀 예외 클래스들
class NovelCrawlingException(Exception):
    """소설 크롤링 관련 기본 예외"""
    def __init__(self, message, url=None, current_state=None):
        self.message = message
        self.url = url
        self.current_state = current_state
        self.timestamp = datetime.now()
        super().__init__(self.message)

class PageRefreshException(NovelCrawlingException):
    """페이지 새로고침 관련 예외"""
    pass

class DataExtractionException(NovelCrawlingException):
    """데이터 추출 관련 예외"""
    pass

class NetworkException(NovelCrawlingException):
    """네트워크 관련 예외"""
    pass

# 크롤링 상태 관리 클래스
class NovelCrawlingState:
    def __init__(self, urls: List[str], save_file: str = ""):
        self.urls = urls
        self.save_file = save_file
        self.current_index = 0
        self.completed_urls = []
        self.failed_urls = []
        self.scraped_data = []
        self.start_time = datetime.now()
        self.last_save_time = None
        self.retry_count = 0
        
        # 이전 상태가 있으면 복구
        self.load_state()
    
    def save_state(self):
        """현재 상태를 파일에 저장"""
        state_data = {
            'urls': self.urls,
            'current_index': self.current_index,
            'completed_urls': self.completed_urls,
            'failed_urls': self.failed_urls,
            'scraped_data': self.scraped_data,
            'start_time': self.start_time,
            'last_save_time': datetime.now(),
            'retry_count': self.retry_count
        }
        
        with open(self.save_file, 'wb') as f:
            pickle.dump(state_data, f)
        
        print(f"📁 상태 저장됨: {len(self.completed_urls)}/{len(self.urls)} 완료, {len(self.failed_urls)} 실패")
    
    def load_state(self):
        """저장된 상태 복구"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'rb') as f:
                    state_data = pickle.load(f)
                
                self.current_index = state_data.get('current_index', 0)
                self.completed_urls = state_data.get('completed_urls', [])
                self.failed_urls = state_data.get('failed_urls', [])
                self.scraped_data = state_data.get('scraped_data', [])
                self.start_time = state_data.get('start_time', datetime.now())
                self.last_save_time = state_data.get('last_save_time')
                self.retry_count = state_data.get('retry_count', 0)
                
                print(f"🔄 이전 상태 복구됨: {len(self.completed_urls)}/{len(self.urls)} 완료")
                if self.last_save_time:
                    print(f"⏰ 마지막 저장 시간: {self.last_save_time}")
                
            except Exception as e:
                print(f"❌ 상태 복구 실패: {e}")
    
    def get_progress(self):
        """진행률 반환"""
        total = len(self.urls)
        completed = len(self.completed_urls)
        failed = len(self.failed_urls)
        return {
            'total': total,
            'completed': completed,
            'failed': failed,
            'remaining': total - completed - failed,
            'progress_percent': (completed + failed) / total * 100 if total > 0 else 0
        }
    
    def save_final_results(self):
        """최종 결과를 JSON으로 저장"""
        results = {
            'scraped_data': self.scraped_data,
            'failed_urls': self.failed_urls,
            'summary': self.get_progress(),
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'total_retry_count': self.retry_count
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'novel_results_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"📊 최종 결과가 {filename}에 저장됨")
        return filename