import { NextResponse } from "next/server"
import { executeQuery } from "@/lib/database"

export async function GET() {
  try {
    console.log("데이터베이스 내용 확인 중...")
    
    // 소설 데이터 확인
    const novels = await executeQuery("SELECT * FROM novels LIMIT 10")
    
    // 웹툰 데이터 확인
    const webtoons = await executeQuery("SELECT * FROM webtoons LIMIT 10")
    
    return NextResponse.json({
      success: true,
      novels: novels,
      webtoons: webtoons,
      novelCount: (novels as any[]).length,
      webtoonCount: (webtoons as any[]).length
    })
    
  } catch (error) {
    console.error("데이터베이스 내용 확인 실패:", error)
    
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : String(error)
    }, { status: 500 })
  }
}
