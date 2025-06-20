"use client"

import type React from "react"

import { useState } from "react"
import Image from "next/image"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Star, Heart, Eye, Shield, ImageIcon } from "lucide-react"
import type { ContentItem } from "@/lib/database"
import { useAuth } from "@/lib/auth-context"
import { formatNumber } from "@/lib/utils"
import ContentModal from "./content-modal"

interface ContentGridProps {
  content: ContentItem[]
}

// 이미지 컴포넌트를 위한 별도 컴포넌트
function ContentImage({ src, alt, item }: { src: string; alt: string; item: ContentItem }) {
  const [imageError, setImageError] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // 이미지 URL 유효성 검사 및 기본값 처리
  const getImageSrc = () => {
    // 프로토콜 상대 URL (//) 처리
    if (src && src.startsWith('//')) {
      return '/placeholder.svg' // 프로토콜 상대 URL은 placeholder로 대체
    }
    
    // 외부 이미지가 실패하거나 placeholder인 경우 로컬 이미지 사용
    if (!src || src === '/placeholder.svg' || imageError || src.includes('img.novelpia.com')) {
      return '/placeholder.svg'
    }
    
    // 상대 URL을 절대 URL로 변환 (필요한 경우)
    if (src.startsWith('/') && !src.startsWith('//')) {
      return src // 이미 절대 경로인 경우
    }
    
    return src
  }

  // 제목의 첫 글자들을 이용한 이니셜 생성
  const getInitials = (title: string) => {
    return title.slice(0, 2).toUpperCase()
  }

  return (
    <div className="aspect-[3/4] relative bg-gradient-to-br from-blue-100 to-purple-100">
      {!imageError && getImageSrc() !== '/placeholder.svg' ? (
        <Image 
          src={getImageSrc()}
          alt={alt}
          fill 
          className="object-cover"
          onLoad={() => setIsLoading(false)}
          onError={() => {
            setImageError(true)
            setIsLoading(false)
          }}
          placeholder="blur"
          blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
        />
      ) : (
        <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-100 to-purple-100">
          <div className="text-center p-4">
            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-2 shadow-md">
              <span className="text-lg font-bold text-gray-600">{getInitials(item.title)}</span>
            </div>
            <p className="text-xs text-gray-600 font-medium line-clamp-2">{item.title}</p>
            <p className="text-xs text-gray-400 mt-1">{item.author}</p>
          </div>
        </div>
      )}
      {isLoading && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse" />
      )}
    </div>
  )
}

export default function ContentGrid({ content }: ContentGridProps) {
  const { user, toggleFavorite } = useAuth()
  const [selectedContent, setSelectedContent] = useState<ContentItem | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleContentClick = (item: ContentItem) => {
    setSelectedContent(item)
    setIsModalOpen(true)
  }

  const handleFavoriteToggle = (e: React.MouseEvent, workId: string) => {
    e.stopPropagation()
    if (user) {
      toggleFavorite(workId)
    }
  }

  if (content.length === 0) {
    return null // 상위 컴포넌트에서 처리
  }

  return (
    <>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
        {content.map((item) => {
          const isFavorite = user?.favoriteWorks.includes(item.id.toString()) || false

          return (
            <Card key={item.id} className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer">
              <CardContent className="p-0" onClick={() => handleContentClick(item)}>
                <div className="relative">
                  <ContentImage 
                    src={item.coverImage || "/placeholder.svg"} 
                    alt={item.title} 
                    item={item}
                  />
                  <Badge
                    variant={item.type === "webtoon" ? "default" : "secondary"}
                    className="absolute top-2 right-2 text-xs"
                  >
                    {item.type === "webtoon" ? "웹툰" : "소설"}
                  </Badge>
                  {item.isAdult && (
                    <Badge variant="destructive" className="absolute top-2 left-2 text-xs">
                      <Shield className="h-3 w-3 mr-1" />
                      19+
                    </Badge>
                  )}
                  {user && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="absolute bottom-2 left-2 h-8 w-8 p-0 bg-white/80 hover:bg-white/90"
                      onClick={(e) => handleFavoriteToggle(e, item.id.toString())}
                    >
                      <Heart className={`h-4 w-4 ${isFavorite ? "fill-red-500 text-red-500" : "text-gray-400"}`} />
                    </Button>
                  )}
                </div>

                <div className="p-3 space-y-2">
                  <h3 className="font-medium text-sm line-clamp-2 leading-tight">{item.title}</h3>

                  <p className="text-xs text-muted-foreground">{item.author}</p>

                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center space-x-1">
                      <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                      <span>{item.rating.toFixed(1)}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Eye className="h-3 w-3" />
                      <span>{formatNumber(item.views)}</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-1">
                    {item.tags.slice(0, 2).map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs px-1 py-0">
                        {tag}
                      </Badge>
                    ))}
                    {item.tags.length > 2 && (
                      <Badge variant="outline" className="text-xs px-1 py-0">
                        +{item.tags.length - 2}
                      </Badge>
                    )}
                  </div>

                  <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">{item.description}</p>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <ContentModal content={selectedContent} isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </>
  )
}
