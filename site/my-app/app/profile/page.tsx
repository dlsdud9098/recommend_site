"use client"

import { useState } from "react"
import Header from "@/components/header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Switch } from "@/components/ui/switch"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { User, Heart, BookOpen, Settings, Shield, AlertTriangle } from "lucide-react"
import ContentGrid from "@/components/content-grid"
import TagSelector from "@/components/tag-selector"
import AdultVerificationModal from "@/components/adult-verification-modal"
import { useContents } from "@/hooks/use-contents"
import ProtectedRoute from "@/components/protected-route"
import { useAuth } from "@/lib/auth-context"

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

export default function ProfilePage() {
  const { user, updateUserSettings, verifyAdult, toggleAdultContent } = useAuth()
  const [profile, setProfile] = useState({
    name: user?.name || "",
    email: user?.email || "",
    bio: "웹툰과 소설을 사랑하는 독자입니다.",
  })
  const [blockedGenres, setBlockedGenres] = useState<string[]>(user?.blockedGenres || [])
  const [blockedTags, setBlockedTags] = useState<string[]>(user?.blockedTags || [])
  const [isVerificationModalOpen, setIsVerificationModalOpen] = useState(false)

  // 찜한 작품 가져오기
  const { contents: favoriteContent } = useContents({
    limit: 100,
    showAdultContent: user?.showAdultContent || false,
  })

  // 최근 본 작품 (더미 데이터)
  const { contents: recentContent } = useContents({
    limit: 8,
    offset: 4,
    showAdultContent: user?.showAdultContent || false,
  })

  const filteredFavoriteContent = favoriteContent.filter((item) => user?.favoriteWorks.includes(item.id.toString()))

  const handleSaveProfile = () => {
    updateUserSettings({
      name: profile.name,
      email: profile.email,
      blockedGenres,
      blockedTags,
    })
    alert("프로필이 저장되었습니다!")
  }

  const handleAdultContentToggle = (checked: boolean) => {
    if (!user?.isAdultVerified && checked) {
      setIsVerificationModalOpen(true)
    } else {
      toggleAdultContent(checked)
    }
  }

  const handleAdultVerified = () => {
    verifyAdult()
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background">
        <Header activeTab="all" onTabChange={() => {}} />

        <main className="container mx-auto px-4 py-6">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center gap-4 mb-8">
              <Avatar className="h-20 w-20">
                <AvatarImage src={user?.avatar || "/placeholder.svg"} alt="프로필" />
                <AvatarFallback className="text-2xl">
                  <User className="h-10 w-10" />
                </AvatarFallback>
              </Avatar>
              <div>
                <h1 className="text-3xl font-bold">{user?.name}</h1>
                <p className="text-muted-foreground">{user?.email}</p>
                {user?.isAdultVerified && (
                  <div className="flex items-center gap-1 mt-1">
                    <Shield className="h-4 w-4 text-green-600" />
                    <span className="text-sm text-green-600">성인 인증 완료</span>
                  </div>
                )}
              </div>
            </div>

            <Tabs defaultValue="favorites" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="favorites" className="flex items-center gap-2">
                  <Heart className="h-4 w-4" />
                  찜한 작품
                </TabsTrigger>
                <TabsTrigger value="recent" className="flex items-center gap-2">
                  <BookOpen className="h-4 w-4" />
                  최근 본 작품
                </TabsTrigger>
                <TabsTrigger value="settings" className="flex items-center gap-2">
                  <Settings className="h-4 w-4" />
                  설정
                </TabsTrigger>
              </TabsList>

              <TabsContent value="favorites" className="mt-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Heart className="h-5 w-5" />
                      찜한 작품 ({filteredFavoriteContent.length}개)
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {filteredFavoriteContent.length > 0 ? (
                      <ContentGrid content={filteredFavoriteContent} />
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">아직 찜한 작품이 없습니다.</div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="recent" className="mt-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BookOpen className="h-5 w-5" />
                      최근 본 작품 ({recentContent.length}개)
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {recentContent.length > 0 ? (
                      <ContentGrid content={recentContent} />
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">최근 본 작품이 없습니다.</div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="settings" className="mt-6">
                <div className="space-y-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>기본 정보</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="name">이름</Label>
                        <Input
                          id="name"
                          value={profile.name}
                          onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="email">이메일</Label>
                        <Input
                          id="email"
                          type="email"
                          value={profile.email}
                          onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="bio">소개</Label>
                        <Textarea
                          id="bio"
                          value={profile.bio}
                          onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                          rows={3}
                        />
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Shield className="h-5 w-5" />
                        성인 콘텐츠 설정
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <Label>성인 작품 표시</Label>
                          <p className="text-sm text-muted-foreground">성인 인증 후 성인 작품을 볼 수 있습니다.</p>
                        </div>
                        <Switch
                          checked={user?.showAdultContent || false}
                          onCheckedChange={handleAdultContentToggle}
                          disabled={!user?.isAdultVerified && !user?.showAdultContent}
                        />
                      </div>

                      {!user?.isAdultVerified && (
                        <Alert>
                          <AlertTriangle className="h-4 w-4" />
                          <AlertDescription>
                            성인 작품을 보려면 본인 인증이 필요합니다. 위 토글을 활성화하면 인증 절차가 시작됩니다.
                          </AlertDescription>
                        </Alert>
                      )}
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>차단 설정</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <div className="space-y-3">
                        <Label>차단 장르</Label>
                        <p className="text-sm text-muted-foreground">선택한 장르의 작품은 목록에서 제외됩니다.</p>
                        <TagSelector
                          availableTags={AVAILABLE_GENRES}
                          selectedTags={blockedGenres}
                          onTagsChange={setBlockedGenres}
                          placeholder="차단할 장르 검색"
                          label="장르"
                        />
                      </div>

                      <div className="space-y-3">
                        <Label>차단 태그</Label>
                        <p className="text-sm text-muted-foreground">
                          선택한 태그가 포함된 작품은 목록에서 제외됩니다.
                        </p>
                        <TagSelector
                          availableTags={AVAILABLE_TAGS}
                          selectedTags={blockedTags}
                          onTagsChange={setBlockedTags}
                          placeholder="차단할 태그 검색"
                          label="태그"
                        />
                      </div>
                    </CardContent>
                  </Card>

                  <Button onClick={handleSaveProfile} className="w-full">
                    설정 저장
                  </Button>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </main>

        <AdultVerificationModal
          isOpen={isVerificationModalOpen}
          onClose={() => setIsVerificationModalOpen(false)}
          onVerified={handleAdultVerified}
        />
      </div>
    </ProtectedRoute>
  )
}
