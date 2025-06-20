import { type NextRequest, NextResponse } from "next/server"
import { getContents } from "@/lib/database"
import type { FilterOptions } from "@/lib/database"

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams

    const filters: FilterOptions = {
      type: (searchParams.get("type") as "all" | "webtoon" | "novel") || "all",
      title: searchParams.get("title") || undefined,
      author: searchParams.get("author") || undefined,
      genre: searchParams.get("genre") || undefined,
      platform: searchParams.get("platform") || undefined,
      serial: searchParams.get("serial") || undefined,
      age: searchParams.get("age") || undefined,
      keywords: searchParams.get("keywords")?.split(",").filter(Boolean) || undefined,
      tags: searchParams.get("tags")?.split(",").filter(Boolean) || undefined, // 호환성을 위해 keywords와 동일하게 처리
      minEpisodes: searchParams.get("minEpisodes") ? Number.parseInt(searchParams.get("minEpisodes")!) : undefined,
      maxEpisodes: searchParams.get("maxEpisodes") ? Number.parseInt(searchParams.get("maxEpisodes")!) : undefined,
      minRating: searchParams.get("minRating") ? Number.parseFloat(searchParams.get("minRating")!) : undefined,
      maxRating: searchParams.get("maxRating") ? Number.parseFloat(searchParams.get("maxRating")!) : undefined,
      minViewers: searchParams.get("minViewers") ? Number.parseInt(searchParams.get("minViewers")!) : undefined,
      maxViewers: searchParams.get("maxViewers") ? Number.parseInt(searchParams.get("maxViewers")!) : undefined,
      blockedGenres: searchParams.get("blockedGenres")?.split(",").filter(Boolean) || [],
      blockedTags: searchParams.get("blockedTags")?.split(",").filter(Boolean) || [],
      sortBy: (searchParams.get("sortBy") as "popularity" | "rating" | "views" | "recommend" | "newest" | "viewers") || "popularity",
      limit: searchParams.get("limit") ? Number.parseInt(searchParams.get("limit")!) : 50,
      offset: searchParams.get("offset") ? Number.parseInt(searchParams.get("offset")!) : 0,
      showAdultContent: searchParams.get("showAdultContent") === "true",
    }

    // tags가 있으면 keywords에도 추가 (호환성)
    if (filters.tags && filters.tags.length > 0) {
      filters.keywords = [...(filters.keywords || []), ...filters.tags]
    }

    // 성인 콘텐츠 필터링
    if (!filters.showAdultContent) {
      // age가 '성인' 또는 '19세 이용가' 등인 것들을 제외
      if (!filters.blockedTags) filters.blockedTags = []
      // 실제로는 age 필드로 필터링하지만, 임시로 여기서 처리
    }

    console.log("API 요청 필터:", filters)
    const contents = await getContents(filters)
    console.log("조회된 컨텐츠 수:", contents.length)

    return NextResponse.json(contents)
  } catch (error) {
    console.error("API Error:", error)
    console.error("Error stack:", error instanceof Error ? error.stack : "No stack trace")
    return NextResponse.json({ 
      error: "Internal Server Error",
      details: error instanceof Error ? error.message : String(error)
    }, { status: 500 })
  }
}

// POST 요청으로 새로운 컨텐츠 추가 (크롤링 데이터 삽입용)
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { type, data } = body // type: 'novel' | 'webtoon', data: 크롤링된 데이터

    if (!type || !data) {
      return NextResponse.json({ error: "Missing type or data" }, { status: 400 })
    }

    if (type !== 'novel' && type !== 'webtoon') {
      return NextResponse.json({ error: "Invalid type. Must be 'novel' or 'webtoon'" }, { status: 400 })
    }

    // 크롤링 데이터를 데이터베이스에 삽입
    const { executeQuery } = await import("@/lib/database")
    
    const table = type === 'novel' ? 'novels' : 'webtoons'
    
    const query = `
      INSERT INTO ${table} (
        url, img, title, author, recommend, genre, serial, publisher, 
        summary, page_count, page_unit, age, platform, keywords, viewers
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ON DUPLICATE KEY UPDATE
        img = VALUES(img),
        recommend = VALUES(recommend),
        genre = VALUES(genre),
        serial = VALUES(serial),
        publisher = VALUES(publisher),
        summary = VALUES(summary),
        page_count = VALUES(page_count),
        page_unit = VALUES(page_unit),
        age = VALUES(age),
        keywords = VALUES(keywords),
        viewers = VALUES(viewers),
        updated_at = CURRENT_TIMESTAMP
    `

    const keywordsJson = Array.isArray(data.keywords) ? JSON.stringify(data.keywords) : data.keywords

    await executeQuery(query, [
      data.url,
      data.img,
      data.title,
      data.author,
      data.recommend || 0,
      data.genre,
      data.serial,
      data.publisher,
      data.summary,
      data.page_count || 0,
      data.page_unit || '화',
      data.age,
      data.platform,
      keywordsJson,
      data.viewers || 0
    ])

    return NextResponse.json({ success: true, message: `${type} data inserted successfully` })
  } catch (error) {
    console.error("POST API Error:", error)
    return NextResponse.json({ error: "Failed to insert data" }, { status: 500 })
  }
}
