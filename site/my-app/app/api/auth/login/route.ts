import { type NextRequest, NextResponse } from "next/server"
import { getUserByEmail, executeQuery } from "@/lib/database"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email, password } = body

    // 입력값 검증
    if (!email || !password) {
      return NextResponse.json({ error: "Email and password are required" }, { status: 400 })
    }

    // 사용자 조회
    const user = await getUserByEmail(email)
    if (!user) {
      return NextResponse.json({ error: "Invalid credentials" }, { status: 401 })
    }

    // 비밀번호 확인
    const crypto = require('crypto')
    const passwordHash = crypto.createHash('sha256').update(password + 'your_salt_here').digest('hex')
    
    if (user.password_hash !== passwordHash) {
      return NextResponse.json({ error: "Invalid credentials" }, { status: 401 })
    }

    // 마지막 로그인 시간 업데이트
    await executeQuery(
      "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
      [user.id]
    )

    // 사용자 정보 반환 (비밀번호 제외)
    const { password_hash, ...userInfo } = user
    
    return NextResponse.json({
      success: true,
      message: "Login successful",
      user: {
        ...userInfo,
        blockedTags: user.blocked_tags ? JSON.parse(user.blocked_tags) : [],
        preferences: user.preferences ? JSON.parse(user.preferences) : {}
      }
    })
  } catch (error) {
    console.error("Login Error:", error)
    return NextResponse.json({ error: "Login failed" }, { status: 500 })
  }
}
