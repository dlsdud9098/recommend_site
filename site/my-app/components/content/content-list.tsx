"\"use client"

import Image from "next/image"
import Link from "next/link"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Star } from "lucide-react"

// 더미 데이터
const NOVELS_DATA = [
  {
    id: 1,
    title: "마법사의 탑",
    author: "김작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.8,
    reviewCount: 1245,
    genres: ["판타지", "액션"],
    status: "연재중",
    summary: "100층의 탑을 오르는 마법사의 모험을 그린 판타지 소설",
    isNew: false,
  },
  {
    id: 3,
    title: "그림자 암살자",
    author: "박작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.7,
    reviewCount: 823,
    genres: ["스릴러", "액션"],
    status: "연재중",
    summary: "어둠 속에서 움직이는 암살자의 비밀 임무를 그린 스릴러 소설",
    isNew: false,
  },
  {
    id: 5,
    title: "판타지 세계",
    author: "정작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.9,
    reviewCount: 2103,
    genres: ["판타지", "모험"],
    status: "완결",
    summary: "다른 세계로 이동한 주인공의 모험을 그린 판타지 소설",
    isNew: true,
  },
  {
    id: 7,
    title: "스릴러 미스터리",
    author: "오작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.7,
    reviewCount: 956,
    genres: ["스릴러", "미스터리"],
    status: "연재중",
    summary: "연쇄 살인 사건을 파헤치는 형사의 이야기를 그린 미스터리 소설",
    isNew: true,
  },
  {
    id: 9,
    title: "신비한 마법서",
    author: "윤작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.3,
    reviewCount: 567,
    genres: ["판타지", "로맨스"],
    status: "연재중",
    summary: "우연히 발견한 마법서로 인해 변화하는 주인공의 일상을 그린 판타지 소설",
    isNew: true,
  },
  {
    id: 11,
    title: "비밀스러운 사랑",
    author: "임작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.2,
    reviewCount: 789,
    genres: ["로맨스", "드라마"],
    status: "완결",
    summary: "비밀을 간직한 두 사람의 애절한 사랑 이야기를 그린 로맨스 소설",
    isNew: false,
  },
  {
    id: 13,
    title: "공포의 집",
    author: "신작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.5,
    reviewCount: 678,
    genres: ["공포", "스릴러"],
    status: "연재중",
    summary: "저주받은 집에 얽힌 무서운 이야기를 그린 공포 소설",
    isNew: false,
  },
  {
    id: 15,
    title: "시간 여행자",
    author: "강작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.6,
    reviewCount: 1023,
    genres: ["SF", "모험"],
    status: "완결",
    summary: "시간을 넘나드는 여행자의 모험을 그린 SF 소설",
    isNew: false,
  },
]

const WEBTOONS_DATA = [
  {
    id: 2,
    title: "용사의 귀환",
    author: "이작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.5,
    reviewCount: 987,
    genres: ["판타지", "액션"],
    status: "연재중",
    summary: "15년 만에 현실 세계로 돌아온 용사의 이야기를 그린 판타지 웹툰",
    isNew: true,
  },
  {
    id: 4,
    title: "마법소녀",
    author: "최작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.6,
    reviewCount: 1432,
    genres: ["판타지", "액션"],
    status: "연재중",
    summary: "평범한 소녀가 마법 소녀로 각성하는 이야기를 그린 판타지 웹툰",
    isNew: false,
  },
  {
    id: 6,
    title: "로맨스 판타지",
    author: "한작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.4,
    reviewCount: 1122,
    genres: ["로맨스", "판타지"],
    status: "연재중",
    summary: "로맨스와 판타지가 결합된 흥미진진한 이야기를 그린 웹툰",
    isNew: false,
  },
  {
    id: 8,
    title: "SF 우주전쟁",
    author: "강작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.5,
    reviewCount: 1345,
    genres: ["SF", "액션"],
    status: "완결",
    summary: "미래 시대를 배경으로 펼쳐지는 우주 전쟁 이야기를 그린 웹툰",
    isNew: false,
  },
  {
    id: 10,
    title: "학원 판타지",
    author: "서작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.6,
    reviewCount: 1212,
    genres: ["판타지", "학원"],
    status: "연재중",
    summary: "마법 학교에서 벌어지는 학생들의 이야기를 그린 판타지 웹툰",
    isNew: true,
  },
  {
    id: 12,
    title: "살인사건",
    author: "조작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.8,
    reviewCount: 1567,
    genres: ["스릴러", "미스터리"],
    status: "연재중",
    summary: "미스터리한 살인사건을 중심으로 이야기가 전개되는 스릴러 웹툰",
    isNew: false,
  },
  {
    id: 14,
    title: "액션 히어로",
    author: "유작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.7,
    reviewCount: 1456,
    genres: ["액션", "히어로"],
    status: "완결",
    summary: "세상을 구하는 히어로의 이야기를 그린 액션 웹툰",
    isNew: false,
  },
  {
    id: 16,
    title: "일상 코미디",
    author: "고작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.5,
    reviewCount: 1123,
    genres: ["일상", "코미디"],
    status: "연재중",
    summary: "평범한 사람들의 웃긴 일상을 그린 코미디 웹툰",
    isNew: false,
  },
]

interface ContentListProps {
  contentType: "novel" | "webtoon"
}

export default function ContentList({ contentType }: ContentListProps) {
  const contentData = contentType === "novel" ? NOVELS_DATA : WEBTOONS_DATA

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      {contentData.map((item) => (
        <Card key={item.id}>
          <CardContent className="p-0">
            <Link href={`/${contentType}s/${item.id}`}>
              <div className="relative">
                <div className="aspect-[2/3] relative">
                  <Image
                    src={item.coverImage || "/placeholder.svg"}
                    alt={item.title}
                    fill
                    className="object-cover rounded-t-lg"
                  />
                </div>
                {item.isNew && <Badge className="absolute top-2 right-2">신작</Badge>}
              </div>
              <div className="p-4">
                <h3 className="font-medium line-clamp-1">{item.title}</h3>
                <p className="text-sm text-muted-foreground line-clamp-1">{item.author}</p>
                <div className="flex items-center mt-2">
                  <Star className="h-4 w-4 fill-yellow-400 text-yellow-400 mr-1" />
                  <span className="text-sm">{item.rating}</span>
                  <span className="text-sm text-muted-foreground ml-1">({item.reviewCount})</span>
                </div>
                <p className="text-sm text-muted-foreground mt-2 line-clamp-2">{item.summary}</p>
              </div>
            </Link>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
