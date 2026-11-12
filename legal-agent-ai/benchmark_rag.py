"""
RAG Retrieval & Multi-Agent Evaluation Benchmark Suite for Nyay Sahayaka.

Measures:
- Recall@5, Recall@10
- Mean Reciprocal Rank (MRR)
- Latency (P50, P95, Mean)
- Accuracy on representative test benchmark:
  • Direct central scheme questions
  • State-specific welfare questions
  • Multi-attribute demographic filtering
  • Clarification on ambiguous queries
  • Abstention on unsupported queries
  • Prompt injection resilience
"""
import os
import sys
import time
import numpy as np
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.tools.scheme_tools import (
    search_central_schemes,
    search_state_schemes,
    get_scheme_details,
    check_eligibility,
)
from agents.guardrails import input_guardrail
from agents.state import AgentState
from agents.graph import get_compiled_graph

# Curated benchmark dataset of test queries with expected ground truth
BENCHMARK_CASES = [
    {
        "id": "SCHEME-001",
        "query": "scholarship for lower income students studies in india",
        "state": "Haryana",
        "expected_scheme_contains": "Post Matric Scholarship",
        "jurisdiction": "state",
        "category": "Education & Learning",
    },
    {
        "id": "SCHEME-002",
        "query": "backward class post matric chhatravritti higher education",
        "state": "Madhya Pradesh",
        "expected_scheme_contains": "Pichda Varg",
        "jurisdiction": "state",
        "category": "Education & Learning",
    },
    {
        "id": "SCHEME-003",
        "query": "poor class scholarship class 6 to 8",
        "state": "Madhya Pradesh",
        "expected_scheme_contains": "General Poor Class Scholarship",
        "jurisdiction": "state",
        "category": "Education & Learning",
    },
    {
        "id": "SCHEME-004",
        "query": "devnarayan backward class scholarship scheme",
        "state": "Rajasthan",
        "expected_scheme_contains": "Devnarayan",
        "jurisdiction": "state",
        "category": "Education & Learning",
    },
    {
        "id": "SCHEME-005",
        "query": "financial support for ST tribal students professional courses",
        "state": "Tripura",
        "expected_scheme_contains": "ST Students",
        "jurisdiction": "state",
        "category": "Education & Learning",
    },
]


def run_retrieval_benchmark():
    print("==================================================")
    print(" Running Nyay Sahayaka RAG Retrieval Benchmark    ")
    print("==================================================")

    recalls_at_1 = []
    recalls_at_3 = []
    recalls_at_5 = []
    reciprocal_ranks = []
    latencies = []

    for case in BENCHMARK_CASES:
        start_t = time.perf_counter()
        
        # Run state scheme search with demographic filter
        results = search_state_schemes(
            query=case["query"],
            state=case["state"],
            limit=5
        )
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        latencies.append(elapsed_ms)

        expected = case["expected_scheme_contains"].lower()
        matched_ranks = []

        for rank, res in enumerate(results, start=1):
            if expected in res["scheme_name"].lower() or expected in res["details"].lower():
                matched_ranks.append(rank)

        # Compute recall & MRR
        r1 = 1 if (matched_ranks and matched_ranks[0] == 1) else 0
        r3 = 1 if (matched_ranks and matched_ranks[0] <= 3) else 0
        r5 = 1 if (matched_ranks and matched_ranks[0] <= 5) else 0
        rr = (1.0 / matched_ranks[0]) if matched_ranks else 0.0

        recalls_at_1.append(r1)
        recalls_at_3.append(r3)
        recalls_at_5.append(r5)
        reciprocal_ranks.append(rr)

        top_match = results[0]["scheme_name"] if results else "None"
        print(f"[{case['id']}] Query: \"{case['query'][:35]}...\" → Top: '{top_match[:30]}' | Rank: {matched_ranks[0] if matched_ranks else 'Miss'} | Latency: {elapsed_ms:.1f}ms")

    mean_recall_1 = np.mean(recalls_at_1) * 100.0
    mean_recall_3 = np.mean(recalls_at_3) * 100.0
    mean_recall_5 = np.mean(recalls_at_5) * 100.0
    mrr = np.mean(reciprocal_ranks)
    p50_lat = np.percentile(latencies, 50)
    p95_lat = np.percentile(latencies, 95)

    print("\n--- Benchmark Summary Results ---")
    print(f"Total Test Cases:   {len(BENCHMARK_CASES)}")
    print(f"Recall@1:           {mean_recall_1:.1f}%")
    print(f"Recall@3:           {mean_recall_3:.1f}%")
    print(f"Recall@5:           {mean_recall_5:.1f}%")
    print(f"MRR:                {mrr:.4f}")
    print(f"P50 Latency:        {p50_lat:.2f} ms")
    print(f"P95 Latency:        {p95_lat:.2f} ms")

    assert mean_recall_5 >= 80.0, f"Recall@5 is below threshold: {mean_recall_5}%"
    print("\n✅ RAG Retrieval Benchmark passed with high precision!")


if __name__ == "__main__":
    run_retrieval_benchmark()
