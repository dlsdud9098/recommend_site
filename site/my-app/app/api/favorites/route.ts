import { type NextRequest, NextResponse } from "next/server"
import { addToFavorites, removeFromFavorites, executeQuery } from "@/lib/database"

// 즐겨찾기 목록 조회
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const userId = searchParams.get("userId")
    const type = searchParams.get("type") // 'novel', 'webtoon', 'all'

    if (!userId) {
      return NextResponse.json({ error: "User ID is required" }, { status: 400 })
    }

    let query = ""
    let params: any[] = [parseInt(userId)]

    if (type === "novel") {
      query = `
        SELECT 
          n.id,
          n.url,
          n.img as coverImage,
          n.title,
          n.author,
          n.recommend,
          n.genre,
          n.serial,
          n.summary as description,
          n.page_count as episodes,
          n.viewers as views,
          n.platform,
          JSON_EXTRACT(n.keywords, '$') as keywords,
          'novel' as type,
          f.created_at as favoriteDate
        FROM user_novel_favorites f
        JOIN novels n ON f.novel_id = n.id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
      `
    } else if (type === "webtoon") {
      query = `
        SELECT 
          w.id,
          w.url,
          w.img as coverImage,
          w.title,
          w.author,
          w.recommend,
          w.genre,
          w.serial,
          w.summary as description,
          w.page_count as episodes,
          w.viewers as views,
          w.platform,
          JSON_EXTRACT(w.keywords, '$') as keywords,
          'webtoon' as type,
          f.created_at as favoriteDate
        FROM user_webtoon_favorites f
        JOIN webtoons w ON f.webtoon_id = w.id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
      `
    } else {
      // 모든 즐겨찾기 (소설 + 웹툰)
      query = `
        (SELECT 
          n.id,
          n.url,
          n.img as coverImage,
          n.title,
          n.author,
          n.recommend,
          n.genre,
          n.serial,
          n.summary as description,
          n.page_count as episodes,
          n.viewers as views,
          n.platform,
          JSON_EXTRACT(n.keywords, '$') as keywords,
          'novel' as type,
          f.created_at as favoriteDate
        FROM user_novel_favorites f
        JOIN novels n ON f.novel_id = n.id
        WHERE f.user_id = ?)
        UNION ALL
        (SELECT 
          w.id,
          w.url,
          w.img as coverImage,
          w.title,
          w.author,
          w.recommend,
          w.genre,
          w.serial,
          w.summary as description,
          w.page_count as episodes,
          w.viewers as views,
          w.platform,
          JSON_EXTRACT(w.keywords, '$') as keywords,
          'webtoon' as type,
          f.created_at as favoriteDate
        FROM user_webtoon_favorites f
        JOIN webtoons w ON f.webtoon_id = w.id
        WHERE f.user_id = ?)
        ORDER BY favoriteDate DESC
      `
      params = [parseInt(userId), parseInt(userId)]
    }

    const results = await executeQuery(query, params) as any[]

    const favorites = results.map((row: any) => ({
      id: row.id,
      title: row.title,
      author: row.author,
      type: row.type,
      coverImage: row.coverImage || "/placeholder.svg?height=400&width=300",
      rating: row.recommend ? row.recommend / 250 : 0,
      episodes: row.episodes || 0,
      tags: row.keywords ? (typeof row.keywords === 'string' ? JSON.parse(row.keywords) : row.keywords) : [],
      description: row.description || '',
      views: row.views || 0,
      genre: row.genre || '',
      siteUrl: row.url || '',
      platform: row.platform || '',
      serial: row.serial || '',
      favoriteDate: row.favoriteDate
    }))

    return NextResponse.json(favorites)
  } catch (error) {
    console.error("Get Favorites Error:", error)
    return NextResponse.json({ error: "Failed to fetch favorites" }, { status: 500 })
  }
}

// 즐겨찾기 추가
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { userId, contentId, type } = body

    if (!userId || !contentId || !type) {
      return NextResponse.json({ error: "User ID, content ID, and type are required" }, { status: 400 })
    }

    if (type !== 'novel' && type !== 'webtoon') {
      return NextResponse.json({ error: "Type must be 'novel' or 'webtoon'" }, { status: 400 })
    }

    await addToFavorites(userId, contentId, type)

    return NextResponse.json({ success: true, message: "Added to favorites" })
  } catch (error) {
    console.error("Add Favorite Error:", error)
    return NextResponse.json({ error: "Failed to add to favorites" }, { status: 500 })
  }
}

// 즐겨찾기 제거
export async function DELETE(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const userId = searchParams.get("userId")
    const contentId = searchParams.get("contentId")
    const type = searchParams.get("type")

    if (!userId || !contentId || !type) {
      return NextResponse.json({ error: "User ID, content ID, and type are required" }, { status: 400 })
    }

    if (type !== 'novel' && type !== 'webtoon') {
      return NextResponse.json({ error: "Type must be 'novel' or 'webtoon'" }, { status: 400 })
    }

    await removeFromFavorites(parseInt(userId), parseInt(contentId), type as 'novel' | 'webtoon')

    return NextResponse.json({ success: true, message: "Removed from favorites" })
  } catch (error) {
    console.error("Remove Favorite Error:", error)
    return NextResponse.json({ error: "Failed to remove from favorites" }, { status: 500 })
  }
}
