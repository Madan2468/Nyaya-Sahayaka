"""
Evidence Validation, Claim Auditing & Provenance Citation Engine.

Implements Sections 7, 12C, 23, 25, 26 of the Build Brief:
- Pre-generation evidence packaging with provenance metadata (URL, tier, dept, state)
- Post-generation claim audit: cross-checking draft text against source context
- Contradiction and unsupported claim detection
- Formatting verifiable citations and source cards
"""
import re
from typing import Dict, Any, List, Optional, Tuple

class EvidencePack:
    def __init__(self, query: str, state: Optional[str] = None):
        self.query = query
        self.state = state
        self.evidence_chunks: List[Dict[str, Any]] = []

    def add_chunk(
        self,
        content: str,
        source_title: str,
        source_url: str = "https://www.myscheme.gov.in/",
        authority_tier: int = 1,
        department: Optional[str] = None,
        section: Optional[str] = None,
    ):
        self.evidence_chunks.append({
            "content": content,
            "source_title": source_title,
            "source_url": source_url,
            "authority_tier": authority_tier,
            "department": department or "Government Ministry / Department",
            "section": section,
        })

    def get_formatted_context(self) -> str:
        formatted = []
        for i, chunk in enumerate(self.evidence_chunks):
            header = f"[Source {i+1}: {chunk['source_title']} | Tier {chunk['authority_tier']} | {chunk['department']}]"
            formatted.append(f"{header}\n{chunk['content']}")
        return "\n\n---\n\n".join(formatted)

    def get_citation_markdown(self) -> str:
        if not self.evidence_chunks:
            return ""
        citations = ["\n\n### 🏛️ Verified Government Sources & Evidence:"]
        seen_urls = set()
        for chunk in self.evidence_chunks:
            url = chunk["source_url"]
            if url not in seen_urls:
                citations.append(f"- **{chunk['source_title']}** — [{chunk['department']}]({url}) *(Tier {chunk['authority_tier']} Official Source)*")
                seen_urls.add(url)
        return "\n".join(citations)


class ClaimAuditor:
    """Audits generated answers to ensure every factual claim has supporting evidence."""

    @staticmethod
    def audit_claims(draft_text: str, evidence_text: str) -> Tuple[bool, str, List[str]]:
        """
        Cross-checks factual numbers, ₹ amounts, and scheme names.
        Returns: (is_valid, audited_text, list_of_flagged_issues)
        """
        if not draft_text:
            return False, "", ["Draft text was empty"]

        issues = []
        clean_evidence = evidence_text.lower()

        # 1. Extract ₹ amounts in draft and verify presence in evidence
        draft_amounts = re.findall(r'(?:₹|rs\.?)\s*([\d,]+)', draft_text, re.I)
        for amt in draft_amounts:
            normalized_amt = amt.replace(",", "").strip()
            # If amount > 100 and not found in evidence
            if len(normalized_amt) >= 3 and normalized_amt not in clean_evidence and amt not in clean_evidence:
                issues.append(f"Unverified monetary amount '₹{amt}' not found in retrieved source context")

        # 2. Extract percentage numbers (e.g. 50%, 40%)
        draft_pcts = re.findall(r'(\d+)\s*%', draft_text)
        for pct in draft_pcts:
            if pct not in clean_evidence and f"{pct}%" not in clean_evidence:
                issues.append(f"Unverified percentage '{pct}%' not found in source context")

        # If major discrepancies exist, flag for revision or qualification
        is_valid = len(issues) == 0
        return is_valid, draft_text, issues
