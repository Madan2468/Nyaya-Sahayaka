"""
LangGraph State Machine for Nyaya Sahayaka Multi-Agent Pipeline.

Topology:
  ┌───────────────┐
  │ input_guard   │
  └──────┬────────┘
         ▼
  ┌───────────────┐
  │ supervisor    │ (routes by intent & jurisdiction + context sufficiency check)
  └──────┬────────┘
         ├── context missing  → output_guard (asks structured clarification)
         ├── central scheme   → central_scheme_agent
         ├── state scheme     → state_scheme_agent
         ├── cross scheme     → scheme_agent
         ├── legal            → ipc_agent
         ├── document         → doc_agent
         └── general          → general_agent
                ▼
  ┌───────────────┐
  │ reflection    │ (claim audit / hallucination check)
  └──────┬────────┘
         ├── needs_revision=True → revision (max 1x) → reflection
         └── needs_revision=False
                ▼
  ┌───────────────┐
  │ output_guard  │ (disclaimer + language + citations)
  └──────┬────────┘
         ▼
        END
"""
import os
import re
from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.guardrails import input_guardrail, output_guardrail, LANG_MAP
from agents.supervisor import supervisor_node
from agents.scheme_agent import scheme_agent_node
from agents.central_scheme_agent import central_scheme_agent_node
from agents.state_scheme_agent import state_scheme_agent_node
from agents.ipc_agent import ipc_agent_node
from agents.doc_agent import doc_agent_node
from agents.reflection import reflection_node, revision_node

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None


def general_agent_node(state: AgentState) -> AgentState:
    query = state.get("sanitized_query", state["query"])
    language = state.get("language", "en")
    full_lang = LANG_MAP.get(language, "English")
    history = state.get("chat_history", [])
    is_voice = state.get("is_voice_mode", False)

    # Detect greeting / name introduction in CURRENT query
    greeting_pattern = r'^(?:hi|hello|hey|namaste|pranam|good morning|good evening|good afternoon)\b|^(?:my name is|mera naam|i am [a-z]+$)'
    is_greeting = bool(re.search(greeting_pattern, query.strip().lower()))

    # Extract name from current query first, then fall back to searching in conversation history
    name_match = re.search(r'(?:my name is|i am|mera naam(?: hai)?|call me)\s+([A-Za-z]+)', query, re.I)
    user_name = name_match.group(1).title() if name_match else ""

    # If name not in current query, search chat history for it
    if not user_name and history:
        for msg in history:
            if msg.get("role") in ("user", "human"):
                hist_name_match = re.search(
                    r'(?:my name is|i am|mera naam(?: hai)?|call me)\s+([A-Za-z]+)',
                    msg.get("content", ""), re.I
                )
                if hist_name_match:
                    user_name = hist_name_match.group(1).title()
                    break  # Use the first (earliest) name introduced

    name_greeting = f"Namaste {user_name}!" if user_name else "Namaste!"

    # Build history text for LLM context (last 6 turns)
    history_text = ""
    if history:
        history_text = "Previous Conversation:\n"
        for msg in history[-6:]:
            role = "User" if msg.get("role") in ("user", "human") else "Agent"
            history_text += f"{role}: {msg.get('content', '')}\n"

    voice_instr = "Reply in ONE sentence." if is_voice else "Be concise (max 3 sentences)."

    if is_greeting:
        prompt = f"""You are 'Nyaya Sahayaka', a friendly and knowledgeable Indian Legal & Government Scheme AI.
The user is saying: "{query}".
Greet them warmly (use "{name_greeting}"). Welcome them to Nyaya Sahayaka.
Clearly and helpfully tell them what you can assist with:
1. 🏛️ Government Schemes & Subsidies (Central & State eligibility check)
2. ⚖️ Legal Rights & Statutory Provisions (IPC/BNS & CrPC/BNSS)
3. 📄 Drafting Legal Documents (FIR, RTI, Legal Notices)

Ask how you can assist them today.
{voice_instr}
Respond in {full_lang}."""
    elif history:
        # Pass full conversation context so LLM can answer memory/context questions
        # e.g. "do you remember my name?" → LLM sees earlier "my name is Madan" in history
        prompt = f"""You are 'Nyaya Sahayaka', a friendly and knowledgeable Indian Legal & Government Scheme AI.
You are continuing a conversation with the user.
{f"The user's name is {user_name}." if user_name else ""}
Answer the user's latest message directly based on the conversation history.
If the user asks whether you remember something (like their name), confirm it warmly using the information from the conversation.
Do NOT start with generic greetings like "Hello!" or "Namaste!" — go straight to the answer.

{voice_instr}
Respond in {full_lang}.

{history_text}
User: {query}"""
    else:
        prompt = f"""You are 'Nyaya Sahayaka', a friendly Indian Legal & Government Scheme AI.
The user's message is a greeting or general inquiry.
Respond helpfully and suggest what you can assist with:
- Government scheme discovery & eligibility (Central & State)
- Legal rights & IPC / BNS sections
- Drafting FIRs, RTI applications, legal notices

{voice_instr}
Respond in {full_lang}.

User: {query}"""

    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key and ChatGoogleGenerativeAI:
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-lite",
                google_api_key=api_key,
                temperature=0.3,
                timeout=12,
            )
            result = llm.invoke(prompt)
            return {
                **state,
                "retrieved_context": "",
                "draft_response": result.content,
                "needs_revision": False,
            }
        except Exception as e:
            print(f"[GeneralAgent] LLM error: {e}")

    # --- Offline / LLM-unavailable fallback ---
    if is_greeting:
        fallback_text = (
            f"{name_greeting} Welcome to Nyaya Sahayaka.\n\n"
            "I can assist you with:\n"
            "• Government scheme discovery & eligibility (Central & State)\n"
            "• Legal rights & IPC/BNS sections\n"
            "• Drafting FIRs, RTI applications, and legal notices\n\n"
            "How can I assist you today?"
        )
    elif history and user_name:
        fallback_text = (
            f"Yes! I remember — your name is **{user_name}**. "
            "How can I assist you further today?"
        )
    elif history:
        fallback_text = (
            "I'm here to assist you. Could you please specify which scheme, law, or document you'd like more details about?"
        )
    else:
        fallback_text = (
            "Namaste! Welcome to Nyaya Sahayaka. How can I assist you today?"
        )

    return {
        **state,
        "retrieved_context": "",
        "draft_response": fallback_text,
        "needs_revision": False,
    }


def route_by_intent_and_jurisdiction(state: AgentState) -> str:
    """Routes supervisor output to specialist agents or clarification path."""
    if state.get("error"):
        return "output_guard"

    # If context is not sufficient, short-circuit directly to output_guard to ask clarification
    if not state.get("is_context_sufficient", True):
        return "output_guard"

    intent = state.get("intent", "general")
    jurisdiction = state.get("jurisdiction", "cross_jurisdiction")

    if intent == "scheme":
        if jurisdiction == "central":
            return "central_scheme_agent"
        elif jurisdiction == "state":
            return "state_scheme_agent"
        else:
            return "scheme_agent"

    return {
        "legal": "ipc_agent",
        "document": "doc_agent",
        "general": "general_agent",
    }.get(intent, "general_agent")


def route_after_reflection(state: AgentState) -> str:
    """After reflection, either revise or proceed to output guardrails."""
    if state.get("needs_revision"):
        return "revision"
    return "output_guard"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("input_guard", input_guardrail)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("scheme_agent", scheme_agent_node)
    graph.add_node("central_scheme_agent", central_scheme_agent_node)
    graph.add_node("state_scheme_agent", state_scheme_agent_node)
    graph.add_node("ipc_agent", ipc_agent_node)
    graph.add_node("doc_agent", doc_agent_node)
    graph.add_node("general_agent", general_agent_node)
    graph.add_node("reflection", reflection_node)
    graph.add_node("revision", revision_node)
    graph.add_node("output_guard", output_guardrail)

    # Entry point
    graph.set_entry_point("input_guard")

    # Input guard -> Supervisor
    graph.add_edge("input_guard", "supervisor")

    # Supervisor conditional routing
    graph.add_conditional_edges(
        "supervisor",
        route_by_intent_and_jurisdiction,
        {
            "scheme_agent": "scheme_agent",
            "central_scheme_agent": "central_scheme_agent",
            "state_scheme_agent": "state_scheme_agent",
            "ipc_agent": "ipc_agent",
            "doc_agent": "doc_agent",
            "general_agent": "general_agent",
            "output_guard": "output_guard",  # For clarification or errors
        },
    )

    # All specialist agents flow into reflection
    graph.add_edge("scheme_agent", "reflection")
    graph.add_edge("central_scheme_agent", "reflection")
    graph.add_edge("state_scheme_agent", "reflection")
    graph.add_edge("ipc_agent", "reflection")
    graph.add_edge("doc_agent", "reflection")
    graph.add_edge("general_agent", "reflection")

    # Reflection -> conditional revision or output guard
    graph.add_conditional_edges(
        "reflection",
        route_after_reflection,
        {
            "revision": "revision",
            "output_guard": "output_guard",
        },
    )

    # After revision, go to output guard (max 1 loop)
    graph.add_edge("revision", "output_guard")

    # Output guard -> END
    graph.add_edge("output_guard", END)

    return graph


def get_compiled_graph():
    """Returns a compiled, ready-to-invoke LangGraph."""
    graph = build_graph()
    return graph.compile()
