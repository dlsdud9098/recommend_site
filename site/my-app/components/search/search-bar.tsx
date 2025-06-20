"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { useRouter } from "next/navigation"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { X, Search } from "lucide-react"

// 자동완성을 위한 더미 데이터
const DUMMY_SUGGESTIONS = [
  { id: 1, title: "마법사의 탑", type: "novel" },
  { id: 2, title: "마법소녀", type: "webtoon" },
  { id: 3, title: "마법의 세계", type: "novel" },
  { id: 4, title: "마법학교", type: "webtoon" },
]

interface SearchBarProps {
  onClose?: () => void
}

export default function SearchBar({ onClose }: SearchBarProps) {
  const [query, setQuery] = useState("")
  const [suggestions, setSuggestions] = useState<typeof DUMMY_SUGGESTIONS>([])
  const [isOpen, setIsOpen] = useState(false)
  const router = useRouter()
  const inputRef = useRef<HTMLInputElement>(null)
  const wrapperRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // 자동완성 로직 (실제로는 API 호출)
    if (query.length > 1) {
      const filtered = DUMMY_SUGGESTIONS.filter((item) => item.title.toLowerCase().includes(query.toLowerCase()))
      setSuggestions(filtered)
      setIsOpen(true)
    } else {
      setSuggestions([])
      setIsOpen(false)
    }
  }, [query])

  useEffect(() => {
    // 컴포넌트 마운트 시 input에 포커스
    inputRef.current?.focus()

    // 외부 클릭 시 자동완성 닫기
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query)}`)
      if (onClose) onClose()
    }
  }

  const handleSuggestionClick = (suggestion: (typeof DUMMY_SUGGESTIONS)[0]) => {
    router.push(`/${suggestion.type}s/${suggestion.id}`)
    setIsOpen(false)
    if (onClose) onClose()
  }

  return (
    <div ref={wrapperRef} className="relative w-full">
      <form onSubmit={handleSearch} className="flex w-full">
        <div className="relative flex-1">
          <Input
            ref={inputRef}
            type="search"
            placeholder="작품명, 작가명으로 검색"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="pr-10"
          />
          {query && (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="absolute right-0 top-0 h-full"
              onClick={() => setQuery("")}
            >
              <X className="h-4 w-4" />
              <span className="sr-only">지우기</span>
            </Button>
          )}
        </div>
        <Button type="submit" className="ml-2">
          <Search className="h-4 w-4 mr-2" />
          검색
        </Button>
        {onClose && (
          <Button type="button" variant="ghost" size="icon" className="ml-2" onClick={onClose}>
            <X className="h-5 w-5" />
            <span className="sr-only">닫기</span>
          </Button>
        )}
      </form>

      {isOpen && suggestions.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-background border rounded-md shadow-lg z-50">
          <ul>
            {suggestions.map((suggestion) => (
              <li
                key={suggestion.id}
                className="px-4 py-2 hover:bg-muted cursor-pointer flex items-center"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                <span className="flex-1">{suggestion.title}</span>
                <span className="text-xs text-muted-foreground">{suggestion.type === "novel" ? "소설" : "웹툰"}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
