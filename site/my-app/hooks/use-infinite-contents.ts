import { useState, useEffect, useCallback } from 'react'
import type { ContentItem } from '@/lib/database'

interface UseInfiniteContentsOptions {
  type?: 'all' | 'webtoon' | 'novel'
  title?: string
  author?: string
  genre?: string
  tags?: string[]
  minEpisodes?: number
  maxEpisodes?: number
  minRating?: number
  maxRating?: number
  blockedGenres?: string[]
  blockedTags?: string[]
  sortBy?: string
  showAdultContent?: boolean
}

const ITEMS_PER_PAGE = 30

export function useInfiniteContents(filters: UseInfiniteContentsOptions) {
  const [contents, setContents] = useState<ContentItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasMore, setHasMore] = useState(true)
  const [currentPage, setCurrentPage] = useState(0)
  const [totalCount, setTotalCount] = useState(0)

  // 필터가 변경될 때 초기화
  useEffect(() => {
    setContents([])
    setCurrentPage(0)
    setHasMore(true)
    setError(null)
  }, [filters])

  // 데이터 로드 함수
  const loadContents = useCallback(async (page: number, isLoadMore: boolean = false) => {
    if (loading) return

    setLoading(true)
    setError(null)

    try {
      const params = new URLSearchParams({
        type: filters.type || 'all',
        sortBy: filters.sortBy || 'popularity',
        limit: ITEMS_PER_PAGE.toString(),
        offset: (page * ITEMS_PER_PAGE).toString(),
        showAdultContent: (filters.showAdultContent || false).toString(),
      })

      // 필터 추가
      if (filters.title) params.append('title', filters.title)
      if (filters.author) params.append('author', filters.author)
      if (filters.genre) params.append('genre', filters.genre)
      if (filters.tags && filters.tags.length > 0) {
        params.append('keywords', filters.tags.join(','))
      }
      if (filters.minEpisodes) params.append('minEpisodes', filters.minEpisodes.toString())
      if (filters.maxEpisodes) params.append('maxEpisodes', filters.maxEpisodes.toString())
      if (filters.minRating) params.append('minRating', filters.minRating.toString())
      if (filters.maxRating) params.append('maxRating', filters.maxRating.toString())
      if (filters.blockedGenres && filters.blockedGenres.length > 0) {
        params.append('blockedGenres', filters.blockedGenres.join(','))
      }
      if (filters.blockedTags && filters.blockedTags.length > 0) {
        params.append('blockedTags', filters.blockedTags.join(','))
      }

      const response = await fetch(`/api/contents?${params}`)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const newContents = await response.json()

      if (isLoadMore) {
        setContents(prev => {
          // 중복 제거
          const existingIds = new Set(prev.map(item => item.id))
          const uniqueNewContents = newContents.filter((item: ContentItem) => !existingIds.has(item.id))
          return [...prev, ...uniqueNewContents]
        })
      } else {
        setContents(newContents)
      }

      // 전체 개수 추정 (첫 페이지에서만)
      if (page === 0 && newContents.length > 0) {
        // 정확한 전체 개수는 별도 API로 가져와야 하지만, 임시로 추정
        setTotalCount(newContents.length < ITEMS_PER_PAGE ? newContents.length : newContents.length * 10)
      }

      // 더 이상 로드할 데이터가 있는지 확인
      setHasMore(newContents.length === ITEMS_PER_PAGE)
      
    } catch (err) {
      console.error('Error loading contents:', err)
      setError(err instanceof Error ? err.message : '데이터를 불러오는 중 오류가 발생했습니다.')
    } finally {
      setLoading(false)
    }
  }, [filters, loading])

  // 다음 페이지 로드
  const loadMore = useCallback(() => {
    if (!hasMore || loading) return
    
    const nextPage = currentPage + 1
    setCurrentPage(nextPage)
    loadContents(nextPage, true)
  }, [currentPage, hasMore, loading, loadContents])

  // 초기 로드 및 필터 변경 시 로드
  useEffect(() => {
    loadContents(0, false)
  }, [filters])

  return {
    contents,
    loading,
    error,
    hasMore,
    loadMore,
    totalCount,
    refresh: () => {
      setContents([])
      setCurrentPage(0)
      setHasMore(true)
      loadContents(0, false)
    }
  }
}
