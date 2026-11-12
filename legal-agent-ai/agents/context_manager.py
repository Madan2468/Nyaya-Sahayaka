"""
Context Manager & Fact Classification Engine for Nyay Sahayaka.

Implements the Clarification-First architectural constraint:
- Classifies user profile variables as USER_CONFIRMED, INFERRED, or UNKNOWN.
- Never converts an inferred fact into a confirmed fact without user agreement.
- Checks whether context is sufficient before executing eligibility decisions.
- Formulates option-based clarifications (A/B/C/D) when critical context is missing.
"""
import re
from typing import Dict, Any, List, Optional, Tuple

class FactCertainty:
    USER_CONFIRMED = "USER_CONFIRMED"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"

class UserContext:
    def __init__(self):
        self.facts: Dict[str, Dict[str, Any]] = {
            "city": {"value": None, "certainty": FactCertainty.UNKNOWN},
            "state": {"value": None, "certainty": FactCertainty.UNKNOWN},
            "age": {"value": None, "certainty": FactCertainty.UNKNOWN},
            "gender": {"value": "All", "certainty": FactCertainty.UNKNOWN},
            "caste": {"value": "All", "certainty": FactCertainty.UNKNOWN},
            "course": {"value": None, "certainty": FactCertainty.UNKNOWN},
            "student_class": {"value": None, "certainty": FactCertainty.UNKNOWN},
            "education_level": {"value": None, "certainty": FactCertainty.UNKNOWN},
            "occupation": {"value": None, "certainty": FactCertainty.UNKNOWN},
            "parent_occupation": {"value": None, "certainty": FactCertainty.UNKNOWN},
            "annual_income": {"value": None, "certainty": FactCertainty.UNKNOWN},
            "disability": {"value": None, "certainty": FactCertainty.UNKNOWN},
            "current_scheme": {"value": None, "certainty": FactCertainty.UNKNOWN},
        }

    def set_confirmed(self, key: str, value: Any):
        if key in self.facts:
            self.facts[key] = {"value": value, "certainty": FactCertainty.USER_CONFIRMED}

    def set_value(self, key: str, value: Any, confirmed: bool = True):
        if confirmed:
            self.set_confirmed(key, value)
        else:
            self.set_inferred(key, value)

    def set_inferred(self, key: str, value: Any):
        if key in self.facts and self.facts[key]["certainty"] != FactCertainty.USER_CONFIRMED:
            self.facts[key] = {"value": value, "certainty": FactCertainty.INFERRED}

    def get_value(self, key: str, default: Any = None) -> Any:
        return self.facts.get(key, {}).get("value", default)

    def get_certainty(self, key: str) -> str:
        return self.facts.get(key, {}).get("certainty", FactCertainty.UNKNOWN)

    def to_profile_dict(self) -> Dict[str, Any]:
        return {k: v["value"] for k, v in self.facts.items() if v["value"] is not None}

# Comprehensive Indian City/Town to State Mapping
CITY_TO_STATE = {
    # West Bengal
    "kolkata": "West Bengal", "calcutta": "West Bengal", "howrah": "West Bengal",
    "siliguri": "West Bengal", "durgapur": "West Bengal", "asansol": "West Bengal",
    "darjeeling": "West Bengal", "kharagpur": "West Bengal", "bengal": "West Bengal",
    # Maharashtra
    "mumbai": "Maharashtra", "bombay": "Maharashtra", "pune": "Maharashtra",
    "nagpur": "Maharashtra", "thane": "Maharashtra", "nashik": "Maharashtra",
    "aurangabad": "Maharashtra", "navi mumbai": "Maharashtra", "solapur": "Maharashtra",
    # Karnataka
    "bengaluru": "Karnataka", "bangalore": "Karnataka", "mysuru": "Karnataka",
    "mysore": "Karnataka", "hubli": "Karnataka", "mangalore": "Karnataka", "belagavi": "Karnataka",
    # Delhi
    "delhi": "Delhi", "new delhi": "Delhi", "ncr": "Delhi",
    # Tamil Nadu
    "chennai": "Tamil Nadu", "madras": "Tamil Nadu", "coimbatore": "Tamil Nadu",
    "madurai": "Tamil Nadu", "salem": "Tamil Nadu", "trichy": "Tamil Nadu", "tiruchirappalli": "Tamil Nadu",
    # Telangana
    "hyderabad": "Telangana", "secunderabad": "Telangana", "warangal": "Telangana", "nizamabad": "Telangana",
    # Gujarat
    "ahmedabad": "Gujarat", "surat": "Gujarat", "vadodara": "Gujarat",
    "baroda": "Gujarat", "rajkot": "Gujarat", "gandhinagar": "Gujarat", "bhavnagar": "Gujarat",
    # Rajasthan
    "jaipur": "Rajasthan", "jodhpur": "Rajasthan", "udaipur": "Rajasthan",
    "kota": "Rajasthan", "bikaner": "Rajasthan", "ajmer": "Rajasthan",
    # Uttar Pradesh
    "lucknow": "Uttar Pradesh", "kanpur": "Uttar Pradesh", "varanasi": "Uttar Pradesh",
    "kashi": "Uttar Pradesh", "banaras": "Uttar Pradesh", "agra": "Uttar Pradesh",
    "noida": "Uttar Pradesh", "greater noida": "Uttar Pradesh", "ghaziabad": "Uttar Pradesh",
    "prayagraj": "Uttar Pradesh", "allahabad": "Uttar Pradesh", "meerut": "Uttar Pradesh", "aligarh": "Uttar Pradesh",
    # Bihar
    "patna": "Bihar", "gaya": "Bihar", "muzaffarpur": "Bihar", "bhagalpur": "Bihar", "darbhanga": "Bihar",
    # Odisha
    "bhubaneswar": "Odisha", "cuttack": "Odisha", "rourkela": "Odisha", "puri": "Odisha",
    "berhampur": "Odisha", "sambalpur": "Odisha", "balasore": "Odisha",
    # Jharkhand
    "ranchi": "Jharkhand", "jamshedpur": "Jharkhand", "dhanbad": "Jharkhand", "bokaro": "Jharkhand",
    # Punjab & Chandigarh
    "chandigarh": "Punjab", "ludhiana": "Punjab", "amritsar": "Punjab", "jalandhar": "Punjab", "patiala": "Punjab",
    # Haryana
    "gurugram": "Haryana", "gurgaon": "Haryana", "faridabad": "Haryana",
    "panipat": "Haryana", "ambala": "Haryana", "karnal": "Haryana", "rohtak": "Haryana", "hisar": "Haryana",
    # Assam & North East
    "guwahati": "Assam", "silchar": "Assam", "dibrugarh": "Assam", "jorhat": "Assam",
    "shillong": "Meghalaya", "imphal": "Manipur", "aizawl": "Mizoram", "kohima": "Nagaland",
    "gangtok": "Sikkim", "agartala": "Tripura", "itanagar": "Arunachal Pradesh",
    # Madhya Pradesh
    "bhopal": "Madhya Pradesh", "indore": "Madhya Pradesh", "gwalior": "Madhya Pradesh",
    "jabalpur": "Madhya Pradesh", "ujjain": "Madhya Pradesh",
    # Kerala
    "thiruvananthapuram": "Kerala", "trivandrum": "Kerala", "kochi": "Kerala",
    "cochin": "Kerala", "kozhikode": "Kerala", "calicut": "Kerala", "thrissur": "Kerala",
    # Uttarakhand
    "dehradun": "Uttarakhand", "haridwar": "Uttarakhand", "rishikesh": "Uttarakhand", "roorkee": "Uttarakhand", "nainital": "Uttarakhand",
    # Himachal Pradesh
    "shimla": "Himachal Pradesh", "dharamshala": "Himachal Pradesh", "mandi": "Himachal Pradesh", "solan": "Himachal Pradesh", "kullu": "Himachal Pradesh", "manali": "Himachal Pradesh",
    # Jammu & Kashmir
    "srinagar": "Jammu & Kashmir", "jammu": "Jammu & Kashmir", "anantnag": "Jammu & Kashmir",
    # Chhattisgarh
    "raipur": "Chhattisgarh", "bhilai": "Chhattisgarh", "bilaspur": "Chhattisgarh",
    # Goa
    "panaji": "Goa", "margao": "Goa", "vasco": "Goa", "goa": "Goa",
    # Andhra Pradesh
    "visakhapatnam": "Andhra Pradesh", "vizag": "Andhra Pradesh", "vijayawada": "Andhra Pradesh", "guntur": "Andhra Pradesh", "tirupati": "Andhra Pradesh",
    # Puducherry
    "puducherry": "Puducherry", "pondicherry": "Puducherry",
}

INDIAN_STATES_CANONICAL = [
    "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh",
    "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka",
    "kerala", "madhya pradesh", "maharashtra", "manipur", "meghalaya", "mizoram",
    "nagaland", "odisha", "punjab", "rajasthan", "sikkim", "tamil nadu", "telangana",
    "tripura", "uttar pradesh", "uttarakhand", "west bengal", "delhi", "jammu & kashmir",
    "puducherry", "chandigarh", "ladakh"
]

STATE_ABBREVIATIONS = {
    "wb": "West Bengal", "w.b.": "West Bengal", "west bengal": "West Bengal",
    "up": "Uttar Pradesh", "u.p.": "Uttar Pradesh", "uttar pradesh": "Uttar Pradesh",
    "mp": "Madhya Pradesh", "m.p.": "Madhya Pradesh", "madhya pradesh": "Madhya Pradesh",
    "tn": "Tamil Nadu", "t.n.": "Tamil Nadu", "tamil nadu": "Tamil Nadu",
    "ap": "Andhra Pradesh", "a.p.": "Andhra Pradesh", "andhra pradesh": "Andhra Pradesh",
    "ts": "Telangana", "tg": "Telangana", "telangana": "Telangana",
    "mh": "Maharashtra", "maharashtra": "Maharashtra",
    "ka": "Karnataka", "karnataka": "Karnataka",
    "kl": "Kerala", "kerala": "Kerala",
    "gj": "Gujarat", "gujarat": "Gujarat",
    "rj": "Rajasthan", "rajasthan": "Rajasthan",
    "pb": "Punjab", "punjab": "Punjab",
    "hr": "Haryana", "haryana": "Haryana",
    "or": "Odisha", "od": "Odisha", "odisha": "Odisha", "orissa": "Odisha",
    "dl": "Delhi", "delhi": "Delhi",
    "uk": "Uttarakhand", "u.k.": "Uttarakhand", "uttarakhand": "Uttarakhand", "uttaranchal": "Uttarakhand",
    "hp": "Himachal Pradesh", "h.p.": "Himachal Pradesh", "himachal pradesh": "Himachal Pradesh",
    "jk": "Jammu & Kashmir", "j&k": "Jammu & Kashmir", "jammu & kashmir": "Jammu & Kashmir",
    "jh": "Jharkhand", "jharkhand": "Jharkhand",
    "cg": "Chhattisgarh", "chhattisgarh": "Chhattisgarh",
    "br": "Bihar", "bihar": "Bihar",
    "as": "Assam", "assam": "Assam",
    "ga": "Goa", "goa": "Goa",
    "py": "Puducherry", "puducherry": "Puducherry",
}


def extract_context_from_text(
    text: str,
    current_context: Optional[UserContext] = None,
    awaiting_slot: Optional[str] = None
) -> UserContext:
    """
    Extracts demographic variables from query text using heuristics and awaiting-slot context.
    """
    ctx = current_context or UserContext()
    t = text.lower().strip()

    # 1. State / City / Abbreviation extraction
    # A. Check direct canonical state names
    for state in INDIAN_STATES_CANONICAL:
        if re.search(r'\b' + re.escape(state) + r'\b', t):
            ctx.set_confirmed("state", state.title())
            break

    # B. Check city to state mapping
    for city, st in CITY_TO_STATE.items():
        if city == "gaya":
            if re.search(r'\b(?:in|at|from|to|near|dist|district)\s+gaya\b', t) or re.search(r'\bgaya\s+(?:city|dist|district|bihar)\b', t):
                ctx.set_confirmed("city", "Gaya")
                ctx.set_confirmed("state", "Bihar")
                break
            continue
        if re.search(r'\b' + re.escape(city) + r'\b', t):
            ctx.set_confirmed("city", city.title())
            ctx.set_confirmed("state", st)
            break

    # C. Check state abbreviations
    if not ctx.get_value("state"):
        for abbr, st in STATE_ABBREVIATIONS.items():
            if re.search(r'\b' + re.escape(abbr) + r'\b', t):
                ctx.set_confirmed("state", st)
                break

    # 2. Targeted awaiting-slot resolution for short/direct answers
    if awaiting_slot:
        slot_lower = awaiting_slot.lower()
        if slot_lower in ("state", "location", "city"):
            if not ctx.get_value("state"):
                for city, st in CITY_TO_STATE.items():
                    if city in t:
                        ctx.set_confirmed("city", city.title())
                        ctx.set_confirmed("state", st)
                        break
        elif slot_lower in ("age", "user_age"):
            m = re.search(r'\b(\d{1,2})\b', t)
            if m:
                ctx.set_confirmed("age", int(m.group(1)))
        elif slot_lower in ("income", "annual_income", "family_income"):
            m = re.search(r'(?:₹|rs\.?)?\s*([\d,]+(?:\s*(?:lakh|lac|k|crore|cr))?)', t)
            if m and m.group(1):
                ctx.set_confirmed("annual_income", m.group(1).strip())
        elif slot_lower in ("caste", "category", "social_category"):
            for c in ["st", "sc", "obc", "ews", "general"]:
                if re.search(r'\b' + c + r'\b', t):
                    ctx.set_confirmed("caste", c.upper() if c != "general" else "General")
                    break
        elif slot_lower in ("course", "student_class", "education_level", "education"):
            courses = ["btech", "b.tech", "be", "b.e", "bsc", "b.sc", "bcom", "b.com", "ba", "b.a", "mbbs", "bed", "b.ed", "llb", "mtech", "msc", "mba", "phd", "diploma", "iti"]
            for crs in courses:
                if crs in t:
                    ctx.set_confirmed("course", crs.upper())
                    ctx.set_confirmed("education_level", "Undergraduate" if crs not in ["mtech", "msc", "mba", "phd"] else "Postgraduate")
                    break

    # 3. Student class / Education / Course
    courses_map = {
        "btech": ("B.Tech", "Undergraduate"),
        "b.tech": ("B.Tech", "Undergraduate"),
        "be": ("B.E", "Undergraduate"),
        "b.e": ("B.E", "Undergraduate"),
        "b.sc": ("B.Sc", "Undergraduate"),
        "bsc": ("B.Sc", "Undergraduate"),
        "b.com": ("B.Com", "Undergraduate"),
        "bcom": ("B.Com", "Undergraduate"),
        "b.a": ("B.A", "Undergraduate"),
        "ba": ("B.A", "Undergraduate"),
        "mbbs": ("MBBS", "Undergraduate"),
        "b.ed": ("B.Ed", "Undergraduate"),
        "bed": ("B.Ed", "Undergraduate"),
        "llb": ("LLB", "Undergraduate"),
        "mtech": ("M.Tech", "Postgraduate"),
        "m.tech": ("M.Tech", "Postgraduate"),
        "msc": ("M.Sc", "Postgraduate"),
        "m.sc": ("M.Sc", "Postgraduate"),
        "mba": ("MBA", "Postgraduate"),
        "phd": ("Ph.D", "Postgraduate"),
        "diploma": ("Diploma", "Diploma / Polytechnic"),
        "polytechnic": ("Polytechnic", "Diploma / Polytechnic"),
        "iti": ("ITI", "Vocational"),
    }
    for key, (course_name, ed_level) in courses_map.items():
        if re.search(r'\b' + re.escape(key) + r'\b', t):
            ctx.set_confirmed("course", course_name)
            ctx.set_confirmed("education_level", ed_level)
            break

    class_match = re.search(r'\b(?:class|std|standard|grade)\s*(\d+|x|xi|xii|ix|viii|iv|v|vi|vii)\b', t, re.I)
    if class_match:
        ctx.set_confirmed("student_class", f"Class {class_match.group(1).upper()}")
    if "matric" in t or "10th" in t or "class 10" in t:
        ctx.set_confirmed("student_class", "Class 10 (Matric)")
    elif "12th" in t or "class 12" in t or "intermediate" in t:
        ctx.set_confirmed("student_class", "Class 12 (Higher Secondary)")
    elif "undergraduate" in t or "degree" in t or "college" in t or "higher education" in t:
        if not ctx.get_value("education_level"):
            ctx.set_confirmed("education_level", "Undergraduate")
    elif "postgraduate" in t or "master" in t:
        if not ctx.get_value("education_level"):
            ctx.set_confirmed("education_level", "Postgraduate")

    # 4. Caste / Social Category
    if re.search(r'\bst\b', t) or "scheduled tribe" in t:
        ctx.set_confirmed("caste", "ST")
    elif re.search(r'\bsc\b', t) or "scheduled caste" in t:
        ctx.set_confirmed("caste", "SC")
    elif re.search(r'\bobc\b', t) or "other backward class" in t:
        ctx.set_confirmed("caste", "OBC")
    elif re.search(r'\bews\b', t) or "economically weaker" in t:
        ctx.set_confirmed("caste", "EWS")
    elif re.search(r'\bgeneral\b', t):
        ctx.set_confirmed("caste", "General")

    # 5. Gender
    if "female" in t or "girl" in t or "woman" in t or "women" in t or "daughter" in t or "mother" in t:
        ctx.set_confirmed("gender", "Female")
    elif "male" in t or "boy" in t or "man" in t or "son" in t or "father" in t:
        ctx.set_confirmed("gender", "Male")

    # 6. Parent / User Occupation
    if "farmer" in t or "kisan" in t or "agriculture" in t or "cultivator" in t:
        ctx.set_confirmed("occupation", "Farmer")
    elif "salt worker" in t or "salt-worker" in t or "salt pan" in t:
        ctx.set_confirmed("parent_occupation", "Salt Worker")
    elif "construction worker" in t or "labour" in t or "laborer" in t:
        ctx.set_confirmed("occupation", "Construction Worker")
    elif "artisan" in t or "weaver" in t or "handicraft" in t:
        ctx.set_confirmed("occupation", "Artisan / Weaver")

    # 7. Age extraction
    age_match = re.search(r'\b(?:i am|age is|aged|age)\s*(\d{1,2})\b', t)
    if age_match:
        ctx.set_confirmed("age", int(age_match.group(1)))

    # 8. Income extraction
    inc_match = re.search(r'(?:income|earn|salary)[^\d]*?(?:₹|rs\.?)?\s*([\d,]+(?:\s*(?:lakh|lac|k|crore|cr))?)', t)
    if inc_match:
        ctx.set_confirmed("annual_income", inc_match.group(1).strip())

    return ctx


def check_context_sufficiency_for_query(
    query: str,
    context: UserContext,
    target_scheme_name: Optional[str] = None
) -> Tuple[bool, Optional[str], Optional[List[str]], Optional[str]]:
    """
    Evaluates if context is sufficient to answer the query or if clarification is needed.
    Returns: (is_sufficient, clarification_question, option_list, missing_slot_name)
    """
    q = query.lower()

    # If the user asks about state schemes or general scheme eligibility without mentioning state
    scheme_intent_words = ["scheme", "yojana", "eligible", "eligibility", "scholarship", "apply", "benefit", "college", "admission"]
    is_scheme_query = any(w in q for w in scheme_intent_words)

    if not is_scheme_query:
        return True, None, None, None

    # Central scheme markers - if query is asking for Central schemes or central college/exam, do not block on state
    central_markers = ["central", "national", "pm ", "pm-", "pradhan mantri", "all india", "union", "upsc", "central college", "central university"]
    if any(m in q for m in central_markers):
        return True, None, None, None

    # Check State
    user_state = context.get_value("state")
    if not user_state:
        # If target scheme is already identified from previous conversation context, allow through
        if target_scheme_name:
            return True, None, None, None
        return False, (
            "To give you the exact eligibility criteria and state-specific benefits, "
            "could you please select or tell me your state of residence?"
        ), [
            "Odisha", "Gujarat", "Haryana", "Madhya Pradesh", "Rajasthan", "Uttar Pradesh", "Other / All India"
        ], "state"

    # Check for specific scheme eligibility query
    if target_scheme_name:
        from agents.tools.scheme_tools import identify_missing_information
        missing = identify_missing_information(target_scheme_name, context.to_profile_dict())
        for item in missing:
            if item.get("is_critical"):
                slot_name = item.get("variable", "details")
                return False, item["question"], item.get("options"), slot_name

    return True, None, None, None


def get_missing_legal_context(query: str, context: Optional[UserContext] = None) -> List[str]:
    """
    Identifies which decision-critical facts are missing from a legal/crime/dispute scenario:
    - 'state': Needed for police jurisdiction and state-specific complaint portals.
    - 'fir_status': Needed to determine whether to file fresh FIR, invoke 154(3) SP complaint, or 156(3) Magistrate.
    - 'timeline': Needed for emergency intervention (e.g. 1930 golden hour, injury MLC).
    - 'evidence': Needed to guide documentation (chats, bank UTR, CCTV, medical report).
    """
    missing = []
    q = query.lower()

    # Check if this is an incident/dispute inquiry rather than a pure academic definition (e.g. "What is IPC 302?")
    is_academic = re.search(r'^\s*(?:what is|define|explain|meaning of)\s*(?:section|ipc|crpc|bns|bnss)?\s*\d+', q)
    if is_academic:
        return []

    # Check state / location
    has_state = False
    if context and context.get_value("state"):
        has_state = True
    elif any(s in q for s in INDIAN_STATES_CANONICAL) or any(c in q for c in CITY_TO_STATE.keys()):
        has_state = True
    if not has_state:
        missing.append("state_location")

    # Check FIR / Police action status
    fir_words = ["fir", "police station", "complaint", "shikayat", "sho", "reported", "daroga", "thana"]
    if not any(w in q for w in fir_words):
        missing.append("police_report_status")

    # Check Evidence / Documentation
    evidence_words = ["cctv", "receipt", "utr", "transaction", "chat", "screenshot", "witness", "gawah", "saboot", "proof", "record", "mlc", "medical"]
    if not any(w in q for w in evidence_words):
        missing.append("evidence_available")

    return missing
