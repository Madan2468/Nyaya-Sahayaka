"""
Comprehensive Conversational Context & Multi-Turn Verification Suite.
Tests all 7 scenarios specified for slot-filling, intent preservation, location resolution, and topic change.
"""
import unittest
from agents.graph import get_compiled_graph
from agents.context_manager import extract_context_from_text, check_context_sufficiency_for_query
from agents.supervisor import supervisor_node


class TestConversationalContext(unittest.TestCase):

    def setUp(self):
        self.app = get_compiled_graph()

    def _base_state(self, query: str, history=None):
        return {
            "query": query,
            "language": "en",
            "state": None,
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
            "collected_slots": None,
            "original_user_query": None,
        }

    def test_1_direct_kolkata_central_college(self):
        """TEST 1: User provides city and central college in turn 1."""
        q = "I live in Kolkata and want to join central college. Are there any schemes for me?"
        state = self._base_state(q)
        routed = supervisor_node(state)

        self.assertEqual(routed["intent"], "scheme")
        self.assertEqual(routed["state"], "West Bengal")
        self.assertEqual(routed["collected_slots"].get("city"), "Kolkata")
        self.assertTrue(routed["is_context_sufficient"], "Should not ask for state when city/central is resolved")

    def test_2_multiturn_kolkata_slot_fill(self):
        """TEST 2: User answers clarification with Kolkata."""
        history = [
            {"role": "user", "content": "Any education schemes for me?"},
            {"role": "agent", "content": "To give you the exact eligibility criteria, could you please tell me your state of residence?"}
        ]
        state = self._base_state("Kolkata", history)
        routed = supervisor_node(state)

        self.assertEqual(routed["intent"], "scheme")
        self.assertEqual(routed["state"], "West Bengal")
        self.assertEqual(routed["collected_slots"].get("city"), "Kolkata")
        self.assertTrue(routed["is_context_sufficient"])

    def test_3_multiturn_west_bengal(self):
        """TEST 3: User answers with West Bengal directly."""
        history = [
            {"role": "user", "content": "Any schemes for college?"},
            {"role": "agent", "content": "What is your state?"}
        ]
        state = self._base_state("West Bengal", history)
        routed = supervisor_node(state)

        self.assertEqual(routed["intent"], "scheme")
        self.assertEqual(routed["state"], "West Bengal")
        self.assertTrue(routed["is_context_sufficient"])

    def test_4_multiturn_mumbai_resolution(self):
        """TEST 4: User answers with Mumbai -> Maharashtra."""
        history = [
            {"role": "user", "content": "Any schemes?"},
            {"role": "agent", "content": "What is your state?"}
        ]
        state = self._base_state("Mumbai", history)
        routed = supervisor_node(state)

        self.assertEqual(routed["intent"], "scheme")
        self.assertEqual(routed["state"], "Maharashtra")
        self.assertEqual(routed["collected_slots"].get("city"), "Mumbai")
        self.assertTrue(routed["is_context_sufficient"])

    def test_5_multiturn_delhi(self):
        """TEST 5: User answers with Delhi."""
        history = [
            {"role": "user", "content": "Any schemes for college?"},
            {"role": "agent", "content": "What is your state?"}
        ]
        state = self._base_state("Delhi", history)
        routed = supervisor_node(state)

        self.assertEqual(routed["intent"], "scheme")
        self.assertEqual(routed["state"], "Delhi")
        self.assertTrue(routed["is_context_sufficient"])

    def test_6_multiturn_course_btech(self):
        """TEST 6: Multi-turn retaining Kolkata, West Bengal, and adding BTech course."""
        history = [
            {"role": "user", "content": "Any education scheme?"},
            {"role": "agent", "content": "What is your state?"},
            {"role": "user", "content": "Kolkata"},
            {"role": "agent", "content": "What course or degree are you studying?"}
        ]
        state = self._base_state("BTech", history)
        routed = supervisor_node(state)

        self.assertEqual(routed["intent"], "scheme")
        self.assertEqual(routed["state"], "West Bengal")
        self.assertEqual(routed["collected_slots"].get("city"), "Kolkata")
        self.assertEqual(routed["collected_slots"].get("course"), "B.Tech")
        self.assertEqual(routed["collected_slots"].get("education_level"), "Undergraduate")

    def test_7_topic_change_to_ipc_302(self):
        """TEST 7: User intentionally changes topic to IPC 302."""
        history = [
            {"role": "user", "content": "Any schemes for college?"},
            {"role": "agent", "content": "What is your state?"}
        ]
        state = self._base_state("Actually, what is IPC Section 302?", history)
        routed = supervisor_node(state)

        self.assertEqual(routed["intent"], "legal", "Should detect explicit topic change to legal")
        self.assertEqual(routed["jurisdiction"], "general")


if __name__ == "__main__":
    unittest.main()
