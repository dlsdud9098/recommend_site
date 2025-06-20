"use client"

import { useState, useEffect, useCallback } from "react"
import type { ContentItem, FilterOptions } from "@/lib/database"

export function useContents(filters: FilterOptions = {}) {
  const [contents, setContents] = useState<ContentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchContents = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const searchParams = new URLSearchParams()

      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== "") {
          if (Array.isArray(value)) {
            if (value.length > 0) {
              searchParams.set(key, value.join(","))
            }
          } else {
            searchParams.set(key, value.toString())
          }
        }
      })

      const response = await fetch(`/api/contents?${searchParams.toString()}`)

      if (!response.ok) {
        throw new Error("Failed to fetch contents")
      }

      const data = await response.json()
      setContents(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred")
    } finally {
      setLoading(false)
    }
  }, [JSON.stringify(filters)])

  useEffect(() => {
    fetchContents()
  }, [fetchContents])

  return { contents, loading, error, refetch: () => fetchContents() }
}
