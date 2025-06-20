"use client"

import type React from "react"

import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { X, Plus } from "lucide-react"

interface TagSelectorProps {
  availableTags: string[]
  selectedTags: string[]
  onTagsChange: (tags: string[]) => void
  placeholder?: string
  label?: string
}

export default function TagSelector({
  availableTags,
  selectedTags,
  onTagsChange,
  placeholder = "태그 검색",
  label = "태그",
}: TagSelectorProps) {
  const [searchTerm, setSearchTerm] = useState("")
  const [customTag, setCustomTag] = useState("")

  const filteredTags = availableTags.filter(
    (tag) => tag.toLowerCase().includes(searchTerm.toLowerCase()) && !selectedTags.includes(tag),
  )

  const handleTagSelect = (tag: string) => {
    if (!selectedTags.includes(tag)) {
      onTagsChange([...selectedTags, tag])
    }
    setSearchTerm("")
  }

  const handleTagRemove = (tag: string) => {
    onTagsChange(selectedTags.filter((t) => t !== tag))
  }

  const handleCustomTagAdd = () => {
    if (customTag.trim() && !selectedTags.includes(customTag.trim())) {
      onTagsChange([...selectedTags, customTag.trim()])
      setCustomTag("")
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault()
      if (filteredTags.length > 0) {
        handleTagSelect(filteredTags[0])
      } else if (customTag.trim()) {
        handleCustomTagAdd()
      }
    }
  }

  return (
    <div className="space-y-3">
      <div className="relative">
        <Input
          placeholder={placeholder}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={handleKeyPress}
        />

        {searchTerm && filteredTags.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-background border rounded-md shadow-lg z-50 max-h-40 overflow-y-auto">
            {filteredTags.slice(0, 10).map((tag) => (
              <button
                key={tag}
                className="w-full px-3 py-2 text-left hover:bg-muted text-sm"
                onClick={() => handleTagSelect(tag)}
              >
                {tag}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="flex items-center gap-2">
        <Input
          placeholder="직접 입력"
          value={customTag}
          onChange={(e) => setCustomTag(e.target.value)}
          onKeyPress={handleKeyPress}
          className="flex-1"
        />
        <Button type="button" variant="outline" size="sm" onClick={handleCustomTagAdd} disabled={!customTag.trim()}>
          <Plus className="h-4 w-4" />
        </Button>
      </div>

      {selectedTags.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium">선택된 {label}:</p>
          <div className="flex flex-wrap gap-2">
            {selectedTags.map((tag) => (
              <Badge key={tag} variant="secondary" className="cursor-pointer">
                {tag}
                <X className="h-3 w-3 ml-1 hover:text-destructive" onClick={() => handleTagRemove(tag)} />
              </Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
