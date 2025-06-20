"use client"

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export type SortOption = "popularity" | "rating" | "views" | "favorites"

interface SortDropdownProps {
  value: SortOption
  onChange: (value: SortOption) => void
}

export default function SortDropdown({ value, onChange }: SortDropdownProps) {
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className="w-[140px]">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="popularity">인기순</SelectItem>
        <SelectItem value="rating">평점순</SelectItem>
        <SelectItem value="views">조회수순</SelectItem>
        <SelectItem value="favorites">선호순</SelectItem>
      </SelectContent>
    </Select>
  )
}
