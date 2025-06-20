import { type NextRequest, NextResponse } from "next/server"
import { createUser, getUserByEmail } from "@/lib/database"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { username, email, password, blockedTags = [], preferences = {} } = body

    // 입력값 검증
    if (!username || !email || !password) {
      return NextResponse.json({ error: "Username, email, and password are required" }, { status: 400 })
    }

    // 이메일 형식 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      return NextResponse.json({ error: "Invalid email format" }, { status: 400 })
    }

    // 기존 사용자 확인
    const existingUser = await getUserByEmail(email)
    if (existingUser) {
      return NextResponse.json({ error: "User already exists with this email" }, { status: 409 })
    }

    // 간단한 비밀번호 해싱 (실제 환경에서는 bcrypt 사용 권장)
    const crypto = require('crypto')
    const passwordHash = crypto.createHash('sha256').update(password + 'your_salt_here').digest('hex')

    // 사용자 생성
    await createUser({
      username,
      email,
      passwordHash,
      blockedTags,
      preferences
    })

    return NextResponse.json({ 
      success: true, 
      message: "User registered successfully",
      user: { username, email }
    })
  } catch (error) {
    console.error("Registration Error:", error)
    return NextResponse.json({ error: "Failed to register user" }, { status: 500 })
  }
}
