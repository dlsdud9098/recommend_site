#!/usr/bin/env python3
"""
웹툰/소설 크롤링 데이터를 데이터베이스에 삽입하는 스크립트
"""

import requests
import json
import sys
from typing import Dict, List, Any

# Next.js API 엔드포인트
API_BASE_URL = "http://localhost:3000/api"

def insert_content_data(content_type: str, data: Dict[str, Any]) -> bool:
    """
    크롤링한 데이터를 API를 통해 데이터베이스에 삽입
    
    Args:
        content_type: 'novel' 또는 'webtoon'
        data: 크롤링한 데이터 딕셔너리
    
    Returns:
        성공 여부
    """
    try:
        url = f"{API_BASE_URL}/contents"
        payload = {
            "type": content_type,
            "data": data
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ {data.get('title', 'Unknown')} - {result.get('message', 'Success')}")
            return True
        else:
            print(f"✗ Error inserting {data.get('title', 'Unknown')}: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Exception inserting {data.get('title', 'Unknown')}: {str(e)}")
        return False

def insert_batch_data(content_type: str, data_list: List[Dict[str, Any]]) -> None:
    """
    배치로 여러 데이터를 삽입
    
    Args:
        content_type: 'novel' 또는 'webtoon'
        data_list: 크롤링한 데이터 리스트
    """
    success_count = 0
    total_count = len(data_list)
    
    print(f"\n=== {content_type.upper()} 데이터 삽입 시작 ({total_count}개) ===")
    
    for i, data in enumerate(data_list, 1):
        print(f"[{i}/{total_count}] ", end="")
        if insert_content_data(content_type, data):
            success_count += 1
    
    print(f"\n=== 삽입 완료: {success_count}/{total_count} 성공 ===\n")

def load_crawled_data(file_path: str) -> List[Dict[str, Any]]:
    """
    크롤링된 JSON 파일을 로드
    
    Args:
        file_path: JSON 파일 경로
    
    Returns:
        데이터 리스트
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    except Exception as e:
        print(f"파일 로드 오류: {str(e)}")
        return []

def validate_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    데이터 유효성 검사 및 기본값 설정
    
    Args:
        data: 원본 데이터
    
    Returns:
        검증된 데이터
    """
    validated = {
        'url': data.get('url', ''),
        'img': data.get('img', ''),
        'title': data.get('title', ''),
        'author': data.get('author', ''),
        'recommend': int(data.get('recommend', 0)),
        'genre': data.get('genre', ''),
        'serial': data.get('serial', ''),
        'publisher': data.get('publisher', ''),
        'summary': data.get('summary', ''),
        'page_count': int(data.get('page_count', 0)),
        'page_unit': data.get('page_unit', '화'),
        'age': data.get('age', '전체이용가'),
        'platform': data.get('platform', 'unknown'),
        'keywords': data.get('keywords', []),
        'viewers': int(data.get('viewers', 0))
    }
    
    # keywords가 문자열인 경우 리스트로 변환
    if isinstance(validated['keywords'], str):
        validated['keywords'] = [validated['keywords']]
    
    return validated

def main():
    """메인 함수"""
    if len(sys.argv) < 3:
        print("사용법: python insert_data.py <type> <json_file>")
        print("예시: python insert_data.py novel novels_data.json")
        print("타입: novel 또는 webtoon")
        sys.exit(1)
    
    content_type = sys.argv[1]
    json_file = sys.argv[2]
    
    if content_type not in ['novel', 'webtoon']:
        print("타입은 'novel' 또는 'webtoon'이어야 합니다.")
        sys.exit(1)
    
    # 데이터 로드
    raw_data = load_crawled_data(json_file)
    if not raw_data:
        print("데이터를 로드할 수 없습니다.")
        sys.exit(1)
    
    # 데이터 검증
    validated_data = []
    for item in raw_data:
        try:
            validated_item = validate_data(item)
            validated_data.append(validated_item)
        except Exception as e:
            print(f"데이터 검증 오류: {str(e)} - {item}")
    
    if not validated_data:
        print("유효한 데이터가 없습니다.")
        sys.exit(1)
    
    # 배치 삽입
    insert_batch_data(content_type, validated_data)

if __name__ == "__main__":
    main()
