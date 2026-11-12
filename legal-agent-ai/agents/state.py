"""
Shared LangGraph state definition for the Nyaya Sahayaka multi-agent pipeline.
All agents read from and write to this typed state dictionary.
"""
from typing import TypedDict, Optional, List, Dict, Any, Literal

class AgentState(TypedDict):
    """Immutable state that flows through every node in the LangGraph."""

    # ─── User Input ──────────────────────────────────────────────
    query: str                                  # Raw user message
    language: str                               # ISO code: en, hi, bn, ta, te, or
    state: Optional[str]                        # Indian state (e.g. "Odisha")
    gender: Optional[str]                       # "Male" / "Female" / "All"
    caste: Optional[str]                        # "General" / "OBC" / "SC" / "ST" / "All"
    is_voice_mode: bool                         # If True, response must be single sentence
    chat_history: List[Dict[str, str]]          # Sliding window from Redis

    # ─── Router / Supervisor ─────────────────────────────────────
    intent: Literal["scheme", "legal", "document", "general"]
    jurisdiction: Optional[Literal["central", "state", "cross_jurisdiction", "general"]]
    sanitized_query: str                        # After input guardrails

    # ─── Conversational Memory & Slot Tracking ───────────────────
    awaiting_slot: Optional[str]                # e.g. "state", "income", "age", "category", "course"
    collected_slots: Optional[Dict[str, Any]]   # Structured dictionary of extracted demographic variables
    original_user_query: Optional[str]          # Original root query initiating the task

    # ─── Context Sufficiency & Clarification ─────────────────────
    is_context_sufficient: bool                 # False → prompt clarification
    missing_variables: Optional[List[str]]      # e.g. ["state", "annual_income"]
    clarification_options: Optional[List[str]]  # Options A/B/C/D for structured response

    # ─── RAG Retrieval & Tool Evidence ───────────────────────────
    retrieved_context: str                      # Search & tool results
    retrieval_metadata: Optional[List[Dict]]    # Source, section, score info
    citations: Optional[str]                    # Formatted government source cards

    # ─── Eligibility Reasoning ───────────────────────────────────
    eligibility_result: Optional[Dict[str, Any]] # Structured criterion evaluations

    # ─── Confidence & Trust Gating ───────────────────────────────
    trust_score: Optional[float]                # Calculated 0-100% score
    confidence_band: Optional[str]              # HIGH, MEDIUM, LOW
    confidence_interval: Optional[str]          # e.g. "96.5% - 99.4%"
    source_portal: Optional[str]                # Official gov portal URL (e.g. https://www.indiacode.nic.in)
    source_name: Optional[str]                  # Name of gov portal (e.g. India Code, myScheme)
    performance_metrics: Optional[Dict[str, Any]] # Latency, SLA, retrieval stats

    # ─── Agent Responses ─────────────────────────────────────────
    draft_response: str                         # Raw specialist agent output
    critique: Optional[str]                     # Self-reflection evaluation
    needs_revision: bool                        # True → loop back for correction

    # ─── HITL ────────────────────────────────────────────────────
    requires_human_confirmation: bool           # True → pause for user approval
    human_approved: bool                        # Set after user confirms

    # ─── Final Output ────────────────────────────────────────────
    final_response: str                         # Guardrail-checked, verified response
    error: Optional[str]                        # Non-None if a node failed gracefully
