"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { User, LogOut, Settings } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import UserSettingsModal from "@/components/user-settings-modal"
import type { ContentType } from "@/app/page"

interface HeaderProps {
  activeTab: ContentType
  onTabChange: (tab: ContentType) => void
}

export default function Header({ activeTab, onTabChange }: HeaderProps) {
  const { user, logout } = useAuth()
  const router = useRouter()
  const [showSettings, setShowSettings] = useState(false)

  const handleLogout = () => {
    logout()
    router.push("/")
  }

  const handleTabChange = (tab: ContentType) => {
    onTabChange(tab)
    router.push("/")
  }

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center space-x-6">
            <Link href="/" className="text-2xl font-bold">
              웹툰·소설 추천
            </Link>

            <nav className="flex items-center space-x-1">
              <Button
                variant={activeTab === "all" ? "default" : "ghost"}
                onClick={() => handleTabChange("all")}
                className="px-4"
              >
                전체
              </Button>
              <Button
                variant={activeTab === "webtoon" ? "default" : "ghost"}
                onClick={() => handleTabChange("webtoon")}
                className="px-4"
              >
                웹툰
              </Button>
              <Button
                variant={activeTab === "novel" ? "default" : "ghost"}
                onClick={() => handleTabChange("novel")}
                className="px-4"
              >
                소설
              </Button>
              <Button variant="ghost" className="px-4" asChild>
                <Link href="/ai-recommend">AI추천</Link>
              </Button>
              {user && (
                <Button variant="ghost" className="px-4" asChild>
                  <Link href="/profile">내 정보</Link>
                </Button>
              )}
            </nav>
          </div>

          <div className="flex items-center space-x-4">
            {user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={user.avatar || "/placeholder.svg"} alt={user.name} />
                      <AvatarFallback>
                        <User className="h-4 w-4" />
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <div className="flex items-center justify-start gap-2 p-2">
                    <div className="flex flex-col space-y-1 leading-none">
                      <p className="font-medium">{user.name}</p>
                      <p className="w-[200px] truncate text-sm text-muted-foreground">{user.email}</p>
                    </div>
                  </div>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link href="/profile" className="w-full cursor-pointer">
                      <User className="mr-2 h-4 w-4" />내 정보
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setShowSettings(true)} className="cursor-pointer">
                    <Settings className="mr-2 h-4 w-4" />
                    설정
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} className="cursor-pointer">
                    <LogOut className="mr-2 h-4 w-4" />
                    로그아웃
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <div className="flex items-center space-x-2">
                <Button variant="ghost" size="sm" asChild>
                  <Link href="/login">로그인</Link>
                </Button>
                <Button size="sm" asChild>
                  <Link href="/register">회원가입</Link>
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
      
      <UserSettingsModal
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
      />
    </header>
  )
}
