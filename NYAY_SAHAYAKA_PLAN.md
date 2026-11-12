# Nyay Sahayaka — Implementation Plan & Progress Tracker

This document tracks implementation progress step-by-step. Each part is implemented, verified with automated tests, and logged in `NYAY_SAHAYAKA_ENGINEERING_LOG.md`.

---

## Progress Overview
- [x] **Part 0: Workspace Audit, Cleanup & Environment Preparation**
- [x] **Part 1: Auditable Scheme Tool Suite & Central vs State Data Retrieval**
- [x] **Part 2: Context Sufficiency & Clarification-First Engine**
- [x] **Part 3: Multi-Agent Architecture (Supervisor, Central Agent, State Agent)**
- [x] **Part 4: Structured Eligibility Engine, "Why Not Eligible", and Alternative Scheme Recovery Flow**
- [x] **Part 5: Confidence-Gated Answering, Trust Scoring & Abstention Layer**
- [x] **Part 6: Pre/Post-Generation Evidence Validation, Claim Audit & Citation Engine**
- [x] **Part 7: Multilingual Equivalence & Single-Brain Voice Integration**
- [x] **Part 8: Comprehensive Evaluation Harness & RAG Benchmarking Suite**
- [x] **Part 9: End-to-End System Verification & Final Engineering Log Polish**

---

## Detailed Task Checklist

### Part 0: Workspace Audit, Cleanup & Environment Preparation
- [x] Inspect existing backend and frontend components.
- [x] Identify redundant and obsolete files (`data_test*.json` dumps, duplicate configs).
- [x] Clean up unneeded files.
- [x] Fix `sec_title` bug in `qdrant_service.py`.
- [x] Initialize and verify Python virtual environment and dependencies.
- [x] Verify: Dependencies load properly and existing baseline tests run.

### Part 1: Auditable Scheme Tool Suite (`agents/tools/`)
- [x] Implement typed scheme tool registry:
  - `search_central_schemes`
  - `search_state_schemes`
  - `get_scheme_details`
  - `get_eligibility_rules`
  - `get_required_documents`
  - `get_application_process`
  - `find_alternative_schemes`
  - `retrieve_source_evidence`
  - `check_source_freshness_and_conflicts`
- [x] Add hybrid search + payload filtering in retrieval tools.
- [x] Verify: Unit test tool execution with mocked & real queries (`test_scheme_tools` passed).

### Part 2: Context Sufficiency & Clarification-First Engine
- [x] Implement `ContextManager` and `FactClassification` (`USER_CONFIRMED`, `INFERRED`, `UNKNOWN`).
- [x] Implement `ContextSufficiencyChecker`:
  - Detect missing decision-critical variables (State, Category, Gender, Occupation, Income, Education).
  - Generate structured option-based clarification queries (e.g. A/B/C/D).
- [x] Verify: Ambiguous or incomplete user queries trigger clarification rather than guessing (`test_context_manager_and_clarification` passed).

### Part 3: Multi-Agent Architecture
- [x] Implement `CentralSchemeAgent` for Union Ministries and national schemes.
- [x] Implement `StateSchemeAgent` for state portals and domicile-specific schemes.
- [x] Update `SupervisorRouter` with smart jurisdiction detection, parallel dispatch, and evidence merger.
- [x] Integrate into LangGraph state machine.
- [x] Verify: Test routing across pure central, pure state, and cross-jurisdictional queries (`test_end_to_end_langgraph_pipeline` passed).

### Part 4: Structured Eligibility & Alternative Scheme Recovery
- [x] Implement `EligibilityEngine`:
  - Structured criterion evaluation (`SATISFIED`, `FAILED`, `UNKNOWN`).
  - Source chunk evidence linking for each evaluated criterion.
- [x] Implement "Why Not Eligible?" structured report generator.
- [x] Implement `AlternativeSchemeFinder` to suggest matching schemes using confirmed profile.
- [x] Verify: Test eligibility evaluation on known test cases (eligible, ineligible, partial) (`test_structured_eligibility_and_alternatives` passed).

### Part 5: Confidence-Gated Answering & Trust Score
- [x] Implement `TrustScoreCalculator` evaluating:
  - Retrieval relevance, source tier, evidence coverage, rule completeness, conflict penalties.
- [x] Implement 3 response state gates:
  - `HIGH_CONFIDENCE` -> Direct answer + citations.
  - `MEDIUM_CONFIDENCE` -> Targeted clarification.
  - `LOW_CONFIDENCE` -> Safe abstention or secondary retrieval.
- [x] Implement structured confidence audit logging.
- [x] Verify: Test high confidence, ambiguous, and unsupported query responses (`test_trust_score_and_confidence_gating` passed).

### Part 6: Evidence Validation, Claim Audit & Citations
- [x] Implement `EvidencePackBuilder` preserving provenance metadata.
- [x] Implement `ClaimAuditor` post-generation check (verifying amounts, dates, percentages, citations).
- [x] Format rich citation cards (Source, Ministry/Dept, URL, Section).
- [x] Verify: Test claim verification against conflicting and unsupported claims.

### Part 7: Multilingual Equivalence & Voice Mode
- [x] Ensure numbers, ₹ amounts, dates, and citations are preserved across English, Hindi, Bengali, Tamil, Odia, Telugu.
- [x] Verify Voice Mode single-brain execution (1-sentence concise response constraint).
- [x] Verify: Run multilingual test suite comparing outputs for factual equivalence.

### Part 8: Comprehensive Evaluation Harness & RAG Benchmark
- [x] Build automated evaluation harness with representative test cases (facts, eligibility, missing info, prompt injection, abstention).
- [x] Measure Recall@5, Recall@10, MRR, Accuracy, Latency (P50/P95).
- [x] Verify: Run full evaluation suite and report actual benchmark metrics (Recall@5: 100%, MRR: 1.0, P50: 3.36ms).

### Part 9: End-to-End System Verification & Final Polish
- [x] Run end-to-end FastAPI test suite.
- [x] Verify frontend contract compatibility (`/api/chat`, `/api/generate-document`, `/api/session/clear`).
- [x] Finalize `NYAY_SAHAYAKA_ENGINEERING_LOG.md` with complete architecture records and test evidence.
