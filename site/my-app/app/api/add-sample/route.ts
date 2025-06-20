import { NextResponse } from "next/server"
import { executeQuery } from "@/lib/database"

export async function POST() {
  try {
    console.log("샘플 데이터 추가 시작...")
    
    // 샘플 소설 데이터
    const sampleNovels = [
      {
        url: 'https://novelpia.com/novel/100001',
        img: '/placeholder.svg',
        title: '전지적 독자 시점',
        author: '싱숑',
        recommend: 2500,
        genre: '판타지',
        serial: '완결',
        publisher: '문피아',
        summary: '소설 속 세상이 현실이 되었을 때, 유일하게 결말을 아는 독자의 이야기',
        page_count: 551,
        page_unit: '화',
        age: '전체이용가',
        platform: 'munpia',
        keywords: JSON.stringify(["판타지", "게임", "회귀", "현대판타지"]),
        viewers: 150000
      },
      {
        url: 'https://novelpia.com/novel/100002',
        img: '/placeholder.svg',
        title: '나 혼자만 레벨업',
        author: '추공',
        recommend: 3000,
        genre: '판타지',
        serial: '완결',
        publisher: '카카오페이지',
        summary: '세계 최약체 헌터가 시스템을 얻고 최강이 되어가는 이야기',
        page_count: 270,
        page_unit: '화',
        age: '전체이용가',
        platform: 'kakao',
        keywords: JSON.stringify(["판타지", "액션", "레벨업", "헌터"]),
        viewers: 200000
      },
      {
        url: 'https://novelpia.com/novel/100003',
        img: '/placeholder.svg',
        title: '악역의 엔딩은 죽음뿐',
        author: '권규리',
        recommend: 2200,
        genre: '로맨스',
        serial: '완결',
        publisher: '리디북스',
        summary: '소설 속 악역으로 빙의한 여주인공의 생존기',
        page_count: 180,
        page_unit: '화',
        age: '15세이용가',
        platform: 'ridibooks',
        keywords: JSON.stringify(["로맨스", "빙의", "악역", "궁정"]),
        viewers: 95000
      }
    ]
    
    // 샘플 웹툰 데이터
    const sampleWebtoons = [
      {
        url: 'https://comic.naver.com/webtoon/detail/758037',
        img: '/placeholder.svg',
        title: '신의 탑',
        author: 'SIU',
        recommend: 3500,
        genre: '판타지',
        serial: '연재중',
        publisher: '네이버웹툰',
        summary: '탑을 오르는 소년 스물다섯번째 밤의 모험',
        page_count: 590,
        page_unit: '화',
        age: '전체이용가',
        platform: 'naver',
        keywords: JSON.stringify(["판타지", "액션", "모험", "탑"]),
        viewers: 250000
      },
      {
        url: 'https://comic.naver.com/webtoon/detail/183559',
        img: '/placeholder.svg',
        title: '마음의 소리',
        author: '조석',
        recommend: 4000,
        genre: '일상',
        serial: '완결',
        publisher: '네이버웹툰',
        summary: '조석과 친구들의 일상을 그린 개그 웹툰',
        page_count: 1122,
        page_unit: '화',
        age: '전체이용가',
        platform: 'naver',
        keywords: JSON.stringify(["개그", "일상", "조석", "유머"]),
        viewers: 500000
      },
      {
        url: 'https://webtoon.kakao.com/content/화산귀환',
        img: '/placeholder.svg',
        title: '화산귀환',
        author: '비가',
        recommend: 3200,
        genre: '무협',
        serial: '연재중',
        publisher: '카카오웹툰',
        summary: '화산파 최고의 검객이 과거로 돌아가 다시 시작하는 이야기',
        page_count: 180,
        page_unit: '화',
        age: '15세이용가',
        platform: 'kakao',
        keywords: JSON.stringify(["무협", "회귀", "검객", "화산파"]),
        viewers: 180000
      }
    ]
    
    // 기존 데이터 클리어 (선택사항)
    await executeQuery("DELETE FROM novels WHERE id > 2")
    await executeQuery("DELETE FROM webtoons WHERE id > 1")
    
    // 소설 데이터 삽입
    for (const novel of sampleNovels) {
      await executeQuery(`
        INSERT INTO novels (url, img, title, author, recommend, genre, serial, publisher, 
                           summary, page_count, page_unit, age, platform, keywords, viewers)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `, [
        novel.url, novel.img, novel.title, novel.author, novel.recommend,
        novel.genre, novel.serial, novel.publisher, novel.summary,
        novel.page_count, novel.page_unit, novel.age, novel.platform,
        novel.keywords, novel.viewers
      ])
    }
    
    // 웹툰 데이터 삽입
    for (const webtoon of sampleWebtoons) {
      await executeQuery(`
        INSERT INTO webtoons (url, img, title, author, recommend, genre, serial, publisher, 
                             summary, page_count, page_unit, age, platform, keywords, viewers)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `, [
        webtoon.url, webtoon.img, webtoon.title, webtoon.author, webtoon.recommend,
        webtoon.genre, webtoon.serial, webtoon.publisher, webtoon.summary,
        webtoon.page_count, webtoon.page_unit, webtoon.age, webtoon.platform,
        webtoon.keywords, webtoon.viewers
      ])
    }
    
    return NextResponse.json({
      success: true,
      message: `${sampleNovels.length}개의 소설과 ${sampleWebtoons.length}개의 웹툰 데이터가 추가되었습니다.`
    })
    
  } catch (error) {
    console.error("샘플 데이터 추가 실패:", error)
    
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : String(error)
    }, { status: 500 })
  }
}
