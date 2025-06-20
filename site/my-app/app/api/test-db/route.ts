import { NextResponse } from "next/server"
import { getPool } from "@/lib/database"

export async function GET() {
  try {
    console.log("데이터베이스 연결 테스트 시작...")
    
    const pool = getPool()
    const [result] = await pool.execute("SELECT 1 as test")
    
    console.log("데이터베이스 연결 성공!")
    
    // 테이블 존재 확인
    const [tables] = await pool.execute("SHOW TABLES")
    
    return NextResponse.json({
      success: true,
      message: "데이터베이스 연결 성공",
      tables: tables,
      testResult: result
    })
    
  } catch (error) {
    console.error("데이터베이스 연결 실패:", error)
    
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : String(error),
      details: error instanceof Error ? error.stack : "No stack trace"
    }, { status: 500 })
  }
}
