"""
Test suite for conversational context memory and follow-up inquiry handling.
Verifies that follow-up questions referencing previous responses maintain context,
preserve intent, correctly identify target entities, and do not repeat greetings.
"""
import unittest
from agents.supervisor import supervisor_node
from agents.graph import get_compiled_graph


class TestFollowUpContext(unittest.TestCase):

    def setUp(self):
        self.app = get_compiled_graph()

    def _base_state(self, query: str, history=None, intent="general", state_val=None):
        return {
            "query": query,
            "language": "en",
            "state": state_val,
            "gender": "All",
            "caste": "All",
            "is_voice_mode": False,
            "chat_history": history or [],
            "intent": intent,
            "sanitized_query": query,
            "retrieved_context": "",
            "retrieval_metadata": None,
            "draft_response": "",
            "critique": None,
            "needs_revision": False,
            "requires_human_confirmation": False,
            "human_approved": False,
            "final_response": "",
            "error": None,
            "awaiting_slot": None,
            "collected_slots": {},
            "original_user_query": None,
        }

    def test_scheme_followup_documents_for_this(self):
        """User asks 'what are the documents required for this?' after scheme recommendation."""
        history = [
            {"role": "user", "content": "I am a BTech student in Karnataka. What scholarships can I get?"},
            {"role": "agent", "content": "Here are the top schemes:\n1. **SSP Post-Matric Scholarship** (Karnataka)\n2. **Vidyasiri Scheme**\n\nHow can I help further?"}
        ]
        s = self._base_state("what are the documents required for this?", history)
        routed = supervisor_node(s)

        self.assertEqual(routed["intent"], "scheme", "Intent must stay scheme, not switch to document or general")
        self.assertTrue(routed["is_context_sufficient"], "Must not block asking for state")
        self.assertIn("SSP Post-Matric Scholarship", routed["sanitized_query"], "Must attach target scheme name to active query")

    def test_scheme_followup_apply_first_one(self):
        """User asks 'how to apply for the first one?' after scheme recommendation."""
        history = [
            {"role": "user", "content": "Tell me schemes for farmers in Uttar Pradesh"},
            {"role": "agent", "content": "Eligible schemes:\n1. **PM Kisan Samman Nidhi**\n2. **UP Kisan Karj Mafi Yojana**"}
        ]
        s = self._base_state("how to apply for the first one?", history)
        routed = supervisor_node(s)

        self.assertEqual(routed["intent"], "scheme")
        self.assertIn("PM Kisan Samman Nidhi", routed["sanitized_query"])

    def test_scheme_followup_hindi_documents(self):
        """User asks 'kya documents lagenge isme?' after scheme recommendation."""
        history = [
            {"role": "user", "content": "PM Awas Yojana ke baare me batao"},
            {"role": "agent", "content": "Scheme: **Pradhan Mantri Awas Yojana (PMAY)**\nBenefits: Subsidy for pucca house."}
        ]
        s = self._base_state("kya documents lagenge isme?", history)
        routed = supervisor_node(s)

        self.assertEqual(routed["intent"], "scheme")
        self.assertIn("Pradhan Mantri Awas Yojana", routed["sanitized_query"])

    def test_legal_followup_is_it_bailable(self):
        """User asks 'is it bailable?' after theft response."""
        history = [
            {"role": "user", "content": "My bike was stolen last night"},
            {"role": "agent", "content": "Applicable provisions:\n1. ⚖️ **Theft: Section 379 IPC / Section 303(2) BNS**\nIt is a cognizable offence."}
        ]
        s = self._base_state("is it bailable?", history)
        routed = supervisor_node(s)

        self.assertEqual(routed["intent"], "legal")
        self.assertTrue(
            "379" in routed["sanitized_query"] or "Theft" in routed["sanitized_query"],
            "Target offence or section must be contextualized"
        )

    def test_general_followup_no_greeting_repetition(self):
        """User says 'aur batao' or 'tell me more' - should not repeat greetings."""
        import os
        from unittest.mock import patch
        from agents.graph import general_agent_node
        history = [
            {"role": "user", "content": "Tell me about RTI Act"},
            {"role": "agent", "content": "RTI Act 2005 allows citizens to seek information from public authorities."}
        ]
        s = self._base_state("tell me more", history, intent="general")
        # Test offline fallback behavior when LLM is unavailable
        with patch.dict(os.environ, {}, clear=True):
            res = general_agent_node(s)

        draft = res.get("draft_response", "")
        self.assertNotIn("Namaste! I'm Nyaya Sahayaka. I can help you with:", draft)
        self.assertIn("specify which scheme", draft)


if __name__ == "__main__":
    unittest.main()
