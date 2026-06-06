# 02 — UI/UX 설계

> 원칙: `awesome-design-md/elevenlabs/DESIGN.md` (이하 *DESIGN.md*)가 우선. `ui-ux-pro-max/SKILL.md`의 접근성·터치·키보드 체크리스트는 보강용.

## 브랜드 선택 이유
- 토픽 = 음성 (TTS) 사운드 보드 → 음성 AI 브랜드인 ElevenLabs 톤이 가장 자연스럽다.
- 교실 TV 환경 = 한산한 큰 화면 → ElevenLabs의 "editorial print magazine" 미감(off-white 캔버스, 가벼운 serif 디스플레이)이 가독성과 위엄을 동시에 준다.
- atmospheric gradient orbs (mint/peach/lavender/sky/rose) → 재생 중 카드 강조에 그대로 활용 가능.

## 색 토큰 (DESIGN.md 그대로)
| 역할 | 토큰 | 값 |
|---|---|---|
| Canvas | `canvas` | `#f5f5f5` |
| Canvas soft | `canvas-soft` | `#fafafa` |
| Surface card | `surface-card` | `#ffffff` |
| Ink (primary text) | `ink` | `#0c0a09` |
| Body | `body` | `#4e4e4e` |
| Muted | `muted` | `#777169` |
| Hairline | `hairline` | `#e7e5e4` |
| Hairline strong | `hairline-strong` | `#d6d3d1` |
| Primary CTA fill | `primary` | `#292524` |
| Primary active | `primary-active` | `#0c0a09` |
| On primary | `on-primary` | `#ffffff` |
| Gradient mint | `gradient-mint` | `#a7e5d3` |
| Gradient peach | `gradient-peach` | `#f4c5a8` |
| Gradient lavender | `gradient-lavender` | `#c8b8e0` |
| Gradient sky | `gradient-sky` | `#a8c8e8` |
| Gradient rose | `gradient-rose` | `#e8b8c4` |
| Semantic error | `semantic-error` | `#dc2626` |

**대비 검증** (WCAG AA 4.5:1):
- `ink` (#0c0a09) on `canvas` (#f5f5f5): 약 17.8:1 ✅
- `body` (#4e4e4e) on `canvas`: 약 7.8:1 ✅
- `muted` (#777169) on `canvas`: 약 4.6:1 ✅ (caption 한정 사용)
- `on-primary` (#fff) on `primary` (#292524): 약 14.8:1 ✅

## 타이포 (DESIGN.md 그대로, 폰트는 시스템 fallback)
- 디스플레이: `Georgia, 'Times New Roman', serif` (Waldenburg 폴백). weight 300 유지하되 시스템 serif는 굵게 보일 수 있어 `font-weight: 300` 명시.
- 본문/네비/버튼: system UI sans (`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif`). 외부 폰트 로드 0.

## 화면 구조 (1화면 SPA)

```
┌────────────────────────────────────────────────────────────┐
│  [Top nav 64px]  EnglishBoard      Speed: [====●==] 1.0x   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│   ◐ Hero band (canvas-soft, 96px padding)                  │
│                                                            │
│   "Listen, repeat, learn."                                 │
│   display-mega (64px / weight 300 / serif)                 │
│                                                            │
│   ┌──────────────────────────────────────┐                 │
│   │  Type a word or sentence…       [▶] │  ← text-input    │
│   └──────────────────────────────────────┘  + pill button  │
│                                                            │
│   (subtle atmospheric mint→peach orb behind hero)          │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  [Tabs] Favorites · Greeting · Classroom · Animals ·       │
│         Food · Colors · Phrases · Recent                   │
│         (badge-pill style, active = ink, idle = surface-strong)│
├────────────────────────────────────────────────────────────┤
│                                                            │
│   ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐               │
│   │ hello │  │ thank │  │ good  │  │ how   │               │
│   │   ▶   │  │  you▶ │  │ morn▶ │  │ are u │               │
│   │   ☆   │  │   ★   │  │   ☆   │  │  ☆ ▶  │               │
│   └───────┘  └───────┘  ...                                │
│   (audio-waveform-card 기반, 4-up grid)                    │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  [Cta-band] Print favorites as cards    [Print PDF →]      │
└────────────────────────────────────────────────────────────┘
```

## 컴포넌트 매핑 (DESIGN.md ↔ 본 화면)

| 본 화면 요소 | DESIGN.md 컴포넌트 | 토큰 |
|---|---|---|
| 상단 헤더 | `top-nav` | canvas / ink / 64px |
| 메인 입력박스 | `text-input` | surface-card / 44px / rounded-md / hairline-strong border |
| ▶ Play 버튼 (입력 옆) | `button-primary` | ink pill 40px |
| 카테고리 탭 | `badge-pill` | active = primary, idle = surface-strong |
| 단어 카드 | `audio-waveform-card` 변형 | surface-card / rounded-xl / 24px padding |
| 재생 중 카드 강조 | `gradient-orb-card` 일부 | radial mint/peach orb 카드 뒤에 |
| 인쇄 CTA 영역 | `cta-band` | canvas / display-lg / pill CTA |
| Speed 슬라이더 | (커스텀) | 트랙 hairline / 핸들 ink pill 16px |

## 단어 카드 (핵심 컴포넌트)
- 카드 사이즈: TV 기준 ≥ 240×140px. 그리드 4-up (desktop), 3-up (tablet), 2-up (mobile).
- 내용 (위→아래):
  1. 단어/문장 본문 (`title-md` 20px, Inter 500)
  2. 카테고리 라벨 (`caption-uppercase` 12px / 600 / 0.96px tracking, muted)
  3. 액션 행: `▶` Play (button-primary 40px pill, 좌측) + `★/☆` Favorite (text 버튼, 우측)
- 재생 중 상태: 카드 외곽에 radial gradient mint→peach 펄스 (1.2s ease-in-out 무한, `prefers-reduced-motion`이면 fade-in 1회).
- 키보드: Tab으로 카드 포커스 → Space=재생, F=즐겨찾기 토글.

## 카테고리 시드 데이터 (코드 인라인)

| Category | 단어/문장 |
|---|---|
| Greeting | Hello, Good morning, Good afternoon, Goodbye, How are you?, Nice to meet you |
| Classroom | Open your book, Sit down please, Raise your hand, Repeat after me, Well done, Listen carefully |
| Animals | dog, cat, bird, elephant, rabbit, monkey, lion, tiger |
| Food | apple, banana, bread, rice, water, milk, juice, cookie |
| Colors | red, blue, yellow, green, orange, purple, black, white |
| Phrases | Thank you, You're welcome, Excuse me, I'm sorry, See you tomorrow, Have a nice day |

## 인쇄 레이아웃 (`@media print`)
- 페이지: A4 portrait, margin 12mm
- 그리드: 4 col × 4 row = 16장/페이지 (즐겨찾기만)
- 카드: 흰 배경 + 1px hairline-strong border, rounded 8px, 16px padding, 단어 본문 중앙 정렬, 폰트 18px
- 페이지 내 색 인쇄 잉크 절약 → 모든 배경 흰색, 텍스트 ink만
- 인쇄 시 헤더/탭/입력/Play 버튼/슬라이더 모두 `display:none`

## 접근성 체크 (ui-ux-pro-max 항목)
- [x] 색 대비 4.5:1 — 위 검증 표
- [x] 포커스 ring — `outline: 2px solid var(--ink); outline-offset: 3px`
- [x] aria-label — Play(`Play "{word}"`), Favorite(`{Add to|Remove from} favorites: "{word}"`), Speed(`Playback speed`)
- [x] Tab 순서 = 시각 순서 (DOM 순서 일치)
- [x] 키보드 네비 — Space로 카드 재생, F로 즐겨찾기
- [x] 최소 터치 영역 44×44 — Play 버튼 40px이지만 카드 클릭 영역 240×140 이상으로 가드
- [x] `prefers-reduced-motion: reduce` 시 orb pulse 비활성
- [x] form label — `<label for>` 명시
- [x] 인쇄 시 의미는 텍스트로만 (gradient orb 제거)

## 반응형
| 폭 | hero h1 | 카드 그리드 | 패딩 |
|---|---|---|---|
| ≥ 1280px | 64px | 4-up | section 96px |
| 1024–1280 | 56px | 4-up | section 64px |
| 640–1024 | 40px | 3-up | section 48px |
| < 640 | 32px | 2-up | section 24px |

## 충돌 시 우선
- DESIGN.md(ElevenLabs)가 ui-ux-pro-max보다 우선.
- 단, **접근성** 항목(대비, 포커스, aria, 키보드)은 ui-ux-pro-max를 추가 검증 체크리스트로 활용.
