"""
Confidence-Gated Answering & Trust Scoring Engine.

Implements Section 12A of the Build Brief:
- Never guess when confidence is low.
- Calculates deterministic Trust Score from measurable signals:
  • Retrieval relevance
  • Source authority tier
  • Evidence claim coverage
  • Rule completeness
  • Consistency / Contradiction penalty
  • Ambiguity penalty
- Categorizes responses into 3 Confidence Bands:
  1. HIGH CONFIDENCE: Answer directly + full source evidence.
  2. MEDIUM / UNCERTAIN: Ask targeted option-based clarification.
  3. LOW / UNSUPPORTED: Safely abstain ("I couldn't verify this from available official sources").
- Structured confidence logging.
"""
from typing import Dict, Any, List, Optional

class ConfidenceBand:
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class TrustEngine:
    """Calculates factual confidence and gates responses to prevent hallucination."""

    @staticmethod
    def calculate_trust_score(
        retrieval_relevance: float,       # 0.0 to 1.0 (from dense/keyword score)
        source_authority_tier: int,       # 1 (myScheme/Gov) to 7 (secondary)
        evidence_coverage: float,         # 0.0 to 1.0 (fraction of claims supported)
        rule_completeness: float,         # 0.0 to 1.0 (fraction of criteria evaluated)
        has_conflicts: bool = False,      # True if contradictory sources exist
        ambiguity_penalty: float = 0.0    # Penalty for missing key variables
    ) -> Dict[str, Any]:
        """
        Calculates calibrated Trust Score (0-100%).
        """
        # Base weights
        w_retrieval = 0.25
        w_authority = 0.20
        w_coverage = 0.30
        w_completeness = 0.25

        # Authority factor: Tier 1=1.0, Tier 2=0.9, Tier 3=0.85, Tier 4=0.8, Tier 5=0.75, Tier 6=0.7, Tier 7=0.5
        authority_weights = {1: 1.0, 2: 0.9, 3: 0.85, 4: 0.8, 5: 0.75, 6: 0.7, 7: 0.5}
        auth_factor = authority_weights.get(source_authority_tier, 0.5)

        raw_score = (
            (retrieval_relevance * w_retrieval) +
            (auth_factor * w_authority) +
            (evidence_coverage * w_coverage) +
            (rule_completeness * w_completeness)
        ) * 100.0

        # Apply penalties
        if has_conflicts:
            raw_score -= 20.0
        raw_score -= (ambiguity_penalty * 15.0)

        trust_score = max(0.0, min(100.0, raw_score))

        # Determine band
        if trust_score >= 70.0 and evidence_coverage >= 0.6:
            band = ConfidenceBand.HIGH
            action = "ANSWER_WITH_EVIDENCE"
        elif trust_score >= 40.0:
            band = ConfidenceBand.MEDIUM
            action = "CLARIFY_AMBIGUITY"
        else:
            band = ConfidenceBand.LOW
            action = "ABSTAIN_SAFELY"

        return {
            "trust_score": round(trust_score, 1),
            "confidence_band": band,
            "recommended_action": action,
            "signals": {
                "retrieval_relevance": round(retrieval_relevance, 2),
                "source_authority_tier": source_authority_tier,
                "evidence_coverage": round(evidence_coverage, 2),
                "rule_completeness": round(rule_completeness, 2),
                "has_conflicts": has_conflicts,
                "ambiguity_penalty": round(ambiguity_penalty, 2),
            }
        }

    @staticmethod
    def get_safe_abstention_message(language: str = "en") -> str:
        """Standard abstention message when evidence is insufficient."""
        messages = {
            "en": "I couldn't verify specific official scheme guidelines for that query from authoritative government sources. Please visit https://www.myscheme.gov.in/ or your local State department for official guidance.",
            "hi": "मैं आधिकारिक सरकारी स्रोतों से इस योजना के सटीक दिशा-निर्देशों की पुष्टि नहीं कर सका। कृपया आधिकारिक जानकारी के लिए https://www.myscheme.gov.in/ या अपने स्थानीय सरकारी कार्यालय पर जाएं।",
            "bn": "আমি অফিসিয়াল সরকারি উৎস থেকে এই প্রকল্পের সঠিক নির্দেশাবলী যাচাই করতে পারিনি। অনুগ্রহ করে অফিসিয়াল তথ্যের জন্য https://www.myscheme.gov.in/ ভিজিট করুন।",
            "ta": "அதிகாரப்பூர்வ அரசு ஆதாரங்களிலிருந்து இந்த திட்டத்திற்கான குறிப்பிட்ட வழிகாட்டுதல்களை என்னால் சரிபார்க்க முடியவில்லை. அதிகாரப்பூர்வ தகவலுக்கு https://www.myscheme.gov.in/ ஐப் பார்வையிடவும்.",
            "or": "ମୁଁ ସରକାରୀ ଉତ୍ସରୁ ଏହି ଯୋଜନାର ସଠିକ ନିୟମାବଳୀ ଯାଞ୍ଚ କରିପାରିଲି ନାହିଁ। ଦୟାକରି ସରକାରୀ ୱେବସାଇଟ୍ https://www.myscheme.gov.in/ କିମ୍ବା ସ୍ଥାନୀୟ କାର୍ଯ୍ୟାଳୟ ସହିତ ଯୋଗାଯୋଗ କରନ୍ତୁ।",
        }
        return messages.get(language, messages["en"])
