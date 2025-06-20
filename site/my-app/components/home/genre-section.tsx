import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Star } from "lucide-react"

// 장르별 더미 데이터
const GENRE_DATA = {
  fantasy: [
    {
      id: 1,
      title: "마법사의 탑",
      author: "김작가",
      coverImage: "/placeholder.svg?height=300&width=200",
      rating: 4.8,
      type: "novel",
    },
    {
      id: 2,
      title: "용사의 귀환",
      author: "이작가",
      coverImage: "/placeholder.svg?height=300&width=200",
      rating: 4.5,
      type: "webtoon",
    },
    {
      id: 5,
      title: "판타지 세계",
      author: "정작가",
      coverImage: "/placeholder.svg?height=300&width=200",
      rating: 4.9,
      type: "novel",
    },
    {
      id: 4,
      title: "마법소녀",
      author: "최작가",
      coverImage: "/placeholder.svg?height=300&width=200",
      rating: 4.6,
      type: "webtoon",
    },
  ],
  romance: [
    {
      id: 6,
      title: "로맨스 판타지",
      author: "한작가",
      coverImage: "/placeholder.svg?height=300&width=200",
      rating: 4.4,
      type: "webtoon",
    },
    {
      id: 9,
      title: "첫사랑의 기억",
      author: "윤작가",
      coverImage: "/placeholder.svg?height=300&width=200",
      rating: 4.3,
      type: "novel",
    },
    {
      id: 10,
      title: "캠퍼스 로맨스",
      author: "서작가",
      coverImage: "/placeholder.svg?height=300&width=200",
      rating: 4.6,
      type: "webtoon",
    },
    {
      id: 11,
      title: "비밀스러운 사랑",
      author: "임작가",
      coverImage: "/placeholder.svg?height=300&width=200",
      rating: 4.2,
      type: "novel",
    },
  ],
  thriller: [
    {
      id: 3,
      title: "그림자 암살자",
      author: "박작가",
      coverImage: "/placeholder.svg?height=300&width=200",
      rating: 4.7,
      type: "novel",
    },
    {
      id: 7,
      title: "스릴러 미스터리",
      author: "오작가",
      coverImage: "/placeholder.svg?height=300&width=200",
      rating: 4.7,
      type: "novel",
    },
    {
      id: 12,
      title: "살인사건",
      author: "조작가",
      coverImage: "/placeholder.svg?height=300&width=200",
      rating: 4.8,
      type: "webtoon",
    },
    {
      id: 13,
      title: "공포의 집",
      author: "신작가",
      coverImage: "/placeholder.svg?height=300&width=200",
      rating: 4.5,
      type: "novel",
    },
  ],
}

interface GenreSectionProps {
  title: string
  genre: keyof typeof GENRE_DATA
}

export default function GenreSection({ title, genre }: GenreSectionProps) {
  const content = GENRE_DATA[genre]

  return (
    <section className="my-12">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">{title}</h2>
        <Button variant="outline" asChild>
          <Link href={`/genre/${genre}`}>더보기</Link>
        </Button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {content.map((item) => (
          <Card key={item.id}>
            <CardContent className="p-0">
              <Link href={`/${item.type}s/${item.id}`}>
                <div className="relative">
                  <div className="aspect-[2/3] relative">
                    <Image
                      src={item.coverImage || "/placeholder.svg"}
                      alt={item.title}
                      fill
                      className="object-cover rounded-t-lg"
                    />
                  </div>
                </div>
                <div className="p-3">
                  <h3 className="font-medium line-clamp-1">{item.title}</h3>
                  <p className="text-sm text-muted-foreground">{item.author}</p>
                  <div className="flex items-center mt-1">
                    <Star className="h-3 w-3 fill-yellow-400 text-yellow-400 mr-1" />
                    <span className="text-sm">{item.rating}</span>
                  </div>
                </div>
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  )
}
