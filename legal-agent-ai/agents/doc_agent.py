"""
Legal Document Drafter Agent.

Handles generation of FIR drafts, RTI applications, legal notices, and complaint letters.
Includes a Human-in-the-Loop checkpoint for high-stakes documents.
"""
import os
from agents.state import AgentState
from agents.guardrails import LANG_MAP

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None


def doc_agent_node(state: AgentState) -> AgentState:
    """
    Drafts legal documents and flags them for human confirmation
    before finalization.
    """
    query = state.get("sanitized_query", state["query"])
    language = state.get("language", "en")
    history = state.get("chat_history", [])
    full_lang = LANG_MAP.get(language, "English")

    # Detect document type from query
    q_lower = query.lower()
    if "fir" in q_lower:
        doc_type = "First Information Report (FIR)"
    elif "rti" in q_lower:
        doc_type = "RTI Application"
    elif "notice" in q_lower:
        doc_type = "Legal Notice"
    elif "complaint" in q_lower:
        doc_type = "Formal Complaint Letter"
    else:
        doc_type = "Legal Document"

    history_text = ""
    if history:
        history_text = "Previous Conversation:\n"
        for msg in history[-4:]:
            role = "User" if msg.get("role") == "user" else "Agent"
            history_text += f"{role}: {msg.get('content', '')}\n"

    prompt = f"""You are 'Nyaya Sahayaka', a professional Indian Legal Document Drafting Assistant.

TASK: Draft a {doc_type} based on the user's description below.

INSTRUCTIONS:
1. Use the standard Indian legal format for a {doc_type}.
2. Include all necessary fields: Date, To (authority), From (complainant), Subject, Body, and Signature block.
3. Use clear, formal language appropriate for a {doc_type}.
4. Mark any field where user information is needed with [FILL_IN: description] placeholders.
5. Respond entirely in {full_lang}.
6. After the draft, add a note: "⚠️ Please review all details carefully before submission. This is an AI-generated draft."

{history_text}

User Request: {query}"""

    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key and ChatGoogleGenerativeAI:
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=api_key,
                temperature=0.1,  # Low temp for formal document tone
                max_retries=1,
                timeout=10,
            )
            result = llm.invoke(prompt)
            return {
                **state,
                "retrieved_context": "",
                "draft_response": result.content,
                "requires_human_confirmation": True,  # Flag for HITL
                "needs_revision": False,
            }
        except Exception as e:
            print(f"[DocAgent] Primary model failed: {e}")
            try:
                fallback = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash-lite",
                    google_api_key=api_key,
                    temperature=0.1,
                    max_retries=1,
                    timeout=10,
                )
                result = fallback.invoke(prompt)
                return {
                    **state,
                    "retrieved_context": "",
                    "draft_response": result.content,
                    "requires_human_confirmation": True,
                    "needs_revision": False,
                }
            except Exception as fallback_e:
                print(f"[DocAgent] Fallback also failed: {fallback_e}")

    return {
        **state,
        "retrieved_context": "",
        "draft_response": (
            f"I can help you draft a {doc_type}, but the AI engine is currently unavailable. "
            "Please try again shortly."
        ),
        "requires_human_confirmation": False,
        "needs_revision": False,
    }
