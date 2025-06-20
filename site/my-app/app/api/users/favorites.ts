import { type NextRequest, NextResponse } from "next/server"
import { addToFavorites, removeFromFavorites, executeQuery } from "@/lib/database"
import jwt from "jsonwebtoken"

// JWT 토큰 검증 함수
function verifyToken(request: NextRequest) {
  const authHeader = request.headers.get('authorization')
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    throw new Error('No token provided')
  }

  const token = authHeader.substring(7)
  const JWT_SECRET = process.env.JWT_SECRET || "your-secret-key"
  
  try {
    return jwt.verify(token, JWT_SECRET) as any
  } catch (error) {
    throw new Error('Invalid token')
  }
}

// 즐겨찾기 목록 조회
export async function GET(request: NextRequest) {
  try {
    const decoded = verifyToken(request)
    const userId = decoded.userId

    const searchParams = request.nextUrl.searchParams
    const type = searchParams.get("type") // 'novel', 'webtoon', 'all'

    let query = ""
    let params: any[] = [userId]

    if (type === 'novel') {
      query = `
        SELECT n.*, 'novel' as type
        FROM user_novel_favorites unf
        JOIN novels n ON unf.novel_id = n.id
        WHERE unf.user_id = ?
        ORDER BY unf.created_at DESC
      `
    } else if (type === 'webtoon') {
      query = `
        SELECT w.*, 'webtoon' as type
        FROM user_webtoon_favorites uwf
        JOIN webtoons w ON uwf.webtoon_id = w.id
        WHERE uwf.user_id = ?
        ORDER BY uwf.created_at DESC
      `
    } else {
      // 모든 즐겨찾기 조회
      query = `
        (SELECT n.*, 'novel' as type, unf.created_at as favorited_at
         FROM user_novel_favorites unf
         JOIN novels n ON unf.novel_id = n.id
         WHERE unf.user_id = ?)
        UNION ALL
        (SELECT w.*, 'webtoon' as type, uwf.created_at as favorited_at
         FROM user_webtoon_favorites uwf
         JOIN webtoons w ON uwf.webtoon_id = w.id
         WHERE uwf.user_id = ?)
        ORDER BY favorited_at DESC
      `
      params = [userId, userId]
    }

    const results = await executeQuery(query, params) as any[]

    const favorites = results.map((row: any) => ({
      id: row.id,
      title: row.title,
      author: row.author,
      type: row.type,
      coverImage: row.img || "/placeholder.svg?height=400&width=300",
      rating: row.recommend ? row.recommend / 250 : 0,
      episodes: row.page_count || 0,
      tags: row.keywords ? JSON.parse(row.keywords) : [],
      description: row.summary || '',
      views: row.viewers || 0,
      genre: row.genre || '',
      siteUrl: row.url || '',
      platform: row.platform || '',
      favoritedAt: row.favorited_at
    }))

    return NextResponse.json(favorites)

  } catch (error) {
    console.error("Favorites GET Error:", error)
    if (error.message === 'No token provided' || error.message === 'Invalid token') {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }
    return NextResponse.json({ error: "Failed to get favorites" }, { status: 500 })
  }
}

// 즐겨찾기 추가
export async function POST(request: NextRequest) {
  try {
    const decoded = verifyToken(request)
    const userId = decoded.userId

    const body = await request.json()
    const { contentId, type } = body

    if (!contentId || !type || (type !== 'novel' && type !== 'webtoon')) {
      return NextResponse.json({ error: "contentId and type (novel/webtoon) are required" }, { status: 400 })
    }

    await addToFavorites(userId, contentId, type)

    return NextResponse.json({ success: true, message: "Added to favorites" })

  } catch (error) {
    console.error("Favorites POST Error:", error)
    if (error.message === 'No token provided' || error.message === 'Invalid token') {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }
    return NextResponse.json({ error: "Failed to add to favorites" }, { status: 500 })
  }
}

// 즐겨찾기 제거
export async function DELETE(request: NextRequest) {
  try {
    const decoded = verifyToken(request)
    const userId = decoded.userId

    const body = await request.json()
    const { contentId, type } = body

    if (!contentId || !type || (type !== 'novel' && type !== 'webtoon')) {
      return NextResponse.json({ error: "contentId and type (novel/webtoon) are required" }, { status: 400 })
    }

    await removeFromFavorites(userId, contentId, type)

    return NextResponse.json({ success: true, message: "Removed from favorites" })

  } catch (error) {
    console.error("Favorites DELETE Error:", error)
    if (error.message === 'No token provided' || error.message === 'Invalid token') {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }
    return NextResponse.json({ error: "Failed to remove from favorites" }, { status: 500 })
  }
}
