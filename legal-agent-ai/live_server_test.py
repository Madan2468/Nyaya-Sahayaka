import json
import requests

BASE_URL = "http://127.0.0.1:8000/api/chat"

def test_single_turn_kolkata_central_college():
    print("\n" + "="*70)
    print("TEST 1: 'hey i live in kolkata and want to join central college have any schemes for me ?'")
    print("="*70)
    payload = {
        "query": "hey i live in kolkata and want to join central college have any schemes for me ?",
        "language": "en",
        "state": None,
        "gender": "all",
        "caste": "all",
        "is_voice_mode": False,
        "chat_history": [],
        "chat_id": "session_test_1"
    }
    resp = requests.post(BASE_URL, json=payload, timeout=35)
    print("Status Code:", resp.status_code)
    data = resp.json()
    print("Detected Intent:", data.get("intent"))
    print("State:", data.get("state"))
    print("Confidence:", data.get("confidence"))
    print("Schemes count:", len(data.get("schemes", [])))
    print("Answer snippet:\n", data.get("response", "")[:400])
    return data

def test_clarification_flow():
    print("\n" + "="*70)
    print("TEST 2: TURN 1 ('Any education schemes for college?') -> TURN 2 ('Kolkata')")
    print("="*70)
    
    # Turn 1
    t1_payload = {
        "query": "Any education schemes for college?",
        "language": "en",
        "state": None,
        "gender": "all",
        "caste": "all",
        "is_voice_mode": False,
        "chat_history": [],
        "chat_id": "session_test_2"
    }
    resp1 = requests.post(BASE_URL, json=t1_payload, timeout=30)
    d1 = resp1.json()
    print("Turn 1 Response:\n", d1.get("response", "")[:300])
    print("Turn 1 missing_slots:", d1.get("missing_slots"))
    print("Turn 1 awaiting_slot in raw state:", d1.get("intent"))

    # Turn 2: User answers "Kolkata"
    t2_payload = {
        "query": "Kolkata",
        "language": "en",
        "state": None,
        "gender": "all",
        "caste": "all",
        "is_voice_mode": False,
        "chat_history": [
            {"role": "user", "content": "Any education schemes for college?"},
            {"role": "agent", "content": d1.get("response", "")}
        ],
        "chat_id": "session_test_2"
    }
    resp2 = requests.post(BASE_URL, json=t2_payload, timeout=30)
    d2 = resp2.json()
    print("\nTurn 2 Status Code:", resp2.status_code)
    print("Turn 2 Intent:", d2.get("intent"))
    print("Turn 2 State:", d2.get("state"))
    print("Turn 2 Schemes count:", len(d2.get("schemes", [])))
    print("Turn 2 Answer snippet:\n", d2.get("response", "")[:500])
    return d2

def test_topic_switch_flow():
    print("\n" + "="*70)
    print("TEST 3: Topic switch from scheme to legal query ('Actually, explain IPC Section 302')")
    print("="*70)
    t3_payload = {
        "query": "Actually, explain IPC Section 302",
        "language": "en",
        "state": None,
        "gender": "all",
        "caste": "all",
        "is_voice_mode": False,
        "chat_history": [
            {"role": "user", "content": "Any education schemes for college?"},
            {"role": "agent", "content": "To give you the exact eligibility criteria and state-specific benefits, could you please select or tell me your state of residence?"}
        ],
        "chat_id": "session_test_3"
    }
    resp3 = requests.post(BASE_URL, json=t3_payload, timeout=30)
    d3 = resp3.json()
    print("Turn 3 Intent:", d3.get("intent"))
    print("Turn 3 Response snippet:\n", d3.get("response", "")[:400])
    return d3

if __name__ == "__main__":
    test_single_turn_kolkata_central_college()
    test_clarification_flow()
    test_topic_switch_flow()
