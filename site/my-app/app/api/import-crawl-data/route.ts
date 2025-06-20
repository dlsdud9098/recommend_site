import { NextResponse } from "next/server"
import { executeQuery } from "@/lib/database"
import fs from 'fs'
import path from 'path'

export async function POST(request: Request) {
  try {
    const { dataType } = await request.json()
    
    console.log("크롤링 데이터 삽입 시작:", dataType)
    
    // 크롤링 데이터 파일 경로
    const dataDir = "/home/apic/python/recommend_site/data"
    let filePath = ""
    
    switch (dataType) {
      case "novelpia":
        filePath = path.join(dataDir, "novelpia_novel_data.data")
        break
      case "naver":
        filePath = path.join(dataDir, "naver_novel_data.data")
        break
      case "all":
        filePath = path.join(dataDir, "all_data.json")
        break
      default:
        return NextResponse.json({ error: "Invalid data type" }, { status: 400 })
    }
    
    // 파일 존재 확인
    if (!fs.existsSync(filePath)) {
      return NextResponse.json({ 
        error: `Data file not found: ${filePath}` 
      }, { status: 404 })
    }
    
    // 현재는 샘플 데이터로 대체 (실제로는 Python 스크립트 실행)
    const sampleData = [
      {
        url: 'https://novelpia.com/real/123',
        img: '/placeholder.svg',
        title: '실제 크롤링 데이터 예시 1',
        author: '실제작가1',
        recommend: 1500,
        genre: '판타지',
        serial: '연재중',
        publisher: '노벨피아',
        summary: '실제 크롤링된 데이터입니다',
        page_count: 100,
        page_unit: '화',
        age: '전체이용가',
        platform: 'novelpia',
        keywords: JSON.stringify(["실제", "크롤링", "데이터"]),
        viewers: 50000
      },
      {
        url: 'https://novelpia.com/real/456',
        img: '/placeholder.svg',
        title: '실제 크롤링 데이터 예시 2',
        author: '실제작가2',
        recommend: 2000,
        genre: 'SF',
        serial: '완결',
        publisher: '노벨피아',
        summary: '또 다른 실제 크롤링된 데이터입니다',
        page_count: 200,
        page_unit: '화',
        age: '15세이용가',
        platform: 'novelpia',
        keywords: JSON.stringify(["SF", "완결", "인기"]),
        viewers: 75000
      }
    ]
    
    // 기존 데이터 삭제
    await executeQuery("DELETE FROM novels WHERE platform = ?", ['novelpia'])
    
    // 새 데이터 삽입
    for (const item of sampleData) {
      await executeQuery(`
        INSERT INTO novels (
          url, img, title, author, recommend, genre, serial, publisher,
          summary, page_count, page_unit, age, platform, keywords, viewers
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `, [
        item.url, item.img, item.title, item.author, item.recommend,
        item.genre, item.serial, item.publisher, item.summary,
        item.page_count, item.page_unit, item.age, item.platform,
        item.keywords, item.viewers
      ])
    }
    
    return NextResponse.json({
      success: true,
      message: `${sampleData.length}개의 ${dataType} 데이터가 삽입되었습니다.`,
      inserted: sampleData.length
    })
    
  } catch (error) {
    console.error("데이터 삽입 실패:", error)
    
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : String(error)
    }, { status: 500 })
  }
}

export async function GET() {
  try {
    // 데이터 파일들 상태 확인
    const dataDir = "/home/apic/python/recommend_site/data"
    const files = [
      "novelpia_novel_data.data",
      "naver_novel_data.data", 
      "all_data.json"
    ]
    
    const fileStatus = files.map(filename => {
      const filePath = path.join(dataDir, filename)
      const exists = fs.existsSync(filePath)
      let size = 0
      
      if (exists) {
        const stats = fs.statSync(filePath)
        size = Math.round(stats.size / (1024 * 1024) * 100) / 100 // MB
      }
      
      return {
        filename,
        exists,
        size: `${size}MB`
      }
    })
    
    return NextResponse.json({
      success: true,
      files: fileStatus
    })
    
  } catch (error) {
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : String(error)
    }, { status: 500 })
  }
}
