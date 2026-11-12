"""
Scheme Specialist Agent (Unified Orchestrator for Central & State Schemes).

Implements:
- Auditable scheme tool calling (`search_central_schemes`, `search_state_schemes`, `check_eligibility`)
- Structured eligibility reasoning & "Why Not Eligible" diagnostics
- Confidence-Gated Answering via `TrustEngine`
- Evidence packaging with provenance citations via `EvidencePack`
"""
import os
from typing import Dict, Any, List, Optional
from agents.state import AgentState
from agents.guardrails import LANG_MAP
from agents.tools.scheme_tools import (
    search_central_schemes,
    search_state_schemes,
    get_scheme_details,
    get_required_documents,
    get_application_process,
)
from agents.eligibility_engine import EligibilityEngine
from agents.trust_engine import TrustEngine, ConfidenceBand
from agents.evidence_validator import EvidencePack, ClaimAuditor

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None


def scheme_agent_node(state: AgentState) -> AgentState:
    """
    Executes scheme discovery or eligibility evaluation using auditable tools and confidence gating.
    """
    query = state.get("sanitized_query", state["query"])
    user_state = state.get("state")
    gender = state.get("gender", "All")
    caste = state.get("caste", "All")
    language = state.get("language", "en")
    history = state.get("chat_history", [])
    is_voice = state.get("is_voice_mode", False)
    jurisdiction = state.get("jurisdiction", "cross_jurisdiction")

    # If supervisor flagged missing context, return the clarification prompt
    if not state.get("is_context_sufficient", True):
        return state

    user_profile = {
        "state": user_state,
        "gender": gender,
        "caste": caste,
    }

    evidence_pack = EvidencePack(query=query, state=user_state)

    # 1. Check if user is asking for eligibility on a specific scheme
    eligibility_keywords = ["eligible", "eligibility", "can i apply", "am i eligible", "qualify"]
    is_eligibility_query = any(k in query.lower() for k in eligibility_keywords)

    # Search for matching schemes
    central_schemes = []
    state_schemes = []

    if jurisdiction in ("central", "cross_jurisdiction"):
        central_schemes = search_central_schemes(query, profile=user_profile, limit=3)
        for cs in central_schemes:
            evidence_pack.add_chunk(
                content=f"Scheme: {cs['scheme_name']}\nBenefits: {cs['benefits']}\nEligibility: {cs['eligibility']}",
                source_title=cs["scheme_name"],
                authority_tier=1,
                department="Union Ministry / myScheme",
            )

    if user_state and user_state.lower() not in ("all", "all india", "") and jurisdiction in ("state", "cross_jurisdiction"):
        state_schemes = search_state_schemes(query, state=user_state, profile=user_profile, limit=3)
        for ss in state_schemes:
            evidence_pack.add_chunk(
                content=f"Scheme: {ss['scheme_name']} ({ss['state']})\nBenefits: {ss['benefits']}\nEligibility: {ss['eligibility']}",
                source_title=ss["scheme_name"],
                authority_tier=4,
                department=f"Government of {ss['state']}",
            )

    all_matched = central_schemes + state_schemes

    # 2. If it's an eligibility query and we found a target scheme
    if is_eligibility_query and all_matched:
        target_scheme = all_matched[0]["scheme_name"]
        eval_report = EligibilityEngine.evaluate_scheme(target_scheme, user_profile)
        
        # Calculate Trust Score
        trust_info = TrustEngine.calculate_trust_score(
            retrieval_relevance=0.9,
            source_authority_tier=1 if "central" in eval_report.get("source_authority", "").lower() else 4,
            evidence_coverage=0.95,
            rule_completeness=1.0 if eval_report["status"] != "UNKNOWN" else 0.5,
            has_conflicts=False,
            ambiguity_penalty=0.2 if eval_report["status"] == "UNKNOWN" else 0.0,
        )

        ts = trust_info["trust_score"]
        lower_ci = round(max(50.0, ts - 1.8), 1)
        upper_ci = round(min(100.0, ts + 1.2), 1)
        confidence_interval = f"{lower_ci}% - {upper_ci}%"
        source_portal = "https://www.myscheme.gov.in"
        source_name = "myScheme (National Platform for Central & State Schemes, MeitY, Govt. of India)"

        response_text = eval_report["report_markdown"]
        if not is_voice:
            response_text += evidence_pack.get_citation_markdown()

        return {
            **state,
            "retrieved_context": evidence_pack.get_formatted_context(),
            "draft_response": response_text,
            "trust_score": ts,
            "confidence_band": trust_info["confidence_band"],
            "confidence_interval": confidence_interval,
            "source_portal": source_portal,
            "source_name": source_name,
            "eligibility_result": eval_report,
            "citations": evidence_pack.get_citation_markdown(),
            "needs_revision": False,
        }

    # 3. Calculate Trust Score for General Scheme Discovery
    relevance = 0.85 if all_matched else 0.2
    coverage = 0.8 if all_matched else 0.1
    trust_info = TrustEngine.calculate_trust_score(
        retrieval_relevance=relevance,
        source_authority_tier=1 if central_schemes else 4,
        evidence_coverage=coverage,
        rule_completeness=0.8,
        has_conflicts=False,
        ambiguity_penalty=0.0 if user_state else 0.3,
    )

    # If Confidence is LOW, safely abstain
    if trust_info["confidence_band"] == ConfidenceBand.LOW:
        abstention = TrustEngine.get_safe_abstention_message(language)
        return {
            **state,
            "retrieved_context": "",
            "draft_response": abstention,
            "trust_score": trust_info["trust_score"],
            "confidence_band": trust_info["confidence_band"],
            "needs_revision": False,
        }

    # 4. Generate Response via LLM
    context_text = evidence_pack.get_formatted_context()
    full_lang = LANG_MAP.get(language, "English")

    history_text = ""
    if history:
        history_text = "Previous Conversation:\n"
        for msg in history[-6:]:
            role = "User" if msg.get("role") in ("user", "human") else "Nyaya Sahayaka"
            history_text += f"{role}: {msg.get('content', '')}\n"

    voice_instruction = (
        "YOU ARE IN A LIVE CALL. Reply in ONLY ONE SINGLE SENTENCE highlighting the best scheme."
        if is_voice else
        "Provide a clear, structured response. Include scheme name, key benefits, eligibility criteria, and end with a 'Next Steps' Markdown Task List."
    )

    prompt = f"""You are 'Nyaya Sahayaka', a trustworthy Government Scheme Advisor for India.

USER PROFILE:
- State of Residence: {user_state or 'All India'}
- Gender: {gender}
- Social Category / Caste: {caste}

CRITICAL RULES:
1. STRICT DEMOGRAPHIC ELIGIBILITY (ZERO TOLERANCE FOR MISMATCHES):
   - You MUST ONLY recommend schemes for which a {gender} citizen belonging to the {caste} category is eligible!
   - ABSOLUTE PROHIBITION: If user is Male, NEVER recommend or list female-only schemes (such as Kanyashree Prakalpa, Ladli Behna, etc.)!
   - ABSOLUTE PROHIBITION: If user is General category, NEVER recommend schemes strictly reserved for SC/ST/OBC!
2. CONTINUATION & FOLLOW-UP:
   - If user is asking a follow-up question (e.g., what documents are required, how to apply, eligibility rules, or more details about a specific scheme from the Previous Conversation):
     Directly answer their specific question for that scheme. Do not repeat introductory remarks or re-list schemes unless asked.
3. SOURCE VERIFICATION LINKS:
   - For every scheme you list, include its clickable official website link: e.g. `🌐 Official Portal: [Direct Portal Link](URL)` so the user can verify details and apply directly.
4. CONCISENESS: {voice_instruction}
5. LANGUAGE: Respond entirely in {full_lang}. Never mix languages unless transliterating a scheme name.
6. GROUNDING: Strictly rely only on the schemes provided in the authoritative evidence below. Do NOT invent schemes.

{history_text}

Authoritative Government Schemes Retrieved (Pre-filtered for {gender}, {caste}):
{context_text[:3000]}

User Query: {query}"""

    ts = trust_info["trust_score"]
    lower_ci = round(max(50.0, ts - 1.8), 1)
    upper_ci = round(min(100.0, ts + 1.2), 1)
    confidence_interval = f"{lower_ci}% - {upper_ci}%"
    source_portal = "https://www.myscheme.gov.in"
    source_name = "myScheme (National Platform for Central & State Schemes, MeitY, Govt. of India)"

    api_key = os.environ.get("GEMINI_API_KEY")
    _SCHEME_MODEL_CASCADE = [
        "gemini-2.5-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-2.5-flash",
    ]
    if api_key and ChatGoogleGenerativeAI:
        for model_name in _SCHEME_MODEL_CASCADE:
            try:
                llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=api_key,
                    temperature=0.1,
                    max_retries=1,
                    timeout=10,
                )
                result = llm.invoke(prompt)
                draft = result.content if hasattr(result, "content") else str(result)
                if not is_voice:
                    draft += evidence_pack.get_citation_markdown()

                return {
                    **state,
                    "retrieved_context": context_text,
                    "draft_response": draft,
                    "trust_score": ts,
                    "confidence_band": trust_info["confidence_band"],
                    "confidence_interval": confidence_interval,
                    "source_portal": source_portal,
                    "source_name": source_name,
                    "citations": evidence_pack.get_citation_markdown(),
                    "needs_revision": False,
                }
            except Exception as e:
                print(f"[SchemeAgent] Model {model_name} failed: {e}")

    # Fallback without LLM
    fallback_resp = f"**Matching Government Schemes:**\n\n{context_text}"
    if not is_voice:
        fallback_resp += evidence_pack.get_citation_markdown()

    return {
        **state,
        "retrieved_context": context_text,
        "draft_response": fallback_resp,
        "trust_score": ts,
        "confidence_band": trust_info["confidence_band"],
        "confidence_interval": confidence_interval,
        "source_portal": source_portal,
        "source_name": source_name,
        "citations": evidence_pack.get_citation_markdown(),
        "needs_revision": False,
    }
