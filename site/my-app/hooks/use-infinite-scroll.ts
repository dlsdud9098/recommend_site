"use client"

import { useState, useEffect, useCallback } from "react"

interface UseInfiniteScrollProps<T> {
  data: T[]
  itemsPerPage?: number
}

export function useInfiniteScroll<T>({ data, itemsPerPage = 30 }: UseInfiniteScrollProps<T>) {
  const [displayedItems, setDisplayedItems] = useState<T[]>([])
  const [hasMore, setHasMore] = useState(true)
  const [isLoading, setIsLoading] = useState(false)

  // 데이터가 변경될 때 초기화
  useEffect(() => {
    const initialItems = data.slice(0, itemsPerPage)
    setDisplayedItems(initialItems)
    setHasMore(data.length > itemsPerPage)
  }, [data, itemsPerPage])

  const loadMore = useCallback(async () => {
    if (isLoading || !hasMore) return

    setIsLoading(true)

    // 로딩 시뮬레이션
    await new Promise((resolve) => setTimeout(resolve, 500))

    const currentLength = displayedItems.length
    const nextItems = data.slice(currentLength, currentLength + itemsPerPage)

    if (nextItems.length === 0) {
      setHasMore(false)
    } else {
      setDisplayedItems((prev) => [...prev, ...nextItems])
      setHasMore(currentLength + nextItems.length < data.length)
    }

    setIsLoading(false)
  }, [data, displayedItems.length, itemsPerPage, isLoading, hasMore])

  // 스크롤 이벤트 처리
  useEffect(() => {
    const handleScroll = () => {
      if (window.innerHeight + document.documentElement.scrollTop >= document.documentElement.offsetHeight - 1000) {
        loadMore()
      }
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [loadMore])

  return {
    displayedItems,
    hasMore,
    isLoading,
    loadMore,
  }
}
