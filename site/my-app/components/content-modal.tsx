"use client"

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Star, Heart, Eye, BookOpen, ExternalLink } from "lucide-react"
import Image from "next/image"
import type { ContentItem } from "@/lib/database"
import { useAuth } from "@/lib/auth-context"
import { formatNumber } from "@/lib/utils"

interface ContentModalProps {
  content: ContentItem | null
  isOpen: boolean
  onClose: () => void
}

export default function ContentModal({ content, isOpen, onClose }: ContentModalProps) {
  const { user, toggleFavorite } = useAuth()

  if (!content) return null

  const isFavorite = user?.favoriteWorks.includes(content.id.toString()) || false

  const handleFavoriteToggle = () => {
    if (user) {
      toggleFavorite(content.id.toString())
    }
  }

  const handleVisitSite = () => {
    window.open(content.siteUrl, "_blank")
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl">{content.title}</DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-1">
            <div className="aspect-[3/4] relative">
              <Image
                src={content.coverImage || "/placeholder.svg"}
                alt={content.title}
                fill
                className="object-cover rounded-lg"
              />
            </div>
          </div>

          <div className="md:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <Badge variant={content.type === "webtoon" ? "default" : "secondary"} className="text-sm">
                {content.type === "webtoon" ? "웹툰" : "소설"}
              </Badge>
              {user && (
                <Button variant="ghost" size="sm" onClick={handleFavoriteToggle}>
                  <Heart className={`h-5 w-5 ${isFavorite ? "fill-red-500 text-red-500" : "text-gray-400"}`} />
                </Button>
              )}
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">작가</h3>
              <p className="text-muted-foreground">{content.author}</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center space-x-2">
                <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                <span className="font-medium">{content.rating.toFixed(2)}</span>
                <span className="text-muted-foreground">평점</span>
              </div>
              <div className="flex items-center space-x-2">
                <BookOpen className="h-4 w-4" />
                <span className="font-medium">{content.episodes}화</span>
              </div>
              <div className="flex items-center space-x-2">
                <Eye className="h-4 w-4" />
                <span className="font-medium">{formatNumber(content.views)}</span>
                <span className="text-muted-foreground">조회수</span>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">장르</h3>
              <Badge variant="outline">{content.genre}</Badge>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">태그</h3>
              <div className="flex flex-wrap gap-2">
                {content.tags.map((tag) => (
                  <Badge key={tag} variant="outline" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">줄거리</h3>
              <p className="text-muted-foreground leading-relaxed">{content.description}</p>
            </div>

            <div className="pt-4">
              <Button onClick={handleVisitSite} className="w-full">
                <ExternalLink className="mr-2 h-4 w-4" />
                작품 보러가기
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
