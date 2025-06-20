import { type NextRequest, NextResponse } from "next/server"
import { executeQuery } from "@/lib/database"

export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const id = Number.parseInt(params.id)
    const searchParams = request.nextUrl.searchParams
    const type = searchParams.get("type") // 'novel' 또는 'webtoon'

    if (!type || (type !== 'novel' && type !== 'webtoon')) {
      return NextResponse.json({ error: "Type parameter is required and must be 'novel' or 'webtoon'" }, { status: 400 })
    }

    const table = type === 'novel' ? 'novels' : 'webtoons'

    const query = `
      SELECT 
        id,
        url,
        img as coverImage,
        title,
        author,
        recommend,
        genre,
        serial,
        publisher,
        summary as description,
        page_count as pageCount,
        page_unit as pageUnit,
        age,
        platform,
        JSON_EXTRACT(keywords, '$') as keywords,
        viewers,
        created_at as createdAt,
        updated_at as updatedAt
      FROM ${table}
      WHERE id = ?
    `

    const results = (await executeQuery(query, [id])) as any[]

    if (results.length === 0) {
      return NextResponse.json({ error: "Content not found" }, { status: 404 })
    }

    const row = results[0]
    const content = {
      id: row.id,
      title: row.title,
      author: row.author,
      type: type,
      coverImage: row.coverImage || "/placeholder.svg?height=400&width=300",
      rating: row.recommend ? row.recommend / 250 : 0, // recommend를 5점 만점으로 변환
      episodes: row.pageCount || 0,
      tags: row.keywords ? (typeof row.keywords === 'string' ? JSON.parse(row.keywords) : row.keywords) : [],
      keywords: row.keywords ? (typeof row.keywords === 'string' ? JSON.parse(row.keywords) : row.keywords) : [],
      description: row.description || '',
      views: row.viewers || 0,
      genre: row.genre || '',
      siteUrl: row.url || '',
      isAdult: row.age === '성인' || row.age?.includes('19'),
      platform: row.platform || '',
      recommend: row.recommend || 0,
      serial: row.serial || '',
      publisher: row.publisher,
      pageCount: row.pageCount || 0,
      pageUnit: row.pageUnit || '화',
      age: row.age || '',
      viewers: row.viewers || 0,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt
    }

    return NextResponse.json(content)
  } catch (error) {
    console.error("API Error:", error)
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 })
  }
}

// PUT 요청으로 컨텐츠 업데이트
export async function PUT(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const id = Number.parseInt(params.id)
    const body = await request.json()
    const { type, data } = body

    if (!type || (type !== 'novel' && type !== 'webtoon')) {
      return NextResponse.json({ error: "Type parameter is required and must be 'novel' or 'webtoon'" }, { status: 400 })
    }

    const table = type === 'novel' ? 'novels' : 'webtoons'

    const query = `
      UPDATE ${table} SET
        img = ?,
        title = ?,
        author = ?,
        recommend = ?,
        genre = ?,
        serial = ?,
        publisher = ?,
        summary = ?,
        page_count = ?,
        page_unit = ?,
        age = ?,
        platform = ?,
        keywords = ?,
        viewers = ?,
        updated_at = CURRENT_TIMESTAMP
      WHERE id = ?
    `

    const keywordsJson = Array.isArray(data.keywords) ? JSON.stringify(data.keywords) : data.keywords

    await executeQuery(query, [
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
      data.viewers || 0,
      id
    ])

    return NextResponse.json({ success: true, message: `${type} updated successfully` })
  } catch (error) {
    console.error("PUT API Error:", error)
    return NextResponse.json({ error: "Failed to update content" }, { status: 500 })
  }
}

// DELETE 요청으로 컨텐츠 삭제
export async function DELETE(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const id = Number.parseInt(params.id)
    const searchParams = request.nextUrl.searchParams
    const type = searchParams.get("type")

    if (!type || (type !== 'novel' && type !== 'webtoon')) {
      return NextResponse.json({ error: "Type parameter is required and must be 'novel' or 'webtoon'" }, { status: 400 })
    }

    const table = type === 'novel' ? 'novels' : 'webtoons'
    const query = `DELETE FROM ${table} WHERE id = ?`

    await executeQuery(query, [id])

    return NextResponse.json({ success: true, message: `${type} deleted successfully` })
  } catch (error) {
    console.error("DELETE API Error:", error)
    return NextResponse.json({ error: "Failed to delete content" }, { status: 500 })
  }
}
