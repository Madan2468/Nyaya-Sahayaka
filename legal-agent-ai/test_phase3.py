import os
import sys
from fastapi.testclient import TestClient

# Ensure root of legal-agent-ai is in PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app

def test_phase3_backend_integration():
    print("========================================")
    print(" Nyaya Sahayaka - Phase 3 Verification  ")
    print("========================================")

    with TestClient(app) as client:
        # 1. Health check
        print("\n--- 1. Health Endpoint Check ---")
        res = client.get("/health")
        print("Status code:", res.status_code)
        print("Response:", res.json())
        assert res.status_code == 200
        health_data = res.json()
        assert health_data["status"] == "ok"
        assert health_data["services"]["langgraph"] == "loaded"
        print("✅ Health check passed.")

        # 2. End-to-end Chat Endpoint (Legal)
        print("\n--- 2. End-to-End Chat (Legal IPC Domain) ---")
        chat_res = client.post(
            "/api/chat",
            json={
                "query": "What is punishment for murder under IPC section 302?",
                "language": "en",
                "chat_id": "test_session_p3"
            }
        )
        print("Chat status:", chat_res.status_code)
        print("Chat response snippet:", chat_res.json().get("response", "")[:200])
        assert chat_res.status_code == 200
        chat_data = chat_res.json()
        assert chat_data["intent"] == "legal"
        assert len(chat_data["response"]) > 20
        print("✅ Legal chat query succeeded.")

        # 3. End-to-End Chat (Scheme with state auto-detection)
        print("\n--- 3. End-to-End Chat (Scheme Domain with Auto State) ---")
        scheme_res = client.post(
            "/api/chat",
            json={
                "query": "What are farmer schemes available in Odisha?",
                "language": "en",
                "chat_id": "test_session_p3"
            }
        )
        print("Scheme status:", scheme_res.status_code)
        print("Scheme response snippet:", scheme_res.json().get("response", "")[:200])
        assert scheme_res.status_code == 200
        scheme_data = scheme_res.json()
        assert scheme_data["intent"] == "scheme"
        print("✅ Scheme chat query succeeded.")

        # 4. Voice Mode test
        print("\n--- 4. Voice Mode Chat ---")
        voice_res = client.post(
            "/api/chat",
            json={
                "query": "What is IPC 302?",
                "language": "en",
                "is_voice_mode": True,
                "chat_id": "test_session_p3"
            }
        )
        print("Voice status:", voice_res.status_code)
        print("Voice response:", voice_res.json().get("response"))
        assert voice_res.status_code == 200
        print("✅ Voice mode chat succeeded.")

        # 5. Clear Session
        print("\n--- 5. Session Clear Endpoint ---")
        clear_res = client.post("/api/session/clear?chat_id=test_session_p3")
        print("Clear status:", clear_res.status_code)
        print("Clear response:", clear_res.json())
        assert clear_res.status_code == 200
        assert clear_res.json()["status"] == "cleared"
        print("✅ Session clear endpoint succeeded.")

        # 6. Document Generation Endpoint
        print("\n--- 6. Generate Document Endpoint ---")
        doc_res = client.post(
            "/api/generate-document",
            json={
                "document_type": "RTI Application",
                "details": {"subject": "Road Repair Records", "authority": "Municipal Corporation Delhi"},
                "language": "en"
            }
        )
        print("Doc gen status:", doc_res.status_code)
        doc_data = doc_res.json()
        print("Doc type:", doc_data.get("document_type"))
        print("Doc snippet:", doc_data.get("document_content", "")[:200])
        assert doc_res.status_code == 200
        assert doc_data["status"] == "success"
        assert doc_data["requires_confirmation"] is True
        print("✅ Document generation endpoint succeeded.")

        print("\n🎉 ALL PHASE 3 INTEGRATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_phase3_backend_integration()
