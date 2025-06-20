import { type NextRequest, NextResponse } from "next/server"
import { getUserByEmail, executeQuery } from "@/lib/database"
import bcrypt from "bcrypt"
import jwt from "jsonwebtoken"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email, password } = body

    // 입력 검증
    if (!email || !password) {
      return NextResponse.json({ error: "Email and password are required" }, { status: 400 })
    }

    // 사용자 조회
    const user = await getUserByEmail(email)
    if (!user) {
      return NextResponse.json({ error: "Invalid email or password" }, { status: 401 })
    }

    // 패스워드 검증
    const isPasswordValid = await bcrypt.compare(password, user.password_hash)
    if (!isPasswordValid) {
      return NextResponse.json({ error: "Invalid email or password" }, { status: 401 })
    }

    // 계정 활성화 상태 확인
    if (!user.is_active) {
      return NextResponse.json({ error: "Account is deactivated" }, { status: 403 })
    }

    // 마지막 로그인 시간 업데이트
    await executeQuery(
      "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
      [user.id]
    )

    // JWT 토큰 생성 (실제 환경에서는 JWT_SECRET을 환경변수로 관리)
    const JWT_SECRET = process.env.JWT_SECRET || "your-secret-key"
    const token = jwt.sign(
      { 
        userId: user.id, 
        email: user.email,
        username: user.username 
      },
      JWT_SECRET,
      { expiresIn: '24h' }
    )

    // 사용자 정보 (패스워드 제외)
    const userInfo = {
      id: user.id,
      username: user.username,
      email: user.email,
      createdAt: user.created_at,
      blockedTags: user.blocked_tags ? JSON.parse(user.blocked_tags) : [],
      preferences: user.preferences ? JSON.parse(user.preferences) : {}
    }

    return NextResponse.json({
      success: true,
      message: "Login successful",
      token,
      user: userInfo
    })

  } catch (error) {
    console.error("Login API Error:", error)
    return NextResponse.json({ error: "Login failed" }, { status: 500 })
  }
}
