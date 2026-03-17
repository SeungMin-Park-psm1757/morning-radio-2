# Quantum Weekly Morning Radio – Codex 통합 팩

이 팩은 현재 `daily-news-summary` 저장소를 **주간 양자기술 아침 방송 시스템**으로 확장하기 위한
**기획안 + 운영 문서 + Codex Skill Pack + 코드 템플릿 + 워크플로 템플릿** 묶음입니다.

목표는 다음과 같습니다.

- 월요일 **06:30 KST**에 실행
- 지난 1주일 동안의 양자기술 최신글을 수집
- 전역 중복 제거 후 핵심 이슈만 선별
- **2인 대화형 아침 방송 스크립트** 생성
- **텔레그램 텍스트 1건 + MP3 2건** 전달
- 기존 `morning_radio` 구조를 최대한 재사용
- API 사용량을 줄이기 위해 **목록/피드 요약 우선 + 대표기사만 상세 확장**
- 크롤링 실패 시 RSS/메타/타이틀 전용 모드까지 내려가는 fallback 설계

## 이 팩을 어떻게 쓰면 되나요?

1. 이 ZIP을 풀고
2. 안의 파일들을 **기존 저장소 루트**에 복사한 뒤
3. Codex를 저장소 루트에서 실행하고
4. `docs/quantum_weekly_radio/CODEX_STARTER_COMMANDS_KO.md`에 있는 지시문 중 하나를 그대로 사용하면 됩니다.

Codex가 자동으로 읽게 되는 핵심 파일은 아래 2개입니다.

- `AGENTS.md`
- `.agents/skills/*/SKILL.md`

## 포함 내용

- `AGENTS.md`  
  저장소 전체 작업 지침

- `.agents/skills/`  
  작업별 Skill 9종

- `docs/quantum_weekly_radio/`  
  기획안, 아키텍처, API 절약 전략, 소스 수집 전략, fallback 정책, 운영 런북, 단계별 구현 순서

- `templates/quantum_weekly_radio/`  
  `.env` 예시, GitHub Actions 워크플로 템플릿, 사이트 설정 YAML, 프롬프트 템플릿

- `starter_overlay/`  
  기존 repo에 **추가형(additive)** 으로 넣을 수 있는 파이썬 모듈/테스트/워크플로 시작 골격

- `examples/`  
  예시 출력 파일과 샘플 메시지

## 권장 구현 순서

1. 새 주간 파이프라인을 `src/morning_radio/weekly_quantum/` 아래에 추가
2. 기존 일간 파이프라인은 건드리지 않고 유지
3. 사이트 adapter 구현
4. 전역 dedup 구현
5. budget-aware summary 구현
6. 2인 대화형 스크립트 + 2개 MP3 + 텔레그램 번들 구현
7. GitHub Actions / 상태 저장 / 재시도 / 헬스체크 추가
8. 테스트와 운영 체크리스트 정리

## 입력 사이트 목록


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


## 가장 먼저 열어볼 파일

- `AGENTS.md`
- `docs/quantum_weekly_radio/PROJECT_BRIEF_KO.md`
- `docs/quantum_weekly_radio/PROJECT_BRIEF_FOR_CODEX.md`
- `docs/quantum_weekly_radio/IMPLEMENTATION_ORDER.md`
- `docs/quantum_weekly_radio/CODEX_STARTER_COMMANDS_KO.md`

## 주의

이 팩은 **완성 코드 배포본**이 아니라,
**Codex가 로컬 저장소에서 안정적으로 구현·수정·확장하도록 만드는 작업 패키지**입니다.

즉, 실제 가치는:
- 기획안 정리
- 판단 기준 고정
- 스킬 호출 기준 고정
- 코드 구조 힌트 제공
- 일정/예산/실패 대응 기준 명시
에 있습니다.
