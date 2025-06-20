"use client"

import { useState } from "react"
import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Star } from "lucide-react"

// 더미 데이터
const PERSONALIZED_DATA = {
  recommended: [
    {
      id: 1,
      title: "마법사의 탑",
      author: "김작가",
      coverImage: "/placeholder.svg?height=300&width=200",
      rating: 4.8,
      type: "novel",
      reason: "판타지 장르 선호",
    },
    {
      id: 2,
      title: "용사의 귀환",
      author: "이작가",
      coverImage: "/placeholder.svg?height=300&width=200",
      rating: 4.5,
      type: "webtoon",
      reason: "액션 장르 선호",
    },
    {
      id: 3,
      title: "그림자 암살자",
      author: "박작가",
      coverImage: "/placeholder.svg?height=300&width=200",
      rating: 4.7,
      type: "novel",
      reason: "스릴러 장르 선호",
    },
    {
      id: 4,
      title: "마법소녀",
      author: "최작가",
      coverImage: "/placeholder.svg?height=300&width=200",
      rating: 4.6,
      type: "webtoon",
      reason: "판타지 장르 선호",
    },
  ],
  continue: [
    {
      id: 5,
      title: "판타지 세계",
      author: "정작가",
      coverImage: "/placeholder.svg?height=300&width=200",
      rating: 4.9,
      type: "novel",
      progress: 45,
      lastRead: "2일 전",
    },
    {
      id: 6,
      title: "로맨스 판타지",
      author: "한작가",
      coverImage: "/placeholder.svg?height=300&width=200",
      rating: 4.4,
      type: "webtoon",
      progress: 23,
      lastRead: "1주일 전",
    },
    {
      id: 7,
      title: "스릴러 미스터리",
      author: "오작가",
      coverImage: "/placeholder.svg?height=300&width=200",
      rating: 4.7,
      type: "novel",
      progress: 78,
      lastRead: "오늘",
    },
    {
      id: 8,
      title: "SF 우주전쟁",
      author: "강작가",
      coverImage: "/placeholder.svg?height=300&width=200",
      rating: 4.5,
      type: "webtoon",
      progress: 12,
      lastRead: "3일 전",
    },
  ],
}

export default function PersonalizedSection() {
  const [isLoggedIn, setIsLoggedIn] = useState(true) // 실제로는 인증 상태에 따라 설정

  if (!isLoggedIn) {
    return (
      <section className="my-12 p-6 bg-muted rounded-xl">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2">맞춤 추천을 받아보세요</h2>
          <p className="text-muted-foreground mb-4">로그인하시면 취향에 맞는 작품을 추천해드립니다.</p>
          <div className="flex justify-center gap-4">
            <Button asChild>
              <Link href="/login">로그인</Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/signup">회원가입</Link>
            </Button>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section className="my-12">
      <h2 className="text-2xl font-bold mb-6">사용자님을 위한 추천</h2>

      <Tabs defaultValue="recommended" className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="recommended">맞춤 추천</TabsTrigger>
          <TabsTrigger value="continue">이어보기</TabsTrigger>
        </TabsList>

        <TabsContent value="recommended" className="mt-0">
          <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {PERSONALIZED_DATA.recommended.map((item) => (
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
                      <p className="text-xs text-muted-foreground mt-2 bg-muted inline-block px-2 py-1 rounded-full">
                        {item.reason}
                      </p>
                    </div>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="continue" className="mt-0">
          <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {PERSONALIZED_DATA.continue.map((item) => (
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
                        <div className="absolute bottom-0 left-0 right-0 h-1 bg-muted">
                          <div className="h-full bg-primary" style={{ width: `${item.progress}%` }} />
                        </div>
                      </div>
                    </div>
                    <div className="p-3">
                      <h3 className="font-medium line-clamp-1">{item.title}</h3>
                      <p className="text-sm text-muted-foreground">{item.author}</p>
                      <div className="flex items-center justify-between mt-1">
                        <div className="flex items-center">
                          <Star className="h-3 w-3 fill-yellow-400 text-yellow-400 mr-1" />
                          <span className="text-sm">{item.rating}</span>
                        </div>
                        <span className="text-xs text-muted-foreground">{item.lastRead} 읽음</span>
                      </div>
                      <p className="text-xs mt-2">{item.progress}% 완료</p>
                    </div>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </section>
  )
}
