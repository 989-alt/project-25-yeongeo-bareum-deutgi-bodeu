# Day 25 — 영어 발음 듣기 보드 (English Pronunciation Sound Board)

## 토픽 (from 100-vibecoding-topics.md #025)
- **카테고리**: 영어
- **대상**: 3~6학년 (초등)
- **환경**: TV (교실 큰 화면 전제 → 큰 타이포, 큰 버튼)
- **AI 사용**: ✕ (Web Speech API만)
- **디자인 브랜드**: ElevenLabs (보조: Apple) → 단일 브랜드로 **ElevenLabs** 선택. 음성 AI 브랜드 → 사운드 보드 토픽과 톤 정렬.

## 한 줄 정의
교사가 단어/문장을 입력하면 한국식이 아닌 영어 TTS로 즉시 들려주는 교실용 사운드 보드.
즐겨찾기·속도 조절·단어 카드 인쇄 지원.

## 기술 제약 (사전 결정)
- **스택**: 단일 `index.html` + vanilla CSS/JS. 빌드 단계 없음.
- **이유**: Web Speech API 한 줄 호출이면 충분. React/Vite는 오버킬.
- **외부 의존 0**: CDN 차단 환경 대비. Tailwind/Inter 폰트 모두 자기완비.
  - Inter는 system font stack으로 폴백 (사용 가능 시 우선).
  - Waldenburg는 라이선스 → `Georgia, 'Times New Roman', serif` 로 폴백 (ElevenLabs DESIGN.md "Known Gaps"에서 EB Garamond / GT Sectra 권고하지만 외부 폰트 의존 없이 시스템 serif).
- **저장**: `localStorage` (즐겨찾기·최근 사용)
- **인쇄**: `window.print()` + `@media print` CSS.
- **TTS**: `speechSynthesis` + `SpeechSynthesisUtterance` (영어 voice 필터).

## Web Speech API 주의점
- Voice list는 비동기 로드 → `speechSynthesis.onvoiceschanged` 핸들러 필요.
- 헤드리스 (Playwright) 환경에서 voices 비어있을 수 있음 → UI는 graceful degradation. 테스트에서는 voices 없어도 UI 렌더링 + 컨트롤 동작은 검증.
- 속도 슬라이더 범위: 0.5 ~ 1.5배 (토픽 명시).
- 한국식 발음 회피 → `voice.lang.startsWith('en')` 우선 필터, `en-US` / `en-GB` 우선 정렬.

## 데이터 시드
- 초등 영어 빈출 단어 30개 + 자주 쓰는 교실 표현 10문장 초기 제공 → 빈 화면 회피.
- 카테고리: Greeting / Classroom / Animals / Food / Colors / Phrases.
