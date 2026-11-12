"""
Self-Reflection / Hallucination Verifier Node.

Cross-checks the agent's draft response against the retrieved context.
If the draft references legal sections or scheme names not present in
the context, flags `needs_revision = True` for a single correction loop.
"""
import os
from agents.state import AgentState

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None


def reflection_node(state: AgentState) -> AgentState:
    """
    Evaluates draft_response for factual grounding against retrieved_context.
    Uses Gemini at T=0.0 for strict boolean evaluation.
    """
    draft = state.get("draft_response", "")
    context = state.get("retrieved_context", "")
    intent = state.get("intent", "general")

    # Skip reflection for general queries or document drafts (templates, not facts)
    if intent in ("general", "document") or not context:
        return {**state, "critique": None, "needs_revision": False}

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or not ChatGoogleGenerativeAI:
        # Can't verify without LLM, pass through
        return {**state, "critique": None, "needs_revision": False}

    try:
        for model_name in ["gemini-2.5-flash-lite", "gemini-1.5-flash", "gemini-1.5-flash-8b"]:
          try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=0.0,
                max_output_tokens=300,
                max_retries=1,
                timeout=8,
            )

            eval_prompt = f"""You are a fact-checking evaluator for an Indian Legal & Scheme AI system.

TASK: Compare the AI's DRAFT RESPONSE against the SOURCE CONTEXT below and general statutory correctness under Indian Law.

Check for:
1. Does the draft fabricate non-existent laws, hallucinated section numbers, or fictitious schemes?
2. Does the draft state punishments or penalties that contradict the source context?

SOURCE CONTEXT:
{context[:3500]}

DRAFT RESPONSE:
{draft[:3500]}

Respond in this EXACT format:
VERDICT: PASS or FAIL
REASON: one-line explanation (or "None" if PASS)"""

            result = llm.invoke(eval_prompt)
            response_text = result.content.strip()

            if "FAIL" in response_text.upper():
                reason = "Hallucination detected"
                if "REASON:" in response_text:
                    reason = response_text.split("REASON:")[-1].strip()
                return {**state, "critique": reason, "needs_revision": True}
            else:
                return {**state, "critique": None, "needs_revision": False}
          except Exception:
            continue  # try next model in cascade

        return {**state, "critique": None, "needs_revision": False}

    except Exception as e:
        print(f"[Reflection] Evaluation failed: {e}")
        return {**state, "critique": None, "needs_revision": False}


def revision_node(state: AgentState) -> AgentState:
    """
    If the reflection node flagged needs_revision, re-generate the response
    with an explicit instruction to only use the provided context.
    This runs at most once (guard in graph prevents infinite loops).
    """
    query = state.get("sanitized_query", state["query"])
    context = state.get("retrieved_context", "")
    critique = state.get("critique", "Unknown issue")
    language = state.get("language", "en")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or not ChatGoogleGenerativeAI:
        return {**state, "needs_revision": False}

    try:
        for model_name in ["gemini-2.5-flash-lite", "gemini-1.5-flash", "gemini-1.5-flash-8b"]:
          try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=0.0,
                timeout=8,
            )

            correction_prompt = f"""You are an Indian Legal AI assistant. Your previous response was flagged with this issue:
"{critique}"

STRICT RULES:
- ONLY cite sections and facts that appear in the SOURCE CONTEXT below.
- If the context doesn't contain the answer, say "Based on my available database, I could not find specific information on this."
- NEVER invent section numbers, scheme names, or punishments.

SOURCE CONTEXT:
{context[:2000]}

User Query: {query}

Provide a corrected, factually grounded response."""

            result = llm.invoke(correction_prompt)
            return {
                **state,
                "draft_response": result.content,
                "needs_revision": False,
                "critique": None,
            }
          except Exception:
            continue

        return {**state, "needs_revision": False}
    except Exception as e:
        print(f"[Revision] Re-generation failed: {e}")
        return {**state, "needs_revision": False}
