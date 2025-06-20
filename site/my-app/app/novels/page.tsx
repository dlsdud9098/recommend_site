"use client"

import { useState, useMemo } from "react"
import Header from "@/components/header"
import FilterBar from "@/components/filter-bar"
import ContentGrid from "@/components/content-grid"
import { CONTENT_DATA } from "@/lib/data"
import type { FilterState } from "@/app/page"

export default function NovelsPage() {
  const [filters, setFilters] = useState<FilterState>({
    type: "novel",
    title: "",
    author: "",
    tags: "",
    minEpisodes: "",
    maxEpisodes: "",
    minRating: "",
    maxRating: "",
  })

  const filteredContent = useMemo(() => {
    let filtered = CONTENT_DATA.filter((item) => item.type === "novel")

    // 제목 필터링
    if (filters.title) {
      filtered = filtered.filter((item) => item.title.toLowerCase().includes(filters.title.toLowerCase()))
    }

    // 작가 필터링
    if (filters.author) {
      filtered = filtered.filter((item) => item.author.toLowerCase().includes(filters.author.toLowerCase()))
    }

    // 태그 필터링
    if (filters.tags) {
      filtered = filtered.filter((item) =>
        item.tags.some((tag) => tag.toLowerCase().includes(filters.tags.toLowerCase())),
      )
    }

    // 연재 수 필터링
    if (filters.minEpisodes) {
      const min = Number.parseInt(filters.minEpisodes)
      if (!isNaN(min)) {
        filtered = filtered.filter((item) => item.episodes >= min)
      }
    }

    if (filters.maxEpisodes) {
      const max = Number.parseInt(filters.maxEpisodes)
      if (!isNaN(max)) {
        filtered = filtered.filter((item) => item.episodes <= max)
      }
    }

    // 평점 필터링
    if (filters.minRating) {
      const min = Number.parseFloat(filters.minRating)
      if (!isNaN(min)) {
        filtered = filtered.filter((item) => item.rating >= min)
      }
    }

    if (filters.maxRating) {
      const max = Number.parseFloat(filters.maxRating)
      if (!isNaN(max)) {
        filtered = filtered.filter((item) => item.rating <= max)
      }
    }

    return filtered
  }, [filters])

  return (
    <div className="min-h-screen bg-background">
      <Header activeTab="novel" onTabChange={() => {}} />

      <main className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">
            소설
            <span className="text-muted-foreground ml-2">({filteredContent.length}개)</span>
          </h2>

          <FilterBar filters={filters} onFiltersChange={setFilters} />
        </div>

        <ContentGrid content={filteredContent} />
      </main>
    </div>
  )
}
