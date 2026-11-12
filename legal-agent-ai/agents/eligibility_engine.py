"""
Structured Eligibility Reasoning & Alternative Scheme Recovery Engine.

Provides:
- Criterion-by-criterion rule validation (SATISFIED, FAILED, UNKNOWN)
- Source-grounded "Why Not Eligible?" diagnostic breakdown
- Automatic discovery and ranking of alternative schemes using confirmed demographic profile
"""
from typing import Dict, Any, List, Optional
from agents.tools.scheme_tools import (
    check_eligibility,
    get_scheme_details,
    find_alternative_schemes,
    get_required_documents,
    get_application_process,
)

class EligibilityEngine:
    """Evaluates scheme eligibility and generates explainable diagnostic reports."""

    @staticmethod
    def evaluate_scheme(scheme_name: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs structured evaluation of user profile against official scheme criteria.
        """
        raw_eval = check_eligibility(scheme_name, user_profile)
        details = get_scheme_details(scheme_name) or {}
        
        status = raw_eval.get("overall_status", "UNKNOWN")
        evaluations = raw_eval.get("evaluations", [])
        failed_reasons = raw_eval.get("failed_reasons", [])
        missing_vars = raw_eval.get("missing_variables", [])

        # Build user-facing structured summary
        summary_lines = [f"### Eligibility Evaluation for **{raw_eval.get('scheme_name', scheme_name)}**\n"]
        
        if status == "SATISFIED":
            summary_lines.append("✅ **Status: ELIGIBLE** — All verified criteria have been satisfied based on your profile.\n")
        elif status == "FAILED":
            summary_lines.append("❌ **Status: NOT ELIGIBLE** — You do not currently meet all mandatory criteria.\n")
        else:
            summary_lines.append("⚠️ **Status: UNCERTAIN (Missing Information)** — Additional details are needed to verify eligibility.\n")

        summary_lines.append("#### Criteria Breakdown:")
        for ev in evaluations:
            icon = "✅" if ev["status"] == "SATISFIED" else ("❌" if ev["status"] == "FAILED" else "❓")
            summary_lines.append(f"- {icon} **{ev['criterion'].replace('_', ' ').title()}**: {ev['description']} *(Your value: {ev['user_value']})*")

        # If failed, add "Why Not Eligible?" section
        alternatives = []
        if status == "FAILED":
            summary_lines.append("\n#### ❌ Why Not Eligible?")
            for reason in failed_reasons:
                summary_lines.append(f"- {reason}")

            summary_lines.append("\n#### 🔄 Recommended Alternative Schemes for You:")
            alternatives = find_alternative_schemes(user_profile, failed_scheme_name=scheme_name, limit=3)
            if alternatives:
                for alt in alternatives:
                    summary_lines.append(f"- **{alt['scheme_name']}** ({alt['state']}): {alt['benefits']} *({alt['why_matched']})*")
            else:
                summary_lines.append("- No immediate matching alternatives found in the database.")

        elif status == "SATISFIED":
            # Add Next Steps & Required Documents
            docs = get_required_documents(scheme_name)
            app_process = get_application_process(scheme_name)
            summary_lines.append("\n#### 📄 Required Documents:")
            for doc in docs:
                summary_lines.append(f"- [ ] {doc}")

            summary_lines.append(f"\n#### 🚀 Application Steps (Official Portal: {app_process.get('application_url', 'https://www.myscheme.gov.in/')}):")
            for step in app_process.get("steps", []):
                summary_lines.append(f"- {step}")

        report_markdown = "\n".join(summary_lines)

        return {
            "scheme_name": raw_eval.get("scheme_name", scheme_name),
            "status": status,
            "evaluations": evaluations,
            "failed_reasons": failed_reasons,
            "missing_variables": missing_vars,
            "alternatives": alternatives,
            "report_markdown": report_markdown,
            "source_authority": "Tier 1: myScheme / Official Ministry Guidelines",
        }
