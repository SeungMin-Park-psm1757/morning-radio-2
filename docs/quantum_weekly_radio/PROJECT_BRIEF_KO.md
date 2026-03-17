# 주간 양자기술 아침방송 시스템 기획안

## 1. 프로젝트 목적

기존 `daily-news-summary` 저장소의 강점인
- 기사 수집
- 중요도 산정
- 중복 제거
- 대화형 라디오 스크립트 생성
- TTS
- 텔레그램 전달
구조를 그대로 살리되,

이제는 **지정된 양자기술 사이트들만 직접 수집**해서
**주 1회 월요일 06:30 KST**에
**한 주의 핵심 동향**을 정리하는 시스템으로 확장한다.

## 2. 사용자 요구사항 요약

- 기존 대화형 라디오 형식 유지
- 텔레그램으로 전달
- 산출물은 **텍스트 1건 + MP3 2건**
- 대상 기간은 최근 1주
- 중복 제거는 기존 알고리즘의 감각을 유지
- 게시글 수가 많아도 API 한도에 걸리지 않도록 설계
- 크롤링 실패 시 fallback 필요
- Codex 로컬에 문서/스킬을 넣고 “구현해”라고 지시하면 진행 가능해야 함

## 3. 대상 소스


- https://thequantuminsider.com/category/daily/
- https://thequantuminsider.com/category/daily/national/
- https://thequantuminsider.com/category/daily/business/
- https://thequantuminsider.com/category/daily/researchandtech/
- https://thequantuminsider.com/category/exclusives/education/
- https://thequantuminsider.com/category/exclusives/insights/
- https://phys.org/physics-news/quantum-physics/?hl=ko-KR
- https://quantumzeitgeist.com/category/quantum-research-news/
- https://quantumcomputingreport.com/news/
- https://quantumcomputingreport.com/our-take/
- https://quantumcomputingreport.com/qnalysis/
- https://quantumfrontiers.com/category/news/


## 4. 핵심 산출물

### 사용자용 산출물
- 주간 텍스트 digest
- `weekly_full.mp3`
- `weekly_headlines.mp3`

### 내부 산출물
- 수집 raw 목록
- normalize 결과
- dedup cluster 결과
- 선정 기사 목록
- category briefs
- 대화형 라디오 스크립트
- source health report
- run metadata
- last successful run state

## 5. 운영 정책

### 실행 시점
- 매주 월요일 06:30 KST

### 윈도우 정책
- “최근 7일 고정”보다 **마지막 성공 실행 시점 ~ 현재 실행 시점**을 기본 윈도우로 사용
- 최초 실행 시에만 안전 버퍼를 포함한 8일 수집 허용

### 전달 정책
- 텔레그램 텍스트 1건
- 전체 방송 MP3 1건
- 헤드라인 MP3 1건

## 6. 기술 방향

### 수집
- Google News RSS 검색 방식 대신 **사이트별 adapter**
- 우선순위:
  1. RSS
  2. 카테고리 목록 HTML
  3. sitemap / meta description
  4. title-only fallback

### 중복 제거
- 기존 exact-title / token-overlap / Jaccard 성격 유지
- 단, 이번에는 **전체 소스 통합 후 전역 dedup**을 먼저 수행

### API 절약
- 모든 글 본문을 LLM에 넣지 않는다
- 목록 excerpt / RSS summary / site-provided bullets 우선
- dedup 이후 대표기사만 상세 확장
- 최종적으로 상위 대표기사 몇 개만 LLM에 투입
- TTS는 최종 스크립트 2건에만 사용

## 7. 비기능 요구사항

- 기존 일간 파이프라인을 망가뜨리지 않을 것
- 공용 함수 재사용 가능하면 재사용할 것
- source 실패 시 전체 run이 죽지 않도록 할 것
- schedule 지연, API 실패, 텔레그램 실패, TTS 실패 각각 독립 대응할 것
- public repo inactivity / schedule 드롭 리스크를 고려할 것

## 8. 권장 구현 전략

### 단계 1
새 weekly pipeline을 별도 namespace에 additive 하게 구현  
예: `src/morning_radio/weekly_quantum/`

### 단계 2
source adapters 구현

### 단계 3
전역 dedup + ranking 구현

### 단계 4
budget-aware summary + dialogue script 생성

### 단계 5
dual-MP3 + Telegram bundle 구현

### 단계 6
GitHub Actions / 상태저장 / 운영런북 / 헬스체크 추가

## 9. 성공 기준

다음 조건을 충족하면 1차 성공으로 본다.

- 월요일 06:30 KST 기준 자동 실행
- 승인된 소스에서 1주간 게시물 수집
- 전역 dedup 후 8~15개 대표 이슈 선별
- 텍스트 1건 + MP3 2건 생성
- 텔레그램 전송 성공
- 일부 source 실패 시에도 방송 생성 가능
- `--skip-llm`, `--skip-tts` 스모크 경로 동작
