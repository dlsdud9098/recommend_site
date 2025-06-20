"use client"

import { useState, useRef } from "react"
import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ChevronLeft, ChevronRight, Star } from "lucide-react"

// 더미 데이터
const POPULAR_CONTENT = [
  {
    id: 1,
    title: "마법사의 탑",
    author: "김작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.8,
    type: "novel",
    isNew: false,
  },
  {
    id: 2,
    title: "용사의 귀환",
    author: "이작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.5,
    type: "webtoon",
    isNew: true,
  },
  {
    id: 3,
    title: "그림자 암살자",
    author: "박작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.7,
    type: "novel",
    isNew: false,
  },
  {
    id: 4,
    title: "마법소녀",
    author: "최작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.6,
    type: "webtoon",
    isNew: false,
  },
  {
    id: 5,
    title: "판타지 세계",
    author: "정작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.9,
    type: "novel",
    isNew: true,
  },
  {
    id: 6,
    title: "로맨스 판타지",
    author: "한작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.4,
    type: "webtoon",
    isNew: false,
  },
  {
    id: 7,
    title: "스릴러 미스터리",
    author: "오작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.7,
    type: "novel",
    isNew: true,
  },
  {
    id: 8,
    title: "SF 우주전쟁",
    author: "강작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.5,
    type: "webtoon",
    isNew: false,
  },
]

const LATEST_CONTENT = [
  {
    id: 9,
    title: "신비한 마법서",
    author: "윤작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.3,
    type: "novel",
    isNew: true,
  },
  {
    id: 10,
    title: "학원 판타지",
    author: "서작가",
    coverImage: "/placeholder.svg?height=300&width=200",
    rating: 4.6,
    type: "webtoon",
    isNew: true,
  },
  // ... 나머지 최신 콘텐츠
].concat(POPULAR_CONTENT.slice(0, 6))

interface ContentCarouselProps {
  type: "popular" | "latest"
}

export default function ContentCarousel({ type }: ContentCarouselProps) {
  const carouselRef = useRef<HTMLDivElement>(null)
  const [showLeftButton, setShowLeftButton] = useState(false)
  const [showRightButton, setShowRightButton] = useState(true)

  const content = type === "popular" ? POPULAR_CONTENT : LATEST_CONTENT

  const scroll = (direction: "left" | "right") => {
    if (carouselRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = carouselRef.current
      const scrollAmount = clientWidth * 0.8

      const newScrollLeft = direction === "left" ? scrollLeft - scrollAmount : scrollLeft + scrollAmount

      carouselRef.current.scrollTo({
        left: newScrollLeft,
        behavior: "smooth",
      })

      // 버튼 표시 여부 업데이트
      setTimeout(() => {
        if (carouselRef.current) {
          setShowLeftButton(carouselRef.current.scrollLeft > 0)
          setShowRightButton(
            carouselRef.current.scrollLeft + carouselRef.current.clientWidth < carouselRef.current.scrollWidth - 10,
          )
        }
      }, 300)
    }
  }

  return (
    <div className="relative">
      <div
        ref={carouselRef}
        className="flex overflow-x-auto scrollbar-hide gap-4 pb-4"
        style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
        onScroll={() => {
          if (carouselRef.current) {
            setShowLeftButton(carouselRef.current.scrollLeft > 0)
            setShowRightButton(
              carouselRef.current.scrollLeft + carouselRef.current.clientWidth < carouselRef.current.scrollWidth - 10,
            )
          }
        }}
      >
        {content.map((item) => (
          <Card key={item.id} className="min-w-[160px] sm:min-w-[200px] flex-shrink-0">
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
                  {item.isNew && <Badge className="absolute top-2 right-2">신작</Badge>}
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

      {showLeftButton && (
        <Button
          variant="secondary"
          size="icon"
          className="absolute left-0 top-1/2 -translate-y-1/2 rounded-full shadow-lg"
          onClick={() => scroll("left")}
        >
          <ChevronLeft className="h-5 w-5" />
          <span className="sr-only">이전</span>
        </Button>
      )}

      {showRightButton && (
        <Button
          variant="secondary"
          size="icon"
          className="absolute right-0 top-1/2 -translate-y-1/2 rounded-full shadow-lg"
          onClick={() => scroll("right")}
        >
          <ChevronRight className="h-5 w-5" />
          <span className="sr-only">다음</span>
        </Button>
      )}
    </div>
  )
}
