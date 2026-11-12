"""
Comprehensive Verification Suite for Nyay Sahayaka Scheme Agent.

Tests:
1. Auditable Scheme Tool Suite
2. Context Sufficiency & Clarification-First Behavior
3. Central vs State Specialist Agents
4. Structured Eligibility Engine & Why Not Eligible breakdown
5. Confidence-Gated Answering & Trust Score calculations
6. End-to-End Compiled LangGraph Pipeline
"""
import os
import sys

# Ensure root of legal-agent-ai is in PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.tools.scheme_tools import (
    search_central_schemes,
    search_state_schemes,
    get_scheme_details,
    get_eligibility_rules,
    check_eligibility,
    identify_missing_information,
    get_required_documents,
    get_application_process,
    find_alternative_schemes,
)
from agents.context_manager import (
    UserContext,
    FactCertainty,
    extract_context_from_text,
    check_context_sufficiency_for_query,
)
from agents.eligibility_engine import EligibilityEngine
from agents.trust_engine import TrustEngine, ConfidenceBand
from agents.state import AgentState
from agents.graph import get_compiled_graph


def test_scheme_tools():
    print("\n--- 1. Testing Auditable Scheme Tool Suite ---")
    
    # 1. Central Scheme Search
    central = search_central_schemes("scholarship higher education", limit=3)
    print(f"Found {len(central)} Central schemes.")
    assert len(central) > 0, "No central schemes found"
    assert central[0]["jurisdiction"] == "Central"
    print(f"✅ Central Scheme Tool verified: '{central[0]['scheme_name']}'")

    # 2. State Scheme Search (Odisha / Haryana / MP)
    state_res = search_state_schemes("scholarship education", state="Odisha", limit=3)
    print(f"Found {len(state_res)} State schemes for Odisha.")
    assert len(state_res) > 0, "No state schemes found for Odisha"
    assert "Odisha" in state_res[0]["state"]
    print(f"✅ State Scheme Tool verified: '{state_res[0]['scheme_name']}' ({state_res[0]['state']})")

    # 3. Scheme Details
    details = get_scheme_details(state_res[0]["scheme_name"])
    assert details is not None
    assert "benefits" in details
    assert "eligibility" in details
    print(f"✅ Scheme Details Tool verified for '{details['scheme_name']}'")

    # 4. Required Documents & Application Process
    docs = get_required_documents(details["scheme_name"])
    app_proc = get_application_process(details["scheme_name"])
    assert len(docs) >= 2, "Insufficient documents retrieved"
    assert len(app_proc["steps"]) >= 3, "Insufficient application steps"
    print(f"✅ Documents & Application Process Tools verified ({len(docs)} docs, {len(app_proc['steps'])} steps).")


def test_context_manager_and_clarification():
    print("\n--- 2. Testing Context Sufficiency & Clarification-First Engine ---")

    # Ambiguous query without State
    ambiguous_query = "What scholarships are available for 10th class students?"
    ctx = extract_context_from_text(ambiguous_query)
    assert ctx.get_value("student_class") == "Class 10 (Matric)"
    assert ctx.get_value("state") is None

    is_sufficient, clarification_q, options, slot_name = check_context_sufficiency_for_query(ambiguous_query, ctx)
    print(f"Is Sufficient: {is_sufficient}")
    print(f"Clarification Question: {clarification_q}")
    print(f"Options: {options}")

    assert is_sufficient is False, "Context sufficiency check failed to catch missing State"
    assert "state" in clarification_q.lower()
    assert options is not None and len(options) > 3
    print("✅ Clarification-First behavior & option generation verified.")

    # Context with confirmed State
    query_with_state = "I am a girl student in Odisha studying in 12th class, SC category. What scholarships can I get?"
    ctx2 = extract_context_from_text(query_with_state)
    assert ctx2.get_value("state") == "Odisha"
    assert ctx2.get_value("gender") == "Female"
    assert ctx2.get_value("caste") == "SC"

    is_sufficient2, _, _, _ = check_context_sufficiency_for_query(query_with_state, ctx2)
    assert is_sufficient2 is True, "Sufficiency check failed when state was present"
    print("✅ Context extraction & fact certainty classification verified.")


def test_structured_eligibility_and_alternatives():
    print("\n--- 3. Testing Structured Eligibility & Why Not Eligible Engine ---")

    # Test scheme
    scheme_name = "Pre-Matric Scholarship for Backward Class Students"
    
    # 1. Eligible Profile
    eligible_profile = {
        "state": "Madhya Pradesh",
        "student_class": "Class 7",
        "caste": "OBC",
    }
    report = EligibilityEngine.evaluate_scheme(scheme_name, eligible_profile)
    print(f"Eligible Profile Status: {report['status']}")
    assert report["status"] == "SATISFIED"
    assert "ELIGIBLE" in report["report_markdown"]
    print("✅ Structured ELIGIBLE evaluation passed.")

    # 2. Ineligible Profile (Wrong state / Wrong caste)
    ineligible_profile = {
        "state": "Gujarat", # Requires MP
        "student_class": "Class 7",
        "caste": "General", # Requires OBC
    }
    fail_report = EligibilityEngine.evaluate_scheme(scheme_name, ineligible_profile)
    print(f"Ineligible Profile Status: {fail_report['status']}")
    assert fail_report["status"] == "FAILED"
    assert len(fail_report["failed_reasons"]) > 0
    assert len(fail_report["alternatives"]) > 0
    print(f"Failed Reasons: {fail_report['failed_reasons']}")
    print(f"Suggested Alternatives Count: {len(fail_report['alternatives'])}")
    print("✅ 'Why Not Eligible' diagnostic & Alternative Scheme Recovery passed.")


def test_trust_score_and_confidence_gating():
    print("\n--- 4. Testing Confidence-Gated Answering & Trust Engine ---")

    # High Confidence Case
    high_conf = TrustEngine.calculate_trust_score(
        retrieval_relevance=0.95,
        source_authority_tier=1,
        evidence_coverage=0.9,
        rule_completeness=1.0,
        has_conflicts=False,
    )
    print(f"High Trust Score: {high_conf['trust_score']}% | Band: {high_conf['confidence_band']}")
    assert high_conf["confidence_band"] == ConfidenceBand.HIGH
    assert high_conf["recommended_action"] == "ANSWER_WITH_EVIDENCE"

    # Low Confidence / Unsupported Case (Abstention Gate)
    low_conf = TrustEngine.calculate_trust_score(
        retrieval_relevance=0.2,
        source_authority_tier=7,
        evidence_coverage=0.1,
        rule_completeness=0.2,
        has_conflicts=True,
    )
    print(f"Low Trust Score: {low_conf['trust_score']}% | Band: {low_conf['confidence_band']}")
    assert low_conf["confidence_band"] == ConfidenceBand.LOW
    assert low_conf["recommended_action"] == "ABSTAIN_SAFELY"

    abstention_msg = TrustEngine.get_safe_abstention_message("en")
    assert "couldn't verify" in abstention_msg
    print("✅ Safe Abstention message and confidence gating verified.")


def test_end_to_end_langgraph_pipeline():
    print("\n--- 5. Testing End-to-End Multi-Agent LangGraph Pipeline ---")
    app = get_compiled_graph()
    assert app is not None

    # Test 1: Ambiguous Scheme Query -> Clarification Output
    print("\n[E2E Scenario 1: Ambiguous Query Clarification]")
    ambiguous_state: AgentState = {
        "query": "I want scholarship for college.",
        "language": "en",
        "state": None,
        "gender": "All",
        "caste": "All",
        "is_voice_mode": False,
        "chat_history": [],
        "intent": "general",
        "jurisdiction": "general",
        "sanitized_query": "I want scholarship for college.",
        "is_context_sufficient": True,
        "missing_variables": None,
        "clarification_options": None,
        "retrieved_context": "",
        "retrieval_metadata": None,
        "citations": None,
        "eligibility_result": None,
        "trust_score": None,
        "confidence_band": None,
        "draft_response": "",
        "critique": None,
        "needs_revision": False,
        "requires_human_confirmation": False,
        "human_approved": False,
        "final_response": "",
        "error": None,
    }

    res1 = app.invoke(ambiguous_state)
    print(f"Scenario 1 Final Response Snippet:\n{res1['final_response'][:250]}...")
    assert res1["is_context_sufficient"] is False or "state" in res1["final_response"].lower()
    print("✅ E2E Clarification-First response verified.")

    # Test 2: Specific State Scheme Query -> State Specialist Response
    print("\n[E2E Scenario 2: Specific State Scheme Query]")
    state_query_state: AgentState = {
        "query": "What are farmer assistance schemes in Odisha?",
        "language": "en",
        "state": "Odisha",
        "gender": "All",
        "caste": "All",
        "is_voice_mode": False,
        "chat_history": [],
        "intent": "general",
        "jurisdiction": "general",
        "sanitized_query": "What are farmer assistance schemes in Odisha?",
        "is_context_sufficient": True,
        "missing_variables": None,
        "clarification_options": None,
        "retrieved_context": "",
        "retrieval_metadata": None,
        "citations": None,
        "eligibility_result": None,
        "trust_score": None,
        "confidence_band": None,
        "draft_response": "",
        "critique": None,
        "needs_revision": False,
        "requires_human_confirmation": False,
        "human_approved": False,
        "final_response": "",
        "error": None,
    }

    res2 = app.invoke(state_query_state)
    print(f"Scenario 2 Final Response Snippet:\n{res2['final_response'][:250]}...")
    assert len(res2["final_response"]) > 20
    assert "Odisha" in res2["final_response"] or "Odisha" in res2.get("retrieved_context", "")
    print("✅ E2E State Scheme Specialist response verified.")


if __name__ == "__main__":
    print("==================================================")
    print(" Nyay Sahayaka Scheme Agent Full Verification    ")
    print("==================================================")
    test_scheme_tools()
    test_context_manager_and_clarification()
    test_structured_eligibility_and_alternatives()
    test_trust_score_and_confidence_gating()
    test_end_to_end_langgraph_pipeline()
    print("\n🎉 ALL NYAY SAHAYAKA SCHEME SYSTEM TESTS PASSED SUCCESSFULLY!")
