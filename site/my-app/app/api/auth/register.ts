import { type NextRequest, NextResponse } from "next/server"
import { createUser, getUserByEmail } from "@/lib/database"
import bcrypt from "bcrypt"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { username, email, password, blockedTags = [], preferences = {} } = body

    // 입력 검증
    if (!username || !email || !password) {
      return NextResponse.json({ error: "Username, email, and password are required" }, { status: 400 })
    }

    // 이메일 형식 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      return NextResponse.json({ error: "Invalid email format" }, { status: 400 })
    }

    // 패스워드 길이 검증
    if (password.length < 6) {
      return NextResponse.json({ error: "Password must be at least 6 characters long" }, { status: 400 })
    }

    // 기존 사용자 확인
    const existingUser = await getUserByEmail(email)
    if (existingUser) {
      return NextResponse.json({ error: "User with this email already exists" }, { status: 409 })
    }

    // 패스워드 해시
    const saltRounds = 12
    const passwordHash = await bcrypt.hash(password, saltRounds)

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
      message: "User created successfully",
      user: { username, email }
    })

  } catch (error) {
    console.error("Register API Error:", error)
    return NextResponse.json({ error: "Failed to create user" }, { status: 500 })
  }
}
