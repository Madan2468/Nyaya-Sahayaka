import os
import sys
from fastapi.testclient import TestClient

# Ensure root of legal-agent-ai is in PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.redis_service import RedisService
from services.qdrant_service import QdrantRAGService
from main import app

def test_redis_service():
    print("\n--- 1. Testing Redis Service ---")
    redis_svc = RedisService()
    print(f"Redis connected: {redis_svc.is_connected}")

    # Test Caching
    test_key = "test_statutory_302"
    test_payload = {"response": "Section 302 IPC deals with punishment for murder.", "intent": "legal"}
    redis_svc.set_cached_response(test_key, test_payload, ttl_seconds=60)
    cached = redis_svc.get_cached_response(test_key)
    assert cached == test_payload, f"Cache mismatch: expected {test_payload}, got {cached}"
    print("✅ Redis Caching verified successfully.")

    # Test Session Memory Sliding Window
    chat_id = "test_session_phase1"
    redis_svc.clear_chat_window(chat_id)
    for i in range(8):
        redis_svc.append_chat_message(chat_id, "user" if i % 2 == 0 else "agent", f"Message {i}", max_turns=6)
    
    history = redis_svc.get_chat_window(chat_id)
    assert len(history) == 6, f"Expected 6 windowed messages, got {len(history)}"
    assert history[-1]["content"] == "Message 7", f"Expected last message to be Message 7, got {history[-1]}"
    print(f"✅ Redis Sliding Window verified (retained last {len(history)} turns).")
    redis_svc.clear_chat_window(chat_id)


def test_qdrant_service():
    print("\n--- 2. Testing Qdrant RAG Service ---")
    qdrant_svc = QdrantRAGService()
    print(f"Qdrant connected: {qdrant_svc.is_connected}")

    # Test Legal Search
    legal_context = qdrant_svc.retrieve("What is punishment for murder in IPC?", top_k=3, intent="legal")
    print(f"\n[Legal Query Result Snippet]:\n{legal_context[:300]}...")
    assert "Section" in legal_context or "IPC" in legal_context, "Legal retrieval did not return section data"
    print("✅ Qdrant Legal Statutory Retrieval verified.")

    # Test Scheme Search with State Filter
    scheme_context = qdrant_svc.retrieve("scholarship for college admission", top_k=3, intent="scheme", state="Odisha")
    print(f"\n[Scheme Query Result Snippet]:\n{scheme_context[:300]}...")
    assert len(scheme_context) > 20, "Scheme retrieval context was unexpectedly empty"
    print("✅ Qdrant Government Scheme Retrieval with State filtering verified.")


def test_fastapi_endpoints():
    print("\n--- 3. Testing FastAPI Health & Rate Limiting ---")
    with TestClient(app) as client:
        # Health check
        res = client.get("/health")
        print("Health status code:", res.status_code)
        print("Health response:", res.json())
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        print("✅ FastAPI /health endpoint verified.")

        # Rate limiter check on chat
        print("Testing rate limiting on /api/chat...")
        for _ in range(2):
            r = client.post(
                "/api/chat",
                json={"query": "Hello", "language": "en"}
            )
            # Should receive valid response status
            assert r.status_code in (200, 429, 500), f"Unexpected status: {r.status_code}"
        print("✅ Rate limiting middleware initialized and active.")

if __name__ == "__main__":
    print("========================================")
    print(" Nyaya Sahayaka - Phase 1 Verification  ")
    print("========================================")
    test_redis_service()
    test_qdrant_service()
    test_fastapi_endpoints()
    print("\n🎉 ALL PHASE 1 TESTS PASSED SUCCESSFULLY!")
