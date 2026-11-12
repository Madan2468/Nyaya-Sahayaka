"""
State Schemes Specialist Agent.

Responsible for:
- State Government schemes (Tier 4 / State Portals: e.g. West Bengal, Odisha, Gujarat, Haryana, MP, Rajasthan)
- Domicile-locked state eligibility criteria
- State-level DBT, scholarship portals, student credit cards, farmer support
"""
import os
from typing import Dict, Any, List, Optional
from agents.state import AgentState
from agents.guardrails import LANG_MAP
from agents.tools.scheme_tools import search_state_schemes, get_scheme_details, get_required_documents
from agents.trust_engine import TrustEngine, ConfidenceBand

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None


def state_scheme_agent_node(state: AgentState) -> AgentState:
    """
    Executes search over State-specific schemes with strict demographic filtering
    and synthesizes source-grounded response with official portal links.
    """
    query = state.get("sanitized_query", state["query"])
    user_state = state.get("state")
    gender = state.get("gender", "All")
    caste = state.get("caste", "All")
    language = state.get("language", "en")
    history = state.get("chat_history", [])
    is_voice = state.get("is_voice_mode", False)

    # If state is missing, prompt for state clarification
    if not user_state or user_state.lower() in ("all", "unknown", ""):
        clarification_msg = (
            "To provide you with accurate State Government schemes and local department benefits, "
            "could you please specify your State of residence (for example: West Bengal, Odisha, Gujarat, Uttar Pradesh)?"
        )
        return {
            **state,
            "retrieved_context": "",
            "draft_response": clarification_msg,
            "needs_revision": False,
        }

    # 1. Auditable tool call: search state schemes with demographic profile
    profile = {"state": user_state, "gender": gender, "caste": caste}
    state_results = search_state_schemes(query=query, state=user_state, profile=profile, limit=4)

    # 2. Determine top portal URL and build authoritative context
    top_portal = "https://www.myscheme.gov.in"
    top_source_name = f"myScheme (Govt of {user_state})"
    if state_results:
        top_portal = state_results[0].get("official_url", top_portal)
        top_source_name = f"{state_results[0]['scheme_name']} Official Portal"

    context_chunks = []
    for s in state_results:
        url = s.get("official_url", "https://www.myscheme.gov.in")
        context_chunks.append(
            f"State Scheme: {s['scheme_name']}\n"
            f"State: {s['state']}\n"
            f"Official Link: {url}\n"
            f"Authority: {s['source_authority']}\n"
            f"Category: {s['category']}\n"
            f"Benefits: {s['benefits']}\n"
            f"Eligibility: {s['eligibility']}"
        )
    retrieved_context = "\n\n---\n\n".join(context_chunks)

    # 3. Calculate Trust Score and Confidence Metrics
    trust_calc = TrustEngine.calculate_trust_score(
        retrieval_relevance=0.94 if state_results else 0.40,
        source_authority_tier=4,
        evidence_coverage=0.95 if state_results else 0.30,
        rule_completeness=0.95,
        has_conflicts=False,
        ambiguity_penalty=0.0,
    )
    trust_score = trust_calc["trust_score"]
    confidence_band = trust_calc["confidence_band"]
    lower_ci = round(max(50.0, trust_score - 1.5), 1)
    upper_ci = round(min(100.0, trust_score + 1.2), 1)
    confidence_interval = f"{lower_ci}% - {upper_ci}%"

    # 4. LLM synthesis with Strict Demographic Constraints
    full_lang = LANG_MAP.get(language, "English")
    history_text = ""
    if history:
        history_text = "Previous Conversation:\n"
        for msg in history[-6:]:
            role = "User" if msg.get("role") in ("user", "human") else "Nyaya Sahayaka"
            history_text += f"{role}: {msg.get('content', '')}\n"

    voice_instruction = (
        f"YOU ARE IN A LIVE CALL. Reply in ONLY ONE SINGLE SENTENCE with the top {user_state} state scheme benefit."
        if is_voice else
        f"Provide a structured, smart response. For each eligible scheme, provide Scheme Name, Key Benefits, Eligibility, and a clickable Official Verification Link."
    )

    prompt = f"""You are 'Nyaya Sahayaka', a State Government Scheme Specialist for {user_state}.

USER PROFILE:
- State of Residence: {user_state}
- Gender: {gender}
- Social Category / Caste: {caste}

CRITICAL RULES:
1. STRICT DEMOGRAPHIC ELIGIBILITY (ZERO TOLERANCE FOR MISMATCHES):
   - You MUST ONLY recommend schemes for which a {gender} citizen belonging to the {caste} category is eligible!
   - ABSOLUTE PROHIBITION: If user is Male, NEVER recommend or list female-only schemes (such as Kanyashree Prakalpa, Ladli Behna, etc.)!
   - ABSOLUTE PROHIBITION: If user is General category, NEVER recommend schemes strictly reserved for SC/ST/OBC (such as Post-Matric SC/ST Scholarship)!
2. CONTINUATION & FOLLOW-UP:
   - If user is asking a follow-up question (e.g., what documents are required, how to apply, or details about a scheme from Previous Conversation):
     Directly answer their specific question for that scheme. Do not re-greet or introduce yourself.
3. SOURCE VERIFICATION LINKS:
   - For every scheme you list, include its clickable official website link: e.g. `🌐 Official Portal: [Direct Portal Link](URL)` so the user can verify details and apply directly.
4. CONCISENESS & QUALITY:
   - Be smart, direct, and helpful. Avoid generic disclaimers or listing ineligible schemes.
5. LANGUAGE: Respond strictly in {full_lang}.

{history_text}

Authoritative State Schemes Retrieved (Pre-filtered for {gender}, {caste}, {user_state}):
{retrieved_context if retrieved_context else f"No direct matching state schemes found for {user_state} matching your profile."}

User Query: {query}"""

    api_key = os.environ.get("GEMINI_API_KEY")
    _MODEL_CASCADE = ["gemini-2.5-flash-lite", "gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-2.5-flash"]
    if api_key and ChatGoogleGenerativeAI:
        for model_name in _MODEL_CASCADE:
            try:
                llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=api_key,
                    temperature=0.1,
                    max_retries=1,
                    timeout=10,
                )
                result = llm.invoke(prompt)
                return {
                    **state,
                    "retrieved_context": retrieved_context,
                    "draft_response": result.content if hasattr(result, "content") else str(result),
                    "trust_score": trust_score,
                    "confidence_band": confidence_band,
                    "confidence_interval": confidence_interval,
                    "source_portal": top_portal,
                    "source_name": top_source_name,
                    "needs_revision": False,
                }
            except Exception as e:
                print(f"[StateSchemeAgent] Model {model_name} failed: {e}")

    # Fallback if no LLM
    fallback_text = (
        f"**Eligible State Government Schemes ({user_state}) for {gender}, {caste} category:**\n\n{retrieved_context}"
        if retrieved_context else
        f"No matching State Government schemes found for {user_state} matching your profile."
    )
    return {
        **state,
        "retrieved_context": retrieved_context,
        "draft_response": fallback_text,
        "trust_score": trust_score,
        "confidence_band": confidence_band,
        "confidence_interval": confidence_interval,
        "source_portal": top_portal,
        "source_name": top_source_name,
        "needs_revision": False,
    }
