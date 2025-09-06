# Knowledge Base Piola Hackathon — September 6, 2025

## FIFA World Cup 26™ — Ticket Sales (First Phase)

### What’s happening
- First sales phase: Visa Presale Draw opens 2025-09-10 11:00 ET (17:00 CEST Berlin) and closes 2025-09-19 11:00 ET (17:00 CEST).
- Who can enter: Qualifying Visa cardholders (18+, FIFA ID required). No purchase necessary.
- Selection: Entries are processed via a randomized draw. Timing within the window does not affect chances.

### Notifications & purchasing after the draw
- From 2025-09-29, successful applicants receive an email with a date/time slot. Slots start 2025-10-01.
- A successful draw does not guarantee ticket availability.

### Ticket products available in Phase 1
- Single-match tickets (all 104 matches).
- Venue-specific and team-specific tickets.

### Pricing
- Group-stage tickets from USD 60.
- Final tickets up to USD 6,730.

### Later ticketing phases
- Multiple additional phases will follow.
- Phase 2 (Early Ticket Draw): Registration 2025-10-27 → 2025-10-31; purchases mid-November to early December.
- Phase 3 (Random Selection Draw): After the Final Draw, fans can apply for specific matches once group matchups are known.
- Final first-come-first-served stage: Closer to the tournament for remaining inventory.

### Additional products & resale
- Supporter tickets and conditional supporter tickets expected closer to the tournament.
- FIFA will launch a secure resale option later in 2025. Mexican residents will use a FIFA Ticket Exchange Platform.

### How to prepare
- Create a FIFA ID and register at fifa.com/tickets.
- Visa cardholders: log in during the entry window to enter the draw.

### Safety & validity
- Only buy via fifa.com/tickets.
- Hospitality packages and tickets from unofficial channels may be invalid.

### Quick FAQ
- Does entering earlier increase chances? No.
- If not selected, are there other chances? Yes — later phases.
- What kinds of tickets exist? Single-match, venue-specific, team-specific, supporter/conditional supporter.
- Price range: USD 60 (group stage) → USD 6,730 (final).
- Where to manage tickets? fifa.com/tickets with a FIFA ID.

---

## FIFA World Cup 26™ — Match Schedule, Fixtures, Results & Stadiums

### Tournament overview
- Dates: 2026-06-11 → 2026-07-19.
- Teams: 48 (hosts Canada, Mexico, USA auto-qualified).
- Format: 12 groups of 4. Top 2 + 8 best third-placed advance to Round of 32, then knockout.

### Key schedule milestones
- Group Stage: 2026-06-11 → 2026-06-27.
- Round of 32: 2026-06-28 → 2026-07-03.
- Round of 16: 2026-07-04 → 2026-07-07.
- Quarter-finals: 2026-07-10 → 2026-07-11.
- Semi-finals: 2026-07-15 → 2026-07-16.
- Bronze Final: 2026-07-18.
- Final: 2026-07-19.

### Venue assignments
- Opening match: Estadio Azteca (Mexico City) — 2026-06-11.
- Host openers: Canada in Toronto (2026-06-12); USA in Los Angeles (2026-06-12).
- Final: New York New Jersey Stadium (2026-07-19).
- Semi-finals: Dallas & Atlanta.
- Bronze final: Miami.
- Most matches in a single city: Dallas (9).

### Matches per host country
- Canada: 13 matches.
- Mexico: 13 matches.
- USA: 78 matches.

### Host cities & stadiums (rights-safe labels)
- Canada: Vancouver (BC Place Vancouver Stadium), Toronto (Toronto Stadium).
- Mexico: Mexico City (Estadio Azteca Mexico City), Guadalajara (Estadio Guadalajara), Monterrey (Estadio Monterrey).
- USA: Atlanta (Atlanta Stadium), Boston (Boston Stadium), Dallas (Dallas Stadium), Houston (Houston Stadium), Kansas City (Kansas City Stadium), Los Angeles (Los Angeles Stadium), Miami (Miami Stadium), New York New Jersey (New York New Jersey Stadium), Philadelphia (Philadelphia Stadium), San Francisco Bay Area (San Francisco Bay Area Stadium), Seattle (Seattle Stadium).

### Draw logistics
- Final Draw: 2025-12-05, Washington, DC (Kennedy Center), 12:00 ET.
- Host seedings: MEX → Group A (A1); CAN → Group B (B1); USA → Group D (D1).

---

## PRD — Embeddable Website Chatbot for FIFA.com (MVP)

### TL;DR
An embeddable chatbot that answers strictly from fifa.com content with enforced citations.  
Scope: English only; website pages only (no PDFs).

### Goals
- Business goals: >80% accuracy, latency <3s, deflect ≥30% inquiries, uptime >99.5%.
- User goals: Fast, accurate, sourced answers; easy admin setup; feedback flows.
- Non-goals: Multi-language, XLS/DOC ingestion, CRM integrations, model-only answers.

### User Stories
- Site visitors: quick answers, citations, feedback.
- Website admins: easy embedding, add seed URLs, monitor questions and accuracy.
- Support leads: analytics, review answers, avoid hallucinations.

### Functional Requirements
- Ingestion: Single-domain crawler (fifa.com/en). PDFs deferred.
- Retrieval & QA: Strict RAG mode, provenance enforcement, domain scoping, freshness controls, no-answer policy.
- Widget: JS snippet, short session memory, configurable evidence display.
- Admin console: data sources, usage logs, provenance, export.
- Guardrails: domain restriction, profanity filter.
- Analytics: thumbs up/down, basic dashboard.
- Deferred: internationalization, XLS/DOC ingestion.

### User Experience
1. Visitor opens chat launcher.
2. Asks a question; system retrieves fifa.com content.
3. Answer shown with citations or fallback.
4. Admin monitors logs and feedback.

### Technical Considerations
- Components: crawler, embedding, vector store, reranker, generator, admin API, widget.
- Privacy: encrypt data, no model training on user data.
- Performance: p95 ≤2.5s, uptime ≥99.5%.
- Challenges: hallucination, freshness, site structure.

### Milestones
- Hackathon Day (2025-09-06): crawler, hybrid retrieval, widget, admin console, eval set.
- Hardening Sprint (week of 2025-09-08): accuracy tuning, logs, security.
- Pilot Prep (weeks of 2025-09-15 → 26): sitemap ingestion, advanced admin, documentation.

### Success Metrics
- Eval set of 10 core FIFA questions (ticketing, resale, payments, etc.).
- Metrics: retrieval@5, answered_with_citation, exact/near-exact match, latency, user rating.

### Team
- 2–3 engineers + part-time designer/PM.
- Timeline: 1 day hackathon → 1–3 weeks to MVP.
