# Nyay Sahayaka — Comprehensive System Requirements

## 1. System Mission & Core Principles
Nyay Sahayaka is an agentic, conversational, multilingual government scheme advisor for Indian citizens. It prioritizes authoritative government data (Tier 1: myScheme, Tier 2: Union Ministries, Tier 3: Official Guidelines/PDFs, Tier 4: State Portals, Tier 5: data.gov.in / OGD). It never invents, guesses, or fabricates scheme eligibility, amounts, deadlines, or requirements.

---

## 2. Core Functional Requirements

### 2.1 Clarification-First & Context Sufficiency
- **Requirement**: Before generating any scheme recommendation or eligibility judgment, the system must inspect context sufficiency.
- **Fact Classification**: Variables must be tracked with certainty states: `USER_CONFIRMED`, `INFERRED`, `UNKNOWN`.
- **Targeted Clarification**: When decision-critical variables (e.g. State, Age, Occupation, Income, Education Level, Category) are missing, the system must ask structured, minimal questions (with selectable options A/B/C/D where practical) rather than guessing.

### 2.2 Multi-Agent Architecture (Central vs State Scheme Agents)
- **Requirement**: Separate and coordinate specialized agents:
  - **Supervisor / Scheme Router**: Analyzes query, intent, jurisdiction, and delegates.
  - **Central Schemes Agent**: Union Ministry schemes, national portals, all-India guidelines.
  - **State Schemes Agent**: State-specific welfare schemes, state department portals, domicile-locked criteria.
  - **General / Fallback Agent**: Handles greetings and general queries.
- **Parallel Dispatch & Merging**: Dispatches both Central and State agents when queries span both, followed by deduplication, conflict detection, and evidence merging.

### 2.3 Auditable Scheme Tool Orchestration
- **Requirement**: Explicit, typed, testable tools callable by agents:
  - `search_central_schemes(query, profile, category)`
  - `search_state_schemes(query, state, profile, category)`
  - `get_scheme_details(scheme_id)`
  - `check_eligibility(scheme_id, profile)`
  - `identify_missing_information(context, scheme)`
  - `get_required_documents(scheme_id)`
  - `get_application_process(scheme_id)`
  - `find_alternative_schemes(profile, failed_scheme)`
  - `retrieve_source_evidence(query, filters)`
  - `check_source_freshness_and_conflicts(scheme_id, sources)`

### 2.4 Structured Eligibility Reasoning Engine
- **Requirement**: Criterion-by-criterion evaluation with structured statuses:
  - `SATISFIED`: Explicit evidence proves the condition is met.
  - `FAILED`: Evidence demonstrates disqualification.
  - `UNKNOWN`: Missing user information or missing source criteria.
- **"Why Not Eligible?" Explanation**: Clear, source-grounded reasoning explaining why a specific criterion failed.
- **Alternative Recovery Flow**: Reuses confirmed profile parameters to find related schemes when the user is ineligible for their requested scheme.

### 2.5 Confidence-Gated Answering & Trust Scoring
- **Requirement**: Calculate a deterministic Trust Score from measurable signals:
  - Retrieval relevance score
  - Source authority tier weight
  - Evidence claim coverage
  - Rule completeness
  - Contradiction / Conflict penalty
  - Ambiguity penalty
- **3 Response Bands**:
  1. **HIGH CONFIDENCE**: Answer directly + cite sources + explain eligibility reasoning.
  2. **MEDIUM / UNCERTAIN**: Ask targeted option-based clarification to resolve ambiguity.
  3. **LOW / UNSUPPORTED**: Retrieve more evidence or safely abstain ("I couldn't verify this from available official sources").

### 2.6 Pre-Generation Evidence Validation & Post-Generation Claim Audit
- **Requirement**:
  - Build pre-generation evidence packs with strict provenance metadata (URL, department, scheme ID, version, section, page).
  - Post-generation claim audit: Cross-check draft claims against evidence chunks for exact amounts, dates, percentages, and criteria. Remove unsupported statements before presentation.

### 2.7 Multilingual Equivalence & Voice Support
- **Requirement**: Equivalence across English, Hindi, Bengali, Tamil, Odia, Telugu.
- Numbers, dates, ₹ amounts, and statutory requirements must remain identical regardless of language.
- Shared single-brain architecture for text and voice interactions (concise 1-sentence mode for live voice).

### 2.8 Evaluation Harness & Benchmarks
- **Requirement**: Automated test suite measuring:
  - Retrieval: Recall@5, Recall@10, MRR (Vector vs Hybrid vs Hybrid+Reranker).
  - Agent Behavior: Answering accuracy, clarification precision, abstention on unsupported queries, prompt injection resilience, latency (P50/P95).
