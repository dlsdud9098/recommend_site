"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Menu, Search } from "lucide-react"
import SearchBar from "@/components/search/search-bar"

export default function Header() {
  const pathname = usePathname()
  const [isSearchOpen, setIsSearchOpen] = useState(false)
  const [isLoggedIn, setIsLoggedIn] = useState(false) // 실제로는 인증 상태에 따라 설정

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background">
      <div className="container flex h-16 items-center justify-between px-4">
        <div className="flex items-center">
          <Sheet>
            <SheetTrigger asChild className="mr-2 md:hidden">
              <Button variant="ghost" size="icon">
                <Menu className="h-5 w-5" />
                <span className="sr-only">메뉴 열기</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-[240px] sm:w-[300px]">
              <nav className="flex flex-col gap-4 mt-8">
                <Link href="/" className="text-lg font-medium">
                  홈
                </Link>
                <Link href="/novels" className="text-lg font-medium">
                  소설
                </Link>
                <Link href="/webtoons" className="text-lg font-medium">
                  웹툰
                </Link>
                <Link href="/community" className="text-lg font-medium">
                  커뮤니티
                </Link>
                <Link href="/library" className="text-lg font-medium">
                  내 서재
                </Link>
              </nav>
            </SheetContent>
          </Sheet>

          <Link href="/" className="flex items-center space-x-2">
            <span className="text-xl font-bold">북툰</span>
          </Link>

          <NavigationMenu className="hidden md:flex ml-6">
            <NavigationMenuList>
              <NavigationMenuItem>
                <Link href="/novels" legacyBehavior passHref>
                  <NavigationMenuLink className={navigationMenuTriggerStyle()}>소설</NavigationMenuLink>
                </Link>
              </NavigationMenuItem>
              <NavigationMenuItem>
                <Link href="/webtoons" legacyBehavior passHref>
                  <NavigationMenuLink className={navigationMenuTriggerStyle()}>웹툰</NavigationMenuLink>
                </Link>
              </NavigationMenuItem>
              <NavigationMenuItem>
                <Link href="/community" legacyBehavior passHref>
                  <NavigationMenuLink className={navigationMenuTriggerStyle()}>커뮤니티</NavigationMenuLink>
                </Link>
              </NavigationMenuItem>
              <NavigationMenuItem>
                <Link href="/library" legacyBehavior passHref>
                  <NavigationMenuLink className={navigationMenuTriggerStyle()}>내 서재</NavigationMenuLink>
                </Link>
              </NavigationMenuItem>
            </NavigationMenuList>
          </NavigationMenu>
        </div>

        <div className="flex items-center space-x-4">
          {isSearchOpen ? (
            <div className="relative w-full max-w-sm">
              <SearchBar onClose={() => setIsSearchOpen(false)} />
            </div>
          ) : (
            <Button variant="ghost" size="icon" onClick={() => setIsSearchOpen(true)}>
              <Search className="h-5 w-5" />
              <span className="sr-only">검색</span>
            </Button>
          )}

          {isLoggedIn ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src="/placeholder-avatar.jpg" alt="프로필" />
                    <AvatarFallback>사용자</AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuItem>
                  <Link href="/profile" className="w-full">
                    프로필
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Link href="/library" className="w-full">
                    내 서재
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Link href="/settings" className="w-full">
                    설정
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <button className="w-full text-left" onClick={() => setIsLoggedIn(false)}>
                    로그아웃
                  </button>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <div className="flex items-center space-x-2">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/login">로그인</Link>
              </Button>
              <Button size="sm" asChild>
                <Link href="/signup">회원가입</Link>
              </Button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
