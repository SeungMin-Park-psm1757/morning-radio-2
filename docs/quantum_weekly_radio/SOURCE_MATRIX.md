# Source Matrix

This matrix tells Codex how to treat each site.

## 1. The Quantum Insider – Daily / National / Business / Research / Education / Insights

### Primary collection method
- category page HTML

### Optional detail enrichment
- article page
- extract brief bullets when present
- extract meta description when bullets are missing

### Notes
- good for business / national / research split
- education / insights should usually receive lower weekly quota than hard news unless signal score is high

## 2. Phys.org Quantum Physics

### Primary collection method
- RSS if available
- fallback to category page HTML

### Detail enrichment
- use short article summary first
- fetch body only for top representatives

### Notes
- strong scientific signal
- do not let this source flood the weekly digest purely by volume

## 3. Quantum Zeitgeist – Quantum Research News

### Primary collection method
- category page HTML

### Detail enrichment
- article page excerpt / first paragraphs

### Notes
- research-heavy
- often overlaps with other research summaries, so global dedup matters

## 4. Quantum Computing Report – News

### Primary collection method
- news list page HTML

### Detail enrichment
- press-release linked detail only for top representatives

### Notes
- very good candidate for list-page-only extraction

## 5. Quantum Computing Report – Our Take

### Primary collection method
- list page HTML

### Notes
- lower-frequency commentary
- useful for “why it matters” context
- cap weekly volume aggressively

## 6. Quantum Computing Report – Qnalysis

### Primary collection method
- list page HTML

### Notes
- analysis-oriented and technical
- high value but low cadence
- usually select only if clearly relevant or unusually strong signal

## 7. Quantum Frontiers – News

### Primary collection method
- RSS feed when available
- fallback to category page HTML

### Notes
- blog-like cadence
- useful context source, but not always straight news
- cap volume and bias toward clearly newsy posts

## Cross-source policy

### Hard-news priority bucket
- TQI daily/national/business/research
- QCR news
- Phys.org recent quantum news

### Deep-context bucket
- TQI education / insights
- QCR our-take / qnalysis
- Quantum Frontiers

### Quota guideline
Weekly representative targets:
- hard news: 6–9 stories
- research/tech: 3–5 stories
- analysis/context: 1–3 stories

## Approved URLs


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

