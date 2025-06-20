"use client"

import { useState, useEffect, useMemo } from "react"
import Header from "@/components/header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Sparkles, RefreshCw } from "lucide-react"
import ContentGrid from "@/components/content-grid"
import { CONTENT_DATA } from "@/lib/data"
import ProtectedRoute from "@/components/protected-route"
import { useAuth } from "@/lib/auth-context"
import { Button } from "@/components/ui/button"

export default function AIRecommendPage() {
  const { user } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [recommendations, setRecommendations] = useState<typeof CONTENT_DATA>([])

  // 사용자의 선호작 기반 추천 로직
  const generateRecommendations = useMemo(() => {
    if (!user || !user.favoriteWorks || user.favoriteWorks.length === 0) {
      // 선호작이 없으면 인기작 기준으로 추천
      return CONTENT_DATA.slice(0, 8)
    }

    // 선호작들의 장르와 태그 분석
    const favoriteItems = CONTENT_DATA.filter((item) => user.favoriteWorks.includes(item.id.toString()))

    const genreCount: Record<string, number> = {}
    const tagCount: Record<string, number> = {}

    favoriteItems.forEach((item) => {
      genreCount[item.genre] = (genreCount[item.genre] || 0) + 1
      item.tags.forEach((tag) => {
        tagCount[tag] = (tagCount[tag] || 0) + 1
      })
    })

    // 선호하는 장르와 태그 추출
    const preferredGenres = Object.keys(genreCount).sort((a, b) => genreCount[b] - genreCount[a])
    const preferredTags = Object.keys(tagCount).sort((a, b) => tagCount[b] - tagCount[a])

    // 추천 점수 계산
    const scoredItems = CONTENT_DATA.filter((item) => !user.favoriteWorks.includes(item.id.toString())) // 이미 찜한 작품 제외
      .filter((item) => !user.blockedGenres?.includes(item.genre)) // 차단된 장르 제외
      .filter((item) => !item.tags.some((tag) => user.blockedTags?.includes(tag))) // 차단된 태그 제외
      .map((item) => {
        let score = 0

        // 장르 점수
        const genreIndex = preferredGenres.indexOf(item.genre)
        if (genreIndex !== -1) {
          score += (preferredGenres.length - genreIndex) * 10
        }

        // 태그 점수
        item.tags.forEach((tag) => {
          const tagIndex = preferredTags.indexOf(tag)
          if (tagIndex !== -1) {
            score += (preferredTags.length - tagIndex) * 5
          }
        })

        // 평점 점수
        score += item.rating * 2

        return { ...item, score }
      })
      .sort((a, b) => b.score - a.score)
      .slice(0, 12)

    return scoredItems
  }, [user])

  useEffect(() => {
    setRecommendations(generateRecommendations)
  }, [generateRecommendations])

  const handleRefreshRecommendations = async () => {
    setIsLoading(true)
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // 추천 목록을 다시 섞어서 새로운 추천 제공
    const shuffled = [...generateRecommendations].sort(() => 0.5 - Math.random())
    setRecommendations(shuffled.slice(0, 8))
    setIsLoading(false)
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background">
        <Header activeTab="all" onTabChange={() => {}} />

        <main className="container mx-auto px-4 py-6">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold mb-2 flex items-center justify-center gap-2">
                <Sparkles className="h-8 w-8 text-primary" />
                AI 맞춤 추천
              </h1>
              <p className="text-muted-foreground">
                {!user || !user.favoriteWorks || user.favoriteWorks.length === 0
                  ? "선호작을 등록하시면 더 정확한 추천을 받을 수 있습니다"
                  : "찜한 작품을 기반으로 맞춤 추천을 제공합니다"}
              </p>
            </div>

            {!user || !user.favoriteWorks || user.favoriteWorks.length === 0 ? (
              <Card className="mb-8">
                <CardHeader>
                  <CardTitle>추천을 위한 안내</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-4">
                    아직 찜한 작품이 없습니다. 관심 있는 작품에 하트를 눌러 선호작으로 등록하시면, AI가 더 정확한 맞춤
                    추천을 제공할 수 있습니다.
                  </p>
                  <p className="text-sm text-muted-foreground">현재는 인기 작품을 기준으로 추천해드리고 있습니다.</p>
                </CardContent>
              </Card>
            ) : (
              <Card className="mb-8">
                <CardHeader>
                  <CardTitle>추천 기준</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-2">
                    찜한 작품 {user.favoriteWorks.length}개를 분석하여 맞춤 추천을 제공합니다.
                  </p>
                  <div className="flex justify-end">
                    <Button variant="outline" onClick={handleRefreshRecommendations} disabled={isLoading}>
                      {isLoading ? (
                        <>
                          <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                          새로고침 중...
                        </>
                      ) : (
                        <>
                          <RefreshCw className="h-4 w-4 mr-2" />
                          추천 새로고침
                        </>
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            <div>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-semibold">추천 작품</h2>
                <Badge variant="secondary" className="text-sm">
                  {recommendations.length}개 추천
                </Badge>
              </div>

              <ContentGrid content={recommendations} />
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
