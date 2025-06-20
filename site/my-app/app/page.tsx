"use client"

import { useState, useMemo, useCallback, useEffect } from "react"
import Header from "@/components/header"
import FilterBar from "@/components/filter-bar"
import ContentGrid from "@/components/content-grid"
import SortDropdown, { type SortOption } from "@/components/sort-dropdown"
import { useAuth } from "@/lib/auth-context"
import { useInfiniteContents } from "@/hooks/use-infinite-contents"
import { Loader2 } from "lucide-react"

export type ContentType = "all" | "webtoon" | "novel"

export interface FilterState {
  type: ContentType
  title: string
  author: string
  tags: string
  genre: string
  minEpisodes: string
  maxEpisodes: string
  minRating: string
  maxRating: string
}

export default function Home() {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState<ContentType>("all")
  const [sortBy, setSortBy] = useState<SortOption>("popularity")
  const [filters, setFilters] = useState<FilterState>({
    type: "all",
    title: "",
    author: "",
    tags: "",
    genre: "",
    minEpisodes: "",
    maxEpisodes: "",
    minRating: "",
    maxRating: "",
  })

  const apiFilters = useMemo(
    () => ({
      type: activeTab,
      title: filters.title || undefined,
      author: filters.author || undefined,
      genre: filters.genre || undefined,
      tags: filters.tags ? filters.tags.split(",").filter(Boolean) : [],
      minEpisodes: filters.minEpisodes ? Number.parseInt(filters.minEpisodes) : undefined,
      maxEpisodes: filters.maxEpisodes ? Number.parseInt(filters.maxEpisodes) : undefined,
      minRating: filters.minRating ? Number.parseFloat(filters.minRating) : undefined,
      maxRating: filters.maxRating ? Number.parseFloat(filters.maxRating) : undefined,
      blockedGenres: user?.blockedGenres || [],
      blockedTags: user?.blockedTags || [],
      sortBy,
      showAdultContent: user?.isAdultVerified && user?.showAdultContent || false,
    }),
    [activeTab, filters, sortBy, user],
  )

  const { 
    contents, 
    loading, 
    error, 
    hasMore, 
    loadMore,
    totalCount 
  } = useInfiniteContents(apiFilters)

  // 스크롤 이벤트 감지
  useEffect(() => {
    const handleScroll = () => {
      // 페이지 하단에서 200px 위에 도달하면 다음 페이지 로드
      if (
        window.innerHeight + document.documentElement.scrollTop >=
        document.documentElement.offsetHeight - 200
      ) {
        if (hasMore && !loading) {
          loadMore()
        }
      }
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [hasMore, loading, loadMore])

  if (error) {
    return (
      <div className="min-h-screen bg-background">
        <Header activeTab={activeTab} onTabChange={setActiveTab} />
        <main className="container mx-auto px-4 py-6">
          <div className="text-center py-12">
            <p className="text-red-500">오류가 발생했습니다: {error}</p>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />

      <main className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">
            {activeTab === "all" ? "전체" : activeTab === "webtoon" ? "웹툰" : "소설"}
            <span className="text-muted-foreground ml-2">
              ({contents.length}{totalCount > contents.length ? `/${totalCount}` : ''}개)
            </span>
          </h2>

          <div className="flex items-center gap-4">
            <SortDropdown value={sortBy} onChange={setSortBy} />
            <FilterBar filters={filters} onFiltersChange={setFilters} />
          </div>
        </div>

        <ContentGrid content={contents} />

        {/* 로딩 인디케이터 */}
        {loading && (
          <div className="flex justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin" />
            <span className="ml-2 text-muted-foreground">더 많은 작품을 불러오는 중...</span>
          </div>
        )}

        {/* 더 이상 불러올 데이터가 없을 때 */}
        {!hasMore && contents.length > 0 && (
          <div className="text-center py-8">
            <p className="text-muted-foreground">모든 작품을 확인했습니다.</p>
          </div>
        )}

        {/* 검색 결과가 없을 때 */}
        {!loading && contents.length === 0 && (
          <div className="text-center py-12">
            <p className="text-muted-foreground">검색 결과가 없습니다.</p>
          </div>
        )}
      </main>
    </div>
  )
}
