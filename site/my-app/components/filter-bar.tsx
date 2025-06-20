"use client"

import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Filter, X } from "lucide-react"
import type { FilterState } from "@/app/page"
import TagSelector from "./tag-selector"

const AVAILABLE_GENRES = ["판타지", "로맨스", "액션", "코미디", "스릴러", "호러", "SF", "미스터리"]
const AVAILABLE_TAGS = [
  "마법",
  "모험",
  "학원",
  "용사",
  "암살자",
  "마법소녀",
  "카페",
  "좀비",
  "생존",
  "시간여행",
  "히어로",
  "추리",
  "요리",
  "일상",
  "치유",
  "성장",
  "복수",
  "전쟁",
  "우정",
  "가족",
]

interface FilterBarProps {
  filters: FilterState
  onFiltersChange: (filters: FilterState) => void
}

export default function FilterBar({ filters, onFiltersChange }: FilterBarProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedTags, setSelectedTags] = useState<string[]>(
    filters.tags ? filters.tags.split(",").filter(Boolean) : [],
  )

  const updateFilter = (key: keyof FilterState, value: string) => {
    onFiltersChange({
      ...filters,
      [key]: value,
    })
  }

  const handleTagsChange = (tags: string[]) => {
    setSelectedTags(tags)
    updateFilter("tags", tags.join(","))
  }

  const clearFilters = () => {
    setSelectedTags([])
    onFiltersChange({
      type: filters.type,
      title: "",
      author: "",
      tags: "",
      genre: "",
      minEpisodes: "",
      maxEpisodes: "",
      minRating: "",
      maxRating: "",
    })
  }

  const applyFilters = () => {
    setIsOpen(false)
  }

  const hasActiveFilters = Object.entries(filters).some(([key, value]) => key !== "type" && value !== "")

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetTrigger asChild>
        <Button variant="outline" className="relative">
          <Filter className="h-4 w-4 mr-2" />
          필터
          {hasActiveFilters && <div className="absolute -top-1 -right-1 h-2 w-2 bg-primary rounded-full" />}
        </Button>
      </SheetTrigger>

      <SheetContent side="right" className="w-[400px] sm:w-[500px]">
        <SheetHeader>
          <SheetTitle>필터 설정</SheetTitle>
        </SheetHeader>

        <div className="py-6 space-y-6">
          <div className="space-y-2">
            <Label htmlFor="title">제목</Label>
            <Input
              id="title"
              placeholder="제목 검색"
              value={filters.title}
              onChange={(e) => updateFilter("title", e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="author">작가</Label>
            <Input
              id="author"
              placeholder="작가 검색"
              value={filters.author}
              onChange={(e) => updateFilter("author", e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="genre">장르</Label>
            <Select value={filters.genre} onValueChange={(value) => updateFilter("genre", value)}>
              <SelectTrigger>
                <SelectValue placeholder="장르 선택" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체</SelectItem>
                {AVAILABLE_GENRES.map((genre) => (
                  <SelectItem key={genre} value={genre}>
                    {genre}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>태그</Label>
            <TagSelector
              availableTags={AVAILABLE_TAGS}
              selectedTags={selectedTags}
              onTagsChange={handleTagsChange}
              placeholder="태그 검색 또는 입력"
            />
          </div>

          <div className="space-y-2">
            <Label>연재 수</Label>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <Label htmlFor="minEpisodes" className="text-sm text-muted-foreground">
                  최소
                </Label>
                <Input
                  id="minEpisodes"
                  placeholder="0"
                  type="number"
                  min="0"
                  value={filters.minEpisodes}
                  onChange={(e) => updateFilter("minEpisodes", e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="maxEpisodes" className="text-sm text-muted-foreground">
                  최대
                </Label>
                <Input
                  id="maxEpisodes"
                  placeholder="999"
                  type="number"
                  min="0"
                  value={filters.maxEpisodes}
                  onChange={(e) => updateFilter("maxEpisodes", e.target.value)}
                />
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <Label>평점</Label>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <Label htmlFor="minRating" className="text-sm text-muted-foreground">
                  최소
                </Label>
                <Input
                  id="minRating"
                  placeholder="0.0"
                  type="number"
                  step="0.1"
                  min="0"
                  max="5"
                  value={filters.minRating}
                  onChange={(e) => updateFilter("minRating", e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="maxRating" className="text-sm text-muted-foreground">
                  최대
                </Label>
                <Input
                  id="maxRating"
                  placeholder="5.0"
                  type="number"
                  step="0.1"
                  min="0"
                  max="5"
                  value={filters.maxRating}
                  onChange={(e) => updateFilter("maxRating", e.target.value)}
                />
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-3 pt-4">
            <Button onClick={applyFilters} className="w-full">
              필터 적용
            </Button>

            {hasActiveFilters && (
              <Button variant="outline" onClick={clearFilters} className="w-full">
                <X className="h-4 w-4 mr-2" />
                필터 초기화
              </Button>
            )}
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
