"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Shield, AlertTriangle } from "lucide-react"

interface AdultVerificationModalProps {
  isOpen: boolean
  onClose: () => void
  onVerify: () => void
}

export default function AdultVerificationModal({ isOpen, onClose, onVerify }: AdultVerificationModalProps) {
  const [birthDate, setBirthDate] = useState("")
  const [agreed, setAgreed] = useState(false)
  const [error, setError] = useState("")

  const handleVerify = () => {
    setError("")

    if (!birthDate) {
      setError("생년월일을 입력해주세요.")
      return
    }

    if (!agreed) {
      setError("약관에 동의해주세요.")
      return
    }

    // 생년월일로 성인 여부 확인
    const birth = new Date(birthDate)
    const today = new Date()
    let age = today.getFullYear() - birth.getFullYear()
    const monthDiff = today.getMonth() - birth.getMonth()

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--
    }

    if (age < 19) {
      setError("19세 미만은 성인 인증을 할 수 없습니다.")
      return
    }

    // 성인 인증 완료
    onVerify()
    onClose()
    setBirthDate("")
    setAgreed(false)
  }

  const handleClose = () => {
    onClose()
    setBirthDate("")
    setAgreed(false)
    setError("")
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-red-500" />
            성인 인증
          </DialogTitle>
          <DialogDescription>
            성인 콘텐츠를 이용하시려면 성인 인증이 필요합니다.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              만 19세 이상만 성인 콘텐츠를 이용할 수 있습니다.
            </AlertDescription>
          </Alert>

          <div className="space-y-2">
            <Label htmlFor="birthDate">생년월일</Label>
            <Input
              id="birthDate"
              type="date"
              value={birthDate}
              onChange={(e) => setBirthDate(e.target.value)}
              max={new Date().toISOString().split('T')[0]}
            />
          </div>

          <div className="space-y-4">
            <div className="flex items-start space-x-2">
              <Checkbox
                id="terms"
                checked={agreed}
                onCheckedChange={(checked) => setAgreed(checked as boolean)}
              />
              <div className="grid gap-1.5 leading-none">
                <Label htmlFor="terms" className="text-sm font-medium">
                  성인 콘텐츠 이용 약관에 동의합니다
                </Label>
                <p className="text-xs text-muted-foreground">
                  만 19세 이상임을 확인하며, 성인 콘텐츠 이용에 동의합니다.
                </p>
              </div>
            </div>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="flex gap-2 pt-4">
            <Button variant="outline" onClick={handleClose} className="flex-1">
              취소
            </Button>
            <Button onClick={handleVerify} className="flex-1">
              인증하기
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
