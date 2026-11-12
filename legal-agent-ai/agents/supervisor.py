"""
Supervisor / Intent & Jurisdiction Router Agent.

Implements Sections 12B, 12D, 17 of the Build Brief:
- Classifies user intent into: scheme | legal | document | general
- Determines jurisdiction: central | state | cross_jurisdiction
- Evaluates Context Sufficiency before delegating to specialist agents
- Detects missing decision-critical variables and triggers clarification-first behavior with options
- Intelligently distinguishes between slot answers/follow-ups and independent new questions
"""
import os
import re
from typing import Optional, Dict, Any, Tuple, List
from agents.state import AgentState
from agents.context_manager import (
    extract_context_from_text,
    check_context_sufficiency_for_query,
    get_missing_legal_context,
)

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None


_DOC_KW = [
    "fir draft", "draft fir", "rti", "draft notice", "complaint draft", "draft",
    "generate document", "write a letter", "legal notice", "application form",
    "draft a legal", "draft an application", "drafting", "draft legal notice"
]

_SCHEME_KW = [
    "scheme", "yojana", "fund", "scholarship", "subsidy", "loan",
    "college", "school", "admission", "help", "support", "kalia",
    "pmay", "pm-kisan", "pm kisan", "benefit", "eligibility", "apply", "pension",
    "chhatravritti", "bpl", "ayushman", "ration", "farmer", "kisan", "student",
    "welfare", "grant", "stipend"
]

_LEGAL_KW = [
    "section", "ipc", "crpc", "bns", "bnss", "penal", "bail", "zamanat",
    "arrest", "punishment", "offence", "offense", "court", "law", "legal",
    "rights", "act", "police", "thana", "daroga", "fir", "zero fir", "sho",
    "theft", "chori", "stolen", "snatch", "snatching", "mobile chori", "car chori",
    "fraud", "cheat", "cheated", "cheating", "scam", "dhokha", "dhokhadhadi", "thag",
    "cyber", "1930", "online fraud", "paise hadap", "upi scam",
    "marpeet", "assault", "beaten", "hit", "injury", "hurt", "chot", "haddi",
    "threat", "dhamki", "threaten", "threatened", "extort", "extortion", "blackmail", "hafta",
    "murder", "hatya", "qatl", "kill", "jaan se", "302", "307",
    "rape", "balatkar", "molest", "chedchad", "sexual harassment", "stalk", "stalking", "posh", "pocso",
    "dowry", "dahej", "cruelty", "498a", "domestic violence", "dv", "gharelu hinsa", "pwdva",
    "landlord", "tenant", "kirayedar", "makan malik", "evict", "eviction", "rent agreement",
    "kabza", "trespass", "land dispute", "property dispute",
    "cheque bounce", "138", "maintenance", "kharcha", "125 crpc",
    "vakil", "lawyer", "advocate", "quash", "false fir", "false case",
    "41a", "154", "156", "438", "439", "420", "376", "379", "323", "506"
]


def _keyword_intent(query: str) -> str:
    q = query.lower().strip()
    # Check for greetings & introductions first
    greeting_pattern = r'^(?:hi|hello|hey|namaste|pranam|good morning|good evening|good afternoon)\b|^(?:my name is|mera naam|i am [a-z]+$)'
    if re.search(greeting_pattern, q):
        return "general"

    for kw in _DOC_KW:
        if kw in q:
            return "document"
    for kw in _LEGAL_KW:
        if kw in q:
            return "legal"
    for kw in _SCHEME_KW:
        if kw in q:
            return "scheme"
    return "general"


def _detect_jurisdiction(query: str, state_val: Optional[str]) -> str:
    """Detects whether the scheme is Central, State, or Cross-Jurisdictional."""
    q = query.lower()
    has_state = bool(state_val and state_val.lower() not in ("all", "all india", "unknown", ""))
    central_markers = ["central", "pm ", "pm-", "pradhan mantri", "national", "all india", "union ministry", "upsc"]
    has_central = any(m in q for m in central_markers)

    if has_state and has_central:
        return "cross_jurisdiction"
    elif has_state:
        return "state"
    elif has_central:
        return "central"

    return "cross_jurisdiction"


def _detect_awaiting_slot_from_agent_message(msg: str) -> Optional[str]:
    """Detects which slot the assistant was waiting for from the previous turn.

    Uses flexible regex patterns that match a variety of natural phrasings an
    agent might use when asking for clarification. The '?' guard ensures we only
    trigger on genuine questions, not descriptive sentences.
    """
    m = msg.lower()
    # ONLY detect a slot if the assistant actually asked the user a question!
    if "?" not in m:
        return None

    # State slot — matches: "what is your state?", "which state?", "tell me your state?",
    # "could you please tell me your state of residence?", "select your state?", etc.
    if re.search(
        r'(?:which|what(?:\s+is(?:\s+your)?)?|tell(?:\s+me(?:\s+your)?)?|select|specify|please\s+(?:tell|share|provide)(?:\s+me)?(?:\s+your)?)\s+state(?:\s+of\s+(?:residence|living|domicile))?',
        m
    ):
        return "state"

    # Income slot — matches: "what is your income?", "tell me your annual income?", etc.
    if re.search(
        r'(?:what(?:\s+is(?:\s+your)?)?|tell(?:\s+me(?:\s+your)?)?|enter(?:\s+your)?|share(?:\s+your)?)\s+(?:annual\s+|family\s+|household\s+)?income',
        m
    ):
        return "income"

    # Category/caste slot
    if re.search(
        r'(?:which|what(?:\s+is(?:\s+your)?)?)\s+(?:caste|category|social\s+category|community)',
        m
    ):
        return "category"

    # Course/degree slot — matches: "what course or degree are you studying?",
    # "which course?", "what is your course?", "what degree are you pursuing?"
    if re.search(
        r'(?:which|what(?:\s+is(?:\s+your)?)?)\s+(?:course|degree|class|stream|programme|program)(?:\s+or\s+(?:course|degree|class|stream))?',
        m
    ):
        return "course"

    # Age slot
    if re.search(r'(?:what(?:\s+is(?:\s+your)?)?|how\s+old)\s+age', m) or "how old are you" in m:
        return "age"

    # Gender slot
    if "your gender" in m or re.search(r'(?:what|which)\s+(?:is\s+your\s+)?gender', m):
        return "gender"

    return None


def _extract_conversation_entities(history: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Extracts schemes, legal sections, and recent context from conversation history.
    """
    schemes = []
    sections = []
    last_agent_msg = ""
    last_user_query = ""

    for msg in reversed(history):
        role = msg.get("role") or msg.get("sender") or ""
        content = msg.get("content", "")
        if role in ("agent", "assistant", "system") and not last_agent_msg:
            last_agent_msg = content
        if role in ("user", "human") and not last_user_query:
            last_user_query = content

    if last_agent_msg:
        # Extract bold scheme/topic titles from numbered lists or bullets
        for m in re.finditer(r'(?:\d+\.|\•|\-)\s*(?:⚖️\s*)?\*\*([^*]+?)\*\*', last_agent_msg):
            title = m.group(1).strip()
            # Ignore structural markdown section headers
            if not any(gh in title.lower() for gh in [
                'applicable', 'legal provision', 'key benefit', 'eligibility',
                'official', 'next step', 'summary', 'important note', 'required document', 'action', 'next steps'
            ]):
                schemes.append(title)

        # Direct 'Scheme: ...'
        for m in re.finditer(r'(?:Scheme|Scheme Name):\s*([^\n\r]+)', last_agent_msg, re.I):
            sname = m.group(1).strip()
            if sname and sname not in schemes:
                schemes.append(sname)

        # Legal sections (IPC / CrPC / BNS / BNSS)
        found_secs = re.findall(
            r'(?:Section\s+)?\d+[A-Za-z]*(?:\(\d+\))?\s*(?:IPC|CrPC|BNS|BNSS)|(?:IPC|CrPC|BNS|BNSS)\s*(?:Section\s+)?\d+[A-Za-z]*(?:\(\d+\))?',
            last_agent_msg, re.I
        )
        sections.extend(found_secs)

    return {
        "schemes": schemes,
        "sections": list(dict.fromkeys(sections)),
        "last_agent_msg": last_agent_msg,
        "last_user_query": last_user_query,
    }


_EXPLICIT_REFERENCE_WORDS = [
    # English pronouns & anaphoric terms
    "this", "that", "these", "those", "it", "its", "them",
    "first", "second", "third", "1st", "2nd", "3rd", "last",
    "former", "latter", "above", "mentioned", "same", "one", "ones",
    # Hindi / Hinglish pronouns & references
    "ye", "yeh", "woh", "wo", "isme", "usme", "iska", "uski", "iske",
    "unka", "unki", "unke", "pehla", "pehli", "pehle", "dusra", "dusri", "dusre",
    "teesra", "teesre", "wahi", "upar", "pehle wale", "dusre wale", "pehle wala", "dusra wala",
]

_FOLLOWUP_ACTIONS = [
    # Documents & application process
    "document", "documents", "kagaz", "certificate", "praman patra",
    "apply", "process", "kaise apply", "form", "portal", "website", "link",
    "eligibility", "patrata", "qualify", "paisa", "rupaye", "amount", "benefit",
    "last date", "deadline", "status", "fee", "fees", "cost", "free", "subsidy",
    # Legal follow-ups
    "punishment", "saza", "bail", "zamanat", "arrest", "fir", "police", "court",
    "remedy", "what next", "fir kya", "kya kare", "kya hoga", "can i", "steps",
    "procedure", "where to", "explain", "detail", "details", "aur batao", "tell me more"
]


def _is_slot_answer_or_continuation(
    raw_query: str,
    awaiting_slot: Optional[str],
    entities: Dict[str, Any],
    history: List[Dict[str, str]]
) -> bool:
    """
    Returns True if current user message is:
    1. A short slot-filling answer to an assistant question.
    2. An anaphoric follow-up question referencing previous schemes, laws, or advice.
    3. A follow-up action (e.g. documents, how to apply, bail, punishment).
    """
    if not history:
        return False

    q = raw_query.strip().lower()
    words = q.split()

    # 0. Check for greetings or self-introductions (e.g. "hi", "hello", "hi my name is madan")
    # Greetings are fresh general inquiries, NEVER slot answers or scheme continuations!
    greeting_pattern = r'^(?:hi|hello|hey|namaste|pranam|good morning|good evening|good afternoon)\b|^(?:my name is|mera naam|i am [a-z]+$)'
    if re.search(greeting_pattern, q):
        return False

    # 1. Check direct slot answers when agent explicitly asked for one
    if awaiting_slot and len(words) <= 6:
        # If user asks a legal question or mentions legal keywords, it is an explicit topic change, NOT a slot answer!
        has_legal = any(k in q for k in ["ipc", "crpc", "bns", "bnss", "section", "fir", "police", "bail", "arrest", "court", "murder", "theft", "fraud", "scam", "cheat"])
        if not has_legal and not any(q.startswith(qs) for qs in ["what is", "tell me about", "define", "explain"]):
            return True

    # 2. Check for explicit reference / anaphoric words (e.g. "for this", "first one", "isme", "what about it")
    has_reference = any(re.search(r'\b' + re.escape(w) + r'\b', q) for w in _EXPLICIT_REFERENCE_WORDS)

    # 3. Check for specific new statute in current query (e.g. "What is IPC Section 420?")
    # If the user explicitly asks about a brand new section without referencing previous context, treat as fresh
    has_specific_new_statute = bool(re.search(r'\b(?:ipc|crpc|bns|bnss)\s*(?:section)?\s*\d+', q))
    if has_specific_new_statute and not has_reference:
        return False

    if has_reference:
        return True

    # 4. Check for follow-up actions (e.g. "what are the documents?", "how to apply?", "is it bailable?")
    has_action = any(act in q for act in _FOLLOWUP_ACTIONS)
    if has_action:
        return True

    # 5. Short follow-ups like "kya kare?", "fir?", "next?"
    if len(words) <= 4 and any(w in q for w in ["kya", "kaise", "what", "how", "next", "then", "aur", "more"]):
        return True

    return False


def supervisor_node(state: AgentState) -> AgentState:
    """
    Supervisor Router with Conversational State & Slot Tracking:
    1. Distinguishes fresh queries from contextual follow-ups and slot answers.
    2. Contextualizes follow-up queries with target schemes and legal provisions from conversation history.
    3. Prevents query repetition and topic entrapment across multiple questions.
    4. Fills slot values and resolves location entities (e.g. Kolkata -> West Bengal).
    5. Evaluates Context Sufficiency and routes to the appropriate specialist agent.
    """
    raw_query = state.get("sanitized_query", state["query"]).strip()
    user_state = state.get("state")
    history = state.get("chat_history", [])

    if state.get("error"):
        return state

    # 1. Identify previous conversation state & extract entities
    entities = _extract_conversation_entities(history)
    last_agent_msg = entities["last_agent_msg"]
    last_user_query = entities["last_user_query"]
    awaiting_slot = state.get("awaiting_slot")

    if not awaiting_slot and last_agent_msg:
        awaiting_slot = _detect_awaiting_slot_from_agent_message(last_agent_msg)

    # 2. Determine raw intent of CURRENT user message
    raw_intent = _keyword_intent(raw_query)

    # 3. Decide if this is a slot answer / follow-up OR a brand new question
    is_continuation = _is_slot_answer_or_continuation(raw_query, awaiting_slot, entities, history)

    target_entity = ""
    if is_continuation and last_user_query:
        # User is answering a clarification or following up on previous topic
        # Determine the underlying thread intent from history
        thread_intent = "general"
        for msg in reversed(history):
            if msg.get("role") in ("user", "human"):
                ti = _keyword_intent(msg.get("content", ""))
                if ti != "general":
                    thread_intent = ti
                    break

        # Preserve thread intent for follow-up questions
        # E.g. "what documents are required?" for a scheme stays 'scheme', not hijacked by 'document' or 'general'
        if thread_intent != "general":
            active_intent = thread_intent
        elif raw_intent != "general":
            active_intent = raw_intent
        else:
            active_intent = "general"

        # Resolve target entity (e.g. first scheme, second scheme, or legal section)
        q_lower = raw_query.lower()
        if any(w in q_lower for w in ["first", "1st", "pehla", "pehli", "option 1"]):
            if entities["schemes"]:
                target_entity = entities["schemes"][0]
        elif any(w in q_lower for w in ["second", "2nd", "dusra", "dusri", "option 2"]):
            if len(entities["schemes"]) > 1:
                target_entity = entities["schemes"][1]
        elif any(w in q_lower for w in ["third", "3rd", "teesra", "option 3"]):
            if len(entities["schemes"]) > 2:
                target_entity = entities["schemes"][2]

        if not target_entity:
            if entities["schemes"]:
                target_entity = entities["schemes"][0]
            elif entities["sections"]:
                target_entity = " / ".join(entities["sections"][:2])

        if awaiting_slot:
            active_query = f"{last_user_query} (User clarified {awaiting_slot}: {raw_query})"
        elif target_entity:
            active_query = f"{raw_query} regarding {target_entity}"
        else:
            active_query = f"{last_user_query} (Follow-up: {raw_query})"

        original_user_query = last_user_query
    else:
        # User has asked a NEW, independent question!
        active_intent = raw_intent
        active_query = raw_query
        original_user_query = raw_query
        awaiting_slot = None

    # 4. Context & Slot Extraction
    extracted_ctx = extract_context_from_text(raw_query, awaiting_slot=awaiting_slot)
    for msg in history:
        role = msg.get("role") or msg.get("sender") or ""
        content = msg.get("content", "")
        if role in ("user", "human") and content:
            extracted_ctx = extract_context_from_text(content, extracted_ctx)

    # Re-apply current query with slot context
    extracted_ctx = extract_context_from_text(raw_query, extracted_ctx, awaiting_slot=awaiting_slot)

    if user_state and user_state != "All":
        extracted_ctx.set_confirmed("state", user_state)

    detected_state = extracted_ctx.get_value("state") or user_state
    gender = state.get("gender") if state.get("gender") != "All" else extracted_ctx.get_value("gender", "All")
    caste = state.get("caste") if state.get("caste") != "All" else extracted_ctx.get_value("caste", "All")

    # 5. Determine Jurisdiction if scheme
    jurisdiction = _detect_jurisdiction(active_query, detected_state) if active_intent == "scheme" else "general"

    # 6. Context Sufficiency Check (Clarification-First)
    is_sufficient = True
    clarification_msg = None
    options = None
    next_awaiting_slot = None
    missing_vars = []

    if active_intent == "scheme":
        is_sufficient, clarification_msg, options, next_awaiting_slot = check_context_sufficiency_for_query(
            query=active_query,
            context=extracted_ctx,
            target_scheme_name=target_entity if target_entity else None,
        )
    elif active_intent == "legal":
        # Check missing legal context (e.g. State for police jurisdiction, FIR status, Evidence)
        missing_vars = get_missing_legal_context(active_query, extracted_ctx)
        # Note: For legal queries, we do NOT block with an empty answer.
        # We allow ipc_agent to run, and ipc_agent presents the statutory overview AND asks clarifying questions!
        is_sufficient = True

    collected_slots = extracted_ctx.to_profile_dict()

    print(
        f"[Supervisor] ActiveIntent={active_intent} | IsContinuation={is_continuation} | "
        f"AwaitingSlot={awaiting_slot} -> NextSlot={next_awaiting_slot} | "
        f"ResolvedState={detected_state} | City={extracted_ctx.get_value('city')} | "
        f"Jurisdiction={jurisdiction} | Sufficient={is_sufficient}"
    )

    if not is_sufficient and clarification_msg:
        opts_text = ""
        if options:
            opts_text = "\n\n" + "\n".join([f"- **{opt}**" for opt in options])
        clarification_response = f"{clarification_msg}{opts_text}"

        return {
            **state,
            "sanitized_query": active_query,
            "original_user_query": original_user_query,
            "intent": active_intent,
            "jurisdiction": jurisdiction,
            "state": detected_state,
            "gender": gender,
            "caste": caste,
            "collected_slots": collected_slots,
            "awaiting_slot": next_awaiting_slot,
            "is_context_sufficient": False,
            "draft_response": clarification_response,
            "clarification_options": options,
            "needs_revision": False,
            "missing_variables": missing_vars,
        }

    return {
        **state,
        "sanitized_query": active_query,
        "original_user_query": original_user_query,
        "intent": active_intent,
        "jurisdiction": jurisdiction,
        "state": detected_state,
        "gender": gender,
        "caste": caste,
        "collected_slots": collected_slots,
        "awaiting_slot": None,
        "is_context_sufficient": True,
        "clarification_options": None,
        "missing_variables": missing_vars,
    }
