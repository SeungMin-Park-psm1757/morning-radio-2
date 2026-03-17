# Codex 시작 지시문 예시

아래 문장을 저장소 루트에서 Codex에 그대로 넣으면 됩니다.

---

## 1. 전체 구조부터 잡기
현재 저장소의 `AGENTS.md`와 `docs/quantum_weekly_radio/` 전체를 먼저 읽고,  
기존 일간 파이프라인을 건드리지 않는 additive 방식으로  
`src/morning_radio/weekly_quantum/` 구조를 생성해줘.  
우선 config, models, state_store, pipeline, cli의 골격과 테스트 골격만 만들고  
아직 source collector 구현은 하지 마.

---

## 2. 소스 수집기만 구현하기
`AGENTS.md`, `docs/quantum_weekly_radio/PROJECT_BRIEF_FOR_CODEX.md`,  
`docs/quantum_weekly_radio/SOURCE_MATRIX.md`,  
`.agents/skills/migrate_google_news_to_direct_source_collectors/SKILL.md`,
`.agents/skills/implement_source_adapter_contracts/SKILL.md`
를 읽고,  
주간 양자 뉴스용 direct source collectors를 구현해줘.  
기존 daily pipeline은 유지하고,  
새 구현은 `src/morning_radio/weekly_quantum/collectors/` 아래에 추가해줘.  
각 source는 timeout, retry, per-source cap, source health report를 포함해줘.

---

## 3. 전역 dedup + ranking 구현하기
현재 저장소의 dedup 감각을 유지하되  
이번에는 전체 소스 통합 후 전역 dedup이 먼저 일어나도록 구현해줘.  
`docs/quantum_weekly_radio/API_BUDGET_STRATEGY.md`와  
`.agents/skills/implement_global_cross_source_dedup_and_ranking/SKILL.md`
를 기준으로  
deterministic unit tests까지 같이 작성해줘.

---

## 4. 요약/스크립트/오디오 번들 구현하기
`docs/quantum_weekly_radio/API_BUDGET_STRATEGY.md`,
`docs/quantum_weekly_radio/FALLBACK_POLICY.md`,
`.agents/skills/implement_budget_aware_summarization/SKILL.md`,
`.agents/skills/generate_dual_host_weekly_radio_show/SKILL.md`,
`.agents/skills/implement_tts_and_telegram_delivery_bundle/SKILL.md`
를 읽고  
주간 텍스트 digest, full script, headlines script, mp3 2종, telegram bundle까지 구현해줘.  
반드시 `--skip-llm`와 `--skip-tts` 경로가 살아 있어야 해.

---

## 5. GitHub Actions까지 마무리
`templates/quantum_weekly_radio/workflows/weekly-quantum-radio.yml`를 참고해서  
`.github/workflows/weekly-quantum-radio.yml`를 실제 저장소에 추가하고,  
manual dispatch, artifact upload, run summary, state-safe rerun 동작까지 정리해줘.

---

## 6. 한 번에 MVP 완성 요청
`AGENTS.md`와 `docs/quantum_weekly_radio/` 전체,
`.agents/skills/` 전체를 읽고  
주간 양자기술 아침방송 MVP를 완성해줘.  
작업 순서는 `docs/quantum_weekly_radio/IMPLEMENTATION_ORDER.md`를 따르고,  
기존 일간 시스템은 깨지지 않게 유지해줘.  
마지막에는 변경 파일 목록, 테스트 결과, 남은 리스크를 요약해줘.
