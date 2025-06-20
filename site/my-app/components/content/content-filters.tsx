"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Filter } from "lucide-react"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"

// 장르 더미 데이터
const GENRES = [
  { id: "fantasy", label: "판타지" },
  { id: "romance", label: "로맨스" },
  { id: "thriller", label: "스릴러" },
  { id: "action", label: "액션" },
  { id: "comedy", label: "코미디" },
  { id: "drama", label: "드라마" },
  { id: "sf", label: "SF" },
  { id: "horror", label: "공포" },
  { id: "mystery", label: "미스터리" },
  { id: "historical", label: "역사" },
]

// 연재 상태 더미 데이터
const STATUS = [
  { id: "ongoing", label: "연재중" },
  { id: "completed", label: "완결" },
  { id: "hiatus", label: "휴재" },
]

interface ContentFiltersProps {
  contentType: "novel" | "webtoon"
}

export default function ContentFilters({ contentType }: ContentFiltersProps) {
  const [selectedGenres, setSelectedGenres] = useState<string[]>([])
  const [selectedStatus, setSelectedStatus] = useState<string[]>([])
  const [sortBy, setSortBy] = useState("popular")

  const handleGenreChange = (genreId: string, checked: boolean) => {
    if (checked) {
      setSelectedGenres([...selectedGenres, genreId])
    } else {
      setSelectedGenres(selectedGenres.filter((id) => id !== genreId))
    }
  }

  const handleStatusChange = (statusId: string, checked: boolean) => {
    if (checked) {
      setSelectedStatus([...selectedStatus, statusId])
    } else {
      setSelectedStatus(selectedStatus.filter((id) => id !== statusId))
    }
  }

  const resetFilters = () => {
    setSelectedGenres([])
    setSelectedStatus([])
    setSortBy("popular")
  }

  const FiltersContent = () => (
    <>
      <div className="space-y-6">
        <Accordion type="single" collapsible defaultValue="genres" className="w-full">
          <AccordionItem value="genres">
            <AccordionTrigger className="text-base font-medium">장르</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-2">
                {GENRES.map((genre) => (
                  <div key={genre.id} className="flex items-center space-x-2">
                    <Checkbox
                      id={`genre-${genre.id}`}
                      checked={selectedGenres.includes(genre.id)}
                      onCheckedChange={(checked) => handleGenreChange(genre.id, checked === true)}
                    />
                    <Label htmlFor={`genre-${genre.id}`}>{genre.label}</Label>
                  </div>
                ))}
              </div>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="status">
            <AccordionTrigger className="text-base font-medium">연재 상태</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-2">
                {STATUS.map((status) => (
                  <div key={status.id} className="flex items-center space-x-2">
                    <Checkbox
                      id={`status-${status.id}`}
                      checked={selectedStatus.includes(status.id)}
                      onCheckedChange={(checked) => handleStatusChange(status.id, checked === true)}
                    />
                    <Label htmlFor={`status-${status.id}`}>{status.label}</Label>
                  </div>
                ))}
              </div>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="sort">
            <AccordionTrigger className="text-base font-medium">정렬</AccordionTrigger>
            <AccordionContent>
              <RadioGroup value={sortBy} onValueChange={setSortBy}>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="popular" id="popular" />
                  <Label htmlFor="popular">인기순</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="latest" id="latest" />
                  <Label htmlFor="latest">최신순</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="rating" id="rating" />
                  <Label htmlFor="rating">평점순</Label>
                </div>
              </RadioGroup>
            </AccordionContent>
          </AccordionItem>
        </Accordion>

        <Button onClick={resetFilters} variant="outline" className="w-full">
          필터 초기화
        </Button>

        <Button className="w-full">적용하기</Button>
      </div>
    </>
  )

  return (
    <>
      {/* 모바일 필터 */}
      <div className="md:hidden w-full mb-4">
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="outline" className="w-full">
              <Filter className="mr-2 h-4 w-4" />
              필터
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-[300px] sm:w-[400px]">
            <SheetHeader>
              <SheetTitle>필터</SheetTitle>
            </SheetHeader>
            <div className="py-4">
              <FiltersContent />
            </div>
          </SheetContent>
        </Sheet>
      </div>

      {/* 데스크톱 필터 */}
      <div className="hidden md:block sticky top-20">
        <div className="bg-card rounded-lg border p-4">
          <h2 className="text-lg font-semibold mb-4">필터</h2>
          <FiltersContent />
        </div>
      </div>
    </>
  )
}
