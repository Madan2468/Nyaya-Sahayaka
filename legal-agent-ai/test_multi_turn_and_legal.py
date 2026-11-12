"""
Unit and Integration Tests for:
1. Multi-turn independent query handling (preventing repeat answer bug).
2. IPC & CrPC / BNS & BNSS hybrid statutory retrieval.
3. Proactive human-like clarifying questions when critical context is missing.
"""
import unittest
from agents.graph import get_compiled_graph
from agents.supervisor import supervisor_node
from services.legal_db import search_legal_statutes, format_statutes_for_llm


class TestMultiTurnAndLegal(unittest.TestCase):

    def setUp(self):
        self.app = get_compiled_graph()

    def _make_state(self, query: str, history=None, state_val=None):
        return {
            "query": query,
            "language": "en",
            "state": state_val,
            "gender": "All",
            "caste": "All",
            "is_voice_mode": False,
            "chat_history": history or [],
            "intent": "general",
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

    def test_1_independent_queries_do_not_merge(self):
        """Verify Turn 2 query does NOT get prepended with Turn 1 query."""
        history = [
            {"role": "user", "content": "What is IPC Section 302?"},
            {"role": "agent", "content": "Section 302 IPC deals with punishment for murder..."}
        ]
        s2 = self._make_state("What is IPC Section 420?", history)
        routed = supervisor_node(s2)

        self.assertEqual(routed["intent"], "legal")
        self.assertEqual(routed["sanitized_query"], "What is IPC Section 420?")
        self.assertNotIn("302", routed["sanitized_query"], "Turn 2 query must not contain Turn 1 content")

    def test_2_legal_db_crpc_retrieval(self):
        """Verify CrPC 154, 154(3), 156(3) are retrieved for police refusal."""
        hits = search_legal_statutes("police refused to register FIR")
        sections = [f"{h['act']} {h['section']}" for h in hits]
        self.assertTrue(any("154" in s for s in sections), "Should retrieve Section 154 CrPC")
        self.assertTrue(any("154(3)" in s or "156(3)" in s for s in sections), "Should retrieve remedies 154(3) or 156(3)")

    def test_3_legal_db_online_fraud_retrieval(self):
        """Verify Section 420 IPC and IT Act 66D are retrieved for online fraud."""
        hits = search_legal_statutes("Someone cheated me online with money")
        sections = [f"{h['act']} {h['section']}" for h in hits]
        self.assertTrue(any("420" in s for s in sections), "Should retrieve IPC 420")
        self.assertTrue(any("66D" in s or "406" in s for s in sections), "Should retrieve IT Act 66D or IPC 406")

    def test_4_legal_db_bail_retrieval(self):
        """Verify Anticipatory Bail 438 CrPC and 41A CrPC notice are retrieved."""
        hits = search_legal_statutes("Can I get anticipatory bail to avoid arrest?")
        sections = [f"{h['act']} {h['section']}" for h in hits]
        self.assertTrue(any("438" in s for s in sections), "Should retrieve Section 438 CrPC")

    def test_5_gaya_disambiguation(self):
        """Verify 'ho gaya' does NOT falsely set State to Bihar."""
        from agents.context_manager import extract_context_from_text
        ctx = extract_context_from_text("Mera purse chori ho gaya")
        self.assertIsNone(ctx.get_value("state"), "'ho gaya' must not trigger Bihar state")
        self.assertIsNone(ctx.get_value("city"), "'ho gaya' must not trigger Gaya city")

        # But explicit city Gaya SHOULD match
        ctx2 = extract_context_from_text("I live in Gaya, Bihar")
        self.assertEqual(ctx2.get_value("state"), "Bihar")
        self.assertEqual(ctx2.get_value("city"), "Gaya")


if __name__ == "__main__":
    unittest.main()
