"use client"

import { useState, useEffect } from "react"
import Image from "next/image"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight } from "lucide-react"

// 배너 더미 데이터
const BANNER_DATA = [
  {
    id: 1,
    title: "마법사의 탑",
    description: "100층의 탑을 오르는 마법사의 모험",
    image: "/placeholder.svg?height=600&width=1200",
    type: "novel",
    badge: "신작",
  },
  {
    id: 2,
    title: "용사의 귀환",
    description: "15년 만에 현실 세계로 돌아온 용사의 이야기",
    image: "/placeholder.svg?height=600&width=1200",
    type: "webtoon",
    badge: "인기",
  },
  {
    id: 3,
    title: "그림자 암살자",
    description: "어둠 속에서 움직이는 암살자의 비밀 임무",
    image: "/placeholder.svg?height=600&width=1200",
    type: "novel",
    badge: "독점",
  },
]

export default function HeroBanner() {
  const [currentSlide, setCurrentSlide] = useState(0)

  // 자동 슬라이드
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % BANNER_DATA.length)
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % BANNER_DATA.length)
  }

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + BANNER_DATA.length) % BANNER_DATA.length)
  }

  return (
    <div className="relative w-full h-[300px] sm:h-[400px] md:h-[500px] overflow-hidden rounded-xl">
      {BANNER_DATA.map((banner, index) => (
        <div
          key={banner.id}
          className={`absolute inset-0 transition-opacity duration-500 ${
            index === currentSlide ? "opacity-100" : "opacity-0 pointer-events-none"
          }`}
        >
          <div className="relative w-full h-full">
            <Image
              src={banner.image || "/placeholder.svg"}
              alt={banner.title}
              fill
              className="object-cover"
              priority={index === 0}
            />
            <div className="absolute inset-0 bg-gradient-to-r from-black/70 to-transparent flex flex-col justify-center px-6 md:px-12">
              <div className="max-w-md text-white">
                <div className="inline-block px-2 py-1 mb-2 text-xs font-medium bg-primary text-primary-foreground rounded">
                  {banner.badge}
                </div>
                <h2 className="text-2xl md:text-4xl font-bold mb-2">{banner.title}</h2>
                <p className="mb-4 text-sm md:text-base opacity-90">{banner.description}</p>
                <div className="flex space-x-3">
                  <Button asChild>
                    <Link href={`/${banner.type}s/${banner.id}`}>자세히 보기</Link>
                  </Button>
                  <Button variant="outline" className="bg-white/10 hover:bg-white/20">
                    <Link href={`/library/add/${banner.id}?type=${banner.type}`}>내 서재에 추가</Link>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      ))}

      {/* 네비게이션 버튼 */}
      <Button
        variant="ghost"
        size="icon"
        className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/30 hover:bg-black/50 text-white rounded-full"
        onClick={prevSlide}
      >
        <ChevronLeft className="h-6 w-6" />
        <span className="sr-only">이전</span>
      </Button>

      <Button
        variant="ghost"
        size="icon"
        className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/30 hover:bg-black/50 text-white rounded-full"
        onClick={nextSlide}
      >
        <ChevronRight className="h-6 w-6" />
        <span className="sr-only">다음</span>
      </Button>

      {/* 인디케이터 */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex space-x-2">
        {BANNER_DATA.map((_, index) => (
          <button
            key={index}
            className={`w-2 h-2 rounded-full ${index === currentSlide ? "bg-white" : "bg-white/50"}`}
            onClick={() => setCurrentSlide(index)}
          />
        ))}
      </div>
    </div>
  )
}
