"""
Comprehensive Indian Legal Statutory Database & Retrieval Service.
Covers:
- Indian Penal Code (IPC, 1860) & Bharatiya Nyaya Sanhita (BNS, 2023)
- Code of Criminal Procedure (CrPC, 1973) & Bharatiya Nagarik Suraksha Sanhita (BNSS, 2023)
- Information Technology Act (IT Act, 2000)
- Protection of Women from Domestic Violence Act (PWDVA, 2005)
- Negotiable Instruments Act (NI Act 1881 - Section 138 Cheque Bounce)
- Procedural rights: FIR (154 CrPC / 173 BNSS), Police Refusal Remedies (154(3) & 156(3) CrPC),
  Notice before arrest (41A CrPC / 35 BNSS), Bail (436/437/438/439 CrPC), Zero FIR, 1930 Cyber Helpline.
"""
import re
from typing import Dict, Any, List, Optional, Tuple

LEGAL_STATUTES: Dict[str, Dict[str, Any]] = {
    # ─── CrPC / BNSS Procedural Sections ──────────────────────────
    "CRPC_154": {
        "act": "Code of Criminal Procedure (CrPC)",
        "section": "154",
        "new_act": "Bharatiya Nagarik Suraksha Sanhita (BNSS)",
        "new_section": "173",
        "title": "Information in cognizable cases (First Information Report - FIR)",
        "category": "procedure",
        "nature": "Statutory Duty / Procedure",
        "summary": (
            "Every information relating to the commission of a cognizable offence given to an officer in charge of a police "
            "station shall be reduced to writing and read over to the informant. "
            "A copy of the FIR must be given to the informant immediately, free of cost. "
            "As per Supreme Court landmark ruling in Lalita Kumari v. Govt. of UP (2014), registration of an FIR is MANDATORY "
            "if information discloses a cognizable offence. Police cannot refuse or delay."
        ),
        "zero_fir_note": (
            "Zero FIR: A victim can file an FIR at ANY police station in India regardless of territorial jurisdiction. "
            "The station must register it as 'Zero FIR' and transfer it to the jurisdictional police station for investigation."
        ),
        "punishment": "N/A (Procedural provision)",
        "court": "Police Station / Jurisdictional Magistrate",
        "keywords": ["fir", "first information report", "police complaint", "zero fir", "lalita kumari", "thaney", "report crime"]
    },
    "CRPC_154_3": {
        "act": "Code of Criminal Procedure (CrPC)",
        "section": "154(3)",
        "new_act": "Bharatiya Nagarik Suraksha Sanhita (BNSS)",
        "new_section": "173(4)",
        "title": "Remedy when Police Officer Refuses to Register FIR",
        "category": "procedure",
        "nature": "Administrative Remedy against Police Inaction",
        "summary": (
            "If the Station House Officer (SHO) refuses to register an FIR for a cognizable offence, the aggrieved person "
            "has the statutory right to send the substance of the complaint in writing by registered post or email to the "
            "Superintendent of Police (SP) / Senior Superintendent of Police (SSP) / Deputy Commissioner of Police (DCP). "
            "The SP/DCP, if satisfied, must either investigate the case or direct a subordinate officer to investigate."
        ),
        "punishment": "Police officer refusing FIR in specific offences (e.g. against women) is punishable under Section 166A IPC / 199 BNS with up to 2 years imprisonment.",
        "court": "Superintendent of Police (SP) / DCP Office",
        "keywords": ["police refused fir", "fir nahi likhi", "police not registering", "sho refused", "superintendent of police", "sp complaint", "sp ko shikayat"]
    },
    "CRPC_156_3": {
        "act": "Code of Criminal Procedure (CrPC)",
        "section": "156(3)",
        "new_act": "Bharatiya Nagarik Suraksha Sanhita (BNSS)",
        "new_section": "175(3)",
        "title": "Power of Judicial Magistrate to Order Police Investigation / FIR",
        "category": "procedure",
        "nature": "Judicial Remedy",
        "summary": (
            "Any Magistrate empowered under Section 190 CrPC may order an investigation by the police for any cognizable offence. "
            "When police and the SP refuse to lodge an FIR, the citizen can file an application under Section 156(3) CrPC before "
            "the Judicial / Metropolitan Magistrate with an affidavit. The Magistrate can direct the police station to register an "
            "FIR and submit an investigation report."
        ),
        "punishment": "Judicial direction to police",
        "court": "Court of Judicial Magistrate First Class (JMFC) / Metropolitan Magistrate (MM)",
        "keywords": ["magistrate fir", "156(3)", "156 3", "court order for fir", "magistrate investigation", "court se fir"]
    },
    "CRPC_41A": {
        "act": "Code of Criminal Procedure (CrPC)",
        "section": "41A",
        "new_act": "Bharatiya Nagarik Suraksha Sanhita (BNSS)",
        "new_section": "35(3)",
        "title": "Notice of Appearance before Police Officer (Protection Against Arbitrary Arrest)",
        "category": "procedure",
        "nature": "Citizen Safeguard against Arrest",
        "summary": (
            "For offences where the maximum punishment is imprisonment for 7 years or less, the police officer CANNOT routinely arrest the accused. "
            "The officer MUST issue a Notice of Appearance under Section 41A CrPC directing the person to appear for questioning. "
            "As held in Arnesh Kumar v. State of Bihar (2014) and Satender Kumar Antil (2022), arrest without complying with 41A is unlawful "
            "and invites contempt of court against the police officer."
        ),
        "punishment": "Procedural safeguard",
        "court": "Investigating Agency / Magistrate",
        "keywords": ["41a", "notice of appearance", "arnesh kumar", "police notice", "arrest protection", "bina warrant arrest"]
    },
    "CRPC_46": {
        "act": "Code of Criminal Procedure (CrPC)",
        "section": "46",
        "new_act": "Bharatiya Nagarik Suraksha Sanhita (BNSS)",
        "new_section": "43",
        "title": "Arrest How Made & Special Protections for Women",
        "category": "procedure",
        "nature": "Human Rights Safeguard",
        "summary": (
            "Police cannot touch a woman while arresting unless the arresting officer is a female officer. "
            "Except in exceptional circumstances, NO WOMAN shall be arrested after sunset and before sunrise (night arrest prohibited) "
            "without the prior written permission of the Judicial Magistrate First Class."
        ),
        "punishment": "Safeguard",
        "court": "Magistrate Court",
        "keywords": ["women arrest", "arrest timing", "sunset sunrise arrest", "mahila girftari"]
    },
    "CRPC_50": {
        "act": "Code of Criminal Procedure (CrPC)",
        "section": "50 & 50A",
        "new_act": "Bharatiya Nagarik Suraksha Sanhita (BNSS)",
        "new_section": "47 & 48",
        "title": "Person Arrested to be Informed of Grounds of Arrest and Right to Bail",
        "category": "procedure",
        "nature": "Fundamental Statutory Right",
        "summary": (
            "Every police officer arresting any person without warrant shall forthwith communicate to him full particulars of the offence "
            "and the grounds for such arrest. In bailable offences, police must inform the accused that they are entitled to be released on bail. "
            "Under 50A and D.K. Basu guidelines, police MUST immediately inform a nominated friend, relative, or family member about the arrest."
        ),
        "punishment": "Safeguard",
        "court": "Magistrate Court",
        "keywords": ["grounds of arrest", "dk basu", "arrest memo", "right to inform family", "girftari ke niyam"]
    },
    "CRPC_57": {
        "act": "Code of Criminal Procedure (CrPC)",
        "section": "57",
        "new_act": "Bharatiya Nagarik Suraksha Sanhita (BNSS)",
        "new_section": "58",
        "title": "Maximum 24-Hour Police Custody Without Magistrate Order",
        "category": "procedure",
        "nature": "Constitutional & Statutory Limit",
        "summary": (
            "No police officer shall detain in custody a person arrested without warrant for a longer period than under all circumstances of the case is reasonable, "
            "and such period shall NOT, in the absence of a special order under Section 167, exceed twenty-four hours (exclusive of travel time)."
        ),
        "punishment": "Illegal detention / Habeas Corpus remedy",
        "court": "Nearest Judicial Magistrate",
        "keywords": ["24 hours custody", "remand", "police detention", "hawaalat"]
    },
    "CRPC_167": {
        "act": "Code of Criminal Procedure (CrPC)",
        "section": "167",
        "new_act": "Bharatiya Nagarik Suraksha Sanhita (BNSS)",
        "new_section": "187",
        "title": "Remand & Statutory / Default Bail",
        "category": "procedure",
        "nature": "Bail & Custody Provision",
        "summary": (
            "Magistrate can authorise detention in police custody up to 15 days, and judicial custody up to 60 days (for offences punishable with up to 10 yrs) "
            "or 90 days (for offences punishable with death, life imprisonment, or >10 yrs). "
            "DEFAULT / STATUTORY BAIL: If the police fail to file the chargesheet within the 60 or 90 day window, the accused acquires an ABSOLUTE "
            "indefeasible right to bail upon furnishing bail bonds."
        ),
        "punishment": "Bail entitlement",
        "court": "Court of Judicial Magistrate / Sessions",
        "keywords": ["default bail", "statutory bail", "60 days bail", "90 days bail", "chargesheet delay"]
    },
    "CRPC_436": {
        "act": "Code of Criminal Procedure (CrPC)",
        "section": "436",
        "new_act": "Bharatiya Nagarik Suraksha Sanhita (BNSS)",
        "new_section": "478",
        "title": "Bail in Bailable Offences (Matter of Absolute Right)",
        "category": "procedure",
        "nature": "Absolute Right",
        "summary": (
            "In all bailable offences, bail is a matter of statutory right, NOT judicial discretion. "
            "The police officer in charge of the station or the Court MUST release the accused upon execution of a personal bond with or without sureties. "
            "If an indigent person cannot furnish bail within a week, they must be released on a personal bond without sureties."
        ),
        "punishment": "Bail granted as a right",
        "court": "Police Station / Magistrate Court",
        "keywords": ["bailable offence", "bailable bail", "zamanat", "bail as right", "bailable sections"]
    },
    "CRPC_437": {
        "act": "Code of Criminal Procedure (CrPC)",
        "section": "437",
        "new_act": "Bharatiya Nagarik Suraksha Sanhita (BNSS)",
        "new_section": "480",
        "title": "Bail in Non-Bailable Offences by Magistrate Court",
        "category": "procedure",
        "nature": "Discretionary Judicial Power",
        "summary": (
            "When a person accused of a non-bailable offence appears before a Magistrate, bail may be granted at the discretion of the court. "
            "Bail shall generally not be granted if there appear reasonable grounds for believing that the accused has been guilty of an offence punishable with death or life imprisonment. "
            "SPECIAL PROVISO: Court may direct that any person under 16 years of age, or any woman, or any sick or infirm person, be released on bail even in serious offences."
        ),
        "punishment": "Judicial Discretion",
        "court": "Court of Judicial Magistrate",
        "keywords": ["non bailable bail", "magistrate bail", "bail for women", "regular bail magistrate"]
    },
    "CRPC_438": {
        "act": "Code of Criminal Procedure (CrPC)",
        "section": "438",
        "new_act": "Bharatiya Nagarik Suraksha Sanhita (BNSS)",
        "new_section": "482",
        "title": "Anticipatory Bail (Direction for Grant of Bail to Person Apprehending Arrest)",
        "category": "procedure",
        "nature": "Pre-arrest Relief",
        "summary": (
            "Where any person has reason to believe that he may be arrested on accusation of having committed a non-bailable offence, "
            "he may apply to the Court of Session or the High Court for anticipatory bail. "
            "If granted, in the event of such arrest, the police officer MUST immediately release the applicant on bail upon furnishing bond. "
            "Criteria: Gravity of accusation, antecedents of applicant, possibility of fleeing from justice, and whether accusation is made with the object of injuring or humiliating."
        ),
        "punishment": "Pre-arrest protection",
        "court": "Court of Session / High Court",
        "keywords": ["anticipatory bail", "arrest se pehle bail", "girftari se bachav", "sessions bail", " अग्रिम जमानत"]
    },
    "CRPC_439": {
        "act": "Code of Criminal Procedure (CrPC)",
        "section": "439",
        "new_act": "Bharatiya Nagarik Suraksha Sanhita (BNSS)",
        "new_section": "483",
        "title": "Special Powers of High Court or Court of Session Regarding Bail (Regular Bail)",
        "category": "procedure",
        "nature": "Higher Court Bail Power",
        "summary": (
            "A High Court or Court of Session has wide powers to direct that any person accused of an offence and in custody be released on bail, "
            "and may impose any condition which it considers necessary. It also has the power to cancel bail."
        ),
        "punishment": "Regular Bail Relief",
        "court": "Sessions Court / High Court",
        "keywords": ["regular bail", "sessions court bail", "high court bail", "zamanat aavedan"]
    },
    "CRPC_125": {
        "act": "Code of Criminal Procedure (CrPC)",
        "section": "125",
        "new_act": "Bharatiya Nagarik Suraksha Sanhita (BNSS)",
        "new_section": "144",
        "title": "Order for Maintenance of Wives, Children, and Parents",
        "category": "procedure",
        "nature": "Social Welfare & Summary Remedy",
        "summary": (
            "Any person having sufficient means who neglects or refuses to maintain his wife (unable to maintain herself), legitimate or illegitimate minor children, "
            "or father/mother (unable to maintain themselves) can be ordered by a Judicial Magistrate to pay a monthly maintenance allowance. "
            "Magistrate can also grant Interim Maintenance and expenses of proceeding during the pendency of the application."
        ),
        "punishment": "Warrant for levy of fine or imprisonment up to 1 month for each month's unpaid maintenance",
        "court": "Family Court / Judicial Magistrate First Class",
        "keywords": ["maintenance", "kharcha", "125 crpc", "patni ka kharcha", "parents maintenance", "child maintenance"]
    },
    "CRPC_482": {
        "act": "Code of Criminal Procedure (CrPC)",
        "section": "482",
        "new_act": "Bharatiya Nagarik Suraksha Sanhita (BNSS)",
        "new_section": "528",
        "title": "Inherent Powers of High Court (Quashing of False FIR / Criminal Proceedings)",
        "category": "procedure",
        "nature": "Constitutional & Inherent Power",
        "summary": (
            "Nothing in this Code shall be deemed to limit or affect the inherent powers of the High Court to make such orders as may be necessary "
            "to give effect to any order under this Code, or to prevent abuse of the process of any court or otherwise to secure the ends of justice. "
            "Widely used to petition the High Court to quash false, malicious, settled, or groundless FIRs and criminal chargesheets (*State of Haryana v. Bhajan Lal*)."
        ),
        "punishment": "Quashing of FIR / Criminal Case",
        "court": "High Court",
        "keywords": ["quash fir", "482 petition", "false fir quash", "high court 482", "jhuthi fir cancel"]
    },
    "CRPC_320": {
        "act": "Code of Criminal Procedure (CrPC)",
        "section": "320",
        "new_act": "Bharatiya Nagarik Suraksha Sanhita (BNSS)",
        "new_section": "359",
        "title": "Compounding of Offences (Legal Settlement / Compromise)",
        "category": "procedure",
        "nature": "Settlement Mechanism",
        "summary": (
            "Specifies which criminal offences can be legally compounded (settled) between the victim and accused. "
            "Category 1: Compoundable by the victim without court permission (e.g. Section 323 Hurt, 504 Insult, 506 Intimidation). "
            "Category 2: Compoundable ONLY with the permission of the Court (e.g. Section 379 Theft, 420 Cheating, 406 Breach of Trust). "
            "Compounding has the effect of an acquittal of the accused."
        ),
        "punishment": "Case closed with acquittal",
        "court": "Trial Magistrate / Sessions",
        "keywords": ["compoundable", "compromise in criminal case", "samjhauta", "case wapas lena"]
    },

    # ─── IPC / BNS Penal Offences ────────────────────────────────
    "IPC_420": {
        "act": "Indian Penal Code (IPC)",
        "section": "420",
        "new_act": "Bharatiya Nyaya Sanhita (BNS)",
        "new_section": "318(4)",
        "title": "Cheating and dishonestly inducing delivery of property",
        "category": "penal",
        "nature": "Cognizable | Non-Bailable | Compoundable with Court Permission",
        "summary": (
            "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy "
            "the whole or any part of a valuable security. Requires dishonest intention at the very inception of the transaction."
        ),
        "punishment": "Imprisonment up to 7 years + Fine",
        "court": "Magistrate of the First Class",
        "keywords": ["420", "cheating", "fraud", "dhokhadhadi", "scam", "financial fraud", "online fraud", "paise hadapna"]
    },
    "IPC_406": {
        "act": "Indian Penal Code (IPC)",
        "section": "406",
        "new_act": "Bharatiya Nyaya Sanhita (BNS)",
        "new_section": "316",
        "title": "Punishment for Criminal Breach of Trust",
        "category": "penal",
        "nature": "Cognizable | Non-Bailable | Compoundable with Court Permission",
        "summary": (
            "Whoever commits criminal breach of trust (entrusted with property and dishonestly misappropriates or converts it to his own use, "
            "or dishonestly uses or disposes of that property in violation of any direction of law or contract)."
        ),
        "punishment": "Imprisonment up to 3 years, or fine, or both",
        "court": "Magistrate of the First Class",
        "keywords": ["406", "breach of trust", "amanat me khayanat", "stridhan", "withholding property", "trust fraud"]
    },
    "IPC_379": {
        "act": "Indian Penal Code (IPC)",
        "section": "379",
        "new_act": "Bharatiya Nyaya Sanhita (BNS)",
        "new_section": "303(2)",
        "title": "Punishment for Theft",
        "category": "penal",
        "nature": "Cognizable | Non-Bailable | Compoundable with Court Permission (if value <= ₹20,000)",
        "summary": (
            "Whoever intends to take dishonestly any movable property out of the possession of any person without that person's consent, "
            "and moves that property in order to such taking, commits theft."
        ),
        "punishment": "Imprisonment up to 3 years, or fine, or both",
        "court": "Any Magistrate",
        "keywords": ["379", "theft", "chori", "stolen", "bike chori", "mobile chori", "purse chori", "car stolen"]
    },
    "BNS_304": {
        "act": "Bharatiya Nyaya Sanhita (BNS)",
        "section": "304",
        "new_act": "Bharatiya Nyaya Sanhita (BNS)",
        "new_section": "304",
        "title": "Snatching (Special provision in new penal law)",
        "category": "penal",
        "nature": "Cognizable | Non-Bailable",
        "summary": (
            "Theft is 'snatching' if, in order to commit theft, the offender suddenly or quickly or forcibly seizes, secures, grabs or takes away "
            "from any person or from his possession any movable property (e.g. mobile snatching, gold chain snatching)."
        ),
        "punishment": "Imprisonment up to 3 years + Fine",
        "court": "Magistrate of the First Class",
        "keywords": ["snatching", "chain snatching", "mobile snatching", "bns 304", "jhapattamari"]
    },
    "IPC_302": {
        "act": "Indian Penal Code (IPC)",
        "section": "302",
        "new_act": "Bharatiya Nyaya Sanhita (BNS)",
        "new_section": "103(1)",
        "title": "Punishment for Murder",
        "category": "penal",
        "nature": "Cognizable | Non-Bailable | Non-Compoundable",
        "summary": (
            "Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine. "
            "Under BNS 103(2), mob lynching on grounds of race, caste, community, sex, place of birth, or language carries death or life imprisonment."
        ),
        "punishment": "Death or Imprisonment for Life + Fine",
        "court": "Court of Session",
        "keywords": ["302", "murder", "hatya", "qatl", "kill", "homicide", "103 bns"]
    },
    "IPC_307": {
        "act": "Indian Penal Code (IPC)",
        "section": "307",
        "new_act": "Bharatiya Nyaya Sanhita (BNS)",
        "new_section": "109",
        "title": "Attempt to Murder",
        "category": "penal",
        "nature": "Cognizable | Non-Bailable | Non-Compoundable",
        "summary": (
            "Whoever does any act with such intention or knowledge, and under such circumstances that, if he by that act caused death, "
            "he would be guilty of murder. If hurt is caused to any person by such act, offender is liable to life imprisonment or up to 10 years."
        ),
        "punishment": "Imprisonment up to 10 years + Fine; If hurt caused: Imprisonment for Life or 10 years",
        "court": "Court of Session",
        "keywords": ["307", "attempt to murder", "jaanleva hamla", "murder attempt", "109 bns"]
    },
    "IPC_323": {
        "act": "Indian Penal Code (IPC)",
        "section": "323",
        "new_act": "Bharatiya Nyaya Sanhita (BNS)",
        "new_section": "115(2)",
        "title": "Punishment for Voluntarily Causing Hurt (Simple Hurt)",
        "category": "penal",
        "nature": "Non-Cognizable | Bailable | Compoundable",
        "summary": (
            "Whoever voluntarily causes bodily pain, disease or infirmity to any person. Non-cognizable (police register NCR unless accompanied by cognizable offence)."
        ),
        "punishment": "Imprisonment up to 1 year, or fine up to ₹1,000, or both",
        "court": "Any Magistrate",
        "keywords": ["323", "simple hurt", "marpeet", "minor injury", "thappad", "beating", "115 bns"]
    },
    "IPC_325": {
        "act": "Indian Penal Code (IPC)",
        "section": "325",
        "new_act": "Bharatiya Nyaya Sanhita (BNS)",
        "new_section": "117(2)",
        "title": "Punishment for Voluntarily Causing Grievous Hurt",
        "category": "penal",
        "nature": "Cognizable | Bailable | Compoundable with Court Permission",
        "summary": (
            "Grievous hurt includes: emasculation, permanent privation of sight of either eye, hearing of either ear, privation of any member or joint, "
            "fracture or dislocation of a bone or tooth, or any hurt which endangers life or causes severe bodily pain for 20 days."
        ),
        "punishment": "Imprisonment up to 7 years + Fine",
        "court": "Any Magistrate",
        "keywords": ["325", "grievous hurt", "fracture", "serious injury", "haddi tootna", "117 bns"]
    },
    "IPC_506": {
        "act": "Indian Penal Code (IPC)",
        "section": "506",
        "new_act": "Bharatiya Nyaya Sanhita (BNS)",
        "new_section": "351(2) & 351(3)",
        "title": "Punishment for Criminal Intimidation",
        "category": "penal",
        "nature": "Non-Cognizable (Part 1) / Cognizable in many States | Bailable | Compoundable",
        "summary": (
            "Whoever threatens another with any injury to his person, reputation or property, or to the person or reputation of anyone in whom that person is interested. "
            "Part 2: If the threat be to cause death or grievous hurt, or destruction of property by fire, the punishment extends to 7 years."
        ),
        "punishment": "Part 1: Up to 2 years or Fine. Part 2 (Threat to cause death/grievous hurt): Imprisonment up to 7 years, or fine, or both.",
        "court": "Magistrate of the First Class",
        "keywords": ["506", "criminal intimidation", "dhamki", "threat to life", "threaten", "jaan se marne ki dhamki", "351 bns"]
    },
    "IPC_504": {
        "act": "Indian Penal Code (IPC)",
        "section": "504",
        "new_act": "Bharatiya Nyaya Sanhita (BNS)",
        "new_section": "352",
        "title": "Intentional Insult with Intent to Provoke Breach of Peace",
        "category": "penal",
        "nature": "Non-Cognizable | Bailable | Compoundable",
        "summary": (
            "Whoever intentionally insults, and thereby gives provocation to any person, intending or knowing it to be likely that such provocation "
            "will cause him to break the public peace, or to commit any other offence."
        ),
        "punishment": "Imprisonment up to 2 years, or fine, or both",
        "court": "Any Magistrate",
        "keywords": ["504", "intentional insult", "gaali galoch", "abuse", "insult", "gali dena", "352 bns"]
    },
    "IPC_498A": {
        "act": "Indian Penal Code (IPC)",
        "section": "498A",
        "new_act": "Bharatiya Nyaya Sanhita (BNS)",
        "new_section": "85 & 86",
        "title": "Husband or relative of husband of a woman subjecting her to cruelty",
        "category": "penal",
        "nature": "Cognizable | Non-Bailable | Non-Compoundable (without High Court / state amendment)",
        "summary": (
            "Whoever, being the husband or relative of the husband of a woman, subjects such woman to cruelty (wilful conduct causing grave injury or danger to life/limb/health, "
            "or harassment with a view to coercing her or any person related to her to meet any unlawful demand for any property or valuable security / dowry). "
            "Notice under Section 41A CrPC is mandatory before arrest (Arnesh Kumar guidelines)."
        ),
        "punishment": "Imprisonment up to 3 years + Fine",
        "court": "Magistrate of the First Class",
        "keywords": ["498a", "cruelty", "dowry harassment", "in laws harassment", "pati sasural", "dahej utpeedan", "85 bns"]
    },
    "IPC_304B": {
        "act": "Indian Penal Code (IPC)",
        "section": "304B",
        "new_act": "Bharatiya Nyaya Sanhita (BNS)",
        "new_section": "80",
        "title": "Dowry Death",
        "category": "penal",
        "nature": "Cognizable | Non-Bailable | Non-Compoundable",
        "summary": (
            "Where the death of a woman is caused by any burns or bodily injury or occurs otherwise than under normal circumstances within seven years of her marriage, "
            "and it is shown that soon before her death she was subjected to cruelty or harassment by her husband or any relative of her husband for, or in connection with, any demand for dowry."
        ),
        "punishment": "Imprisonment for a term not less than 7 years, extending to Imprisonment for Life",
        "court": "Court of Session",
        "keywords": ["304b", "dowry death", "dahej hatya", "death within 7 years marriage", "80 bns"]
    },
    "IPC_376": {
        "act": "Indian Penal Code (IPC)",
        "section": "376",
        "new_act": "Bharatiya Nyaya Sanhita (BNS)",
        "new_section": "64",
        "title": "Punishment for Rape",
        "category": "penal",
        "nature": "Cognizable | Non-Bailable | Non-Compoundable",
        "summary": (
            "Sexual assault without consent or against will. Strict statutory guidelines: statement of victim to be recorded by a woman police officer "
            "or woman magistrate under Section 164(5A) CrPC / 183 BNSS. Medical examination under 164A CrPC / 184 BNSS. Victim identity cannot be disclosed (Section 228A IPC / 73 BNS)."
        ),
        "punishment": "Rigorous imprisonment not less than 10 years up to Life Imprisonment + Fine",
        "court": "Court of Session",
        "keywords": ["376", "rape", "balatkar", "sexual assault", "64 bns", "posh", "pocso"]
    },
    "IPC_354": {
        "act": "Indian Penal Code (IPC)",
        "section": "354",
        "new_act": "Bharatiya Nyaya Sanhita (BNS)",
        "new_section": "74",
        "title": "Assault or criminal force to woman with intent to outrage her modesty",
        "category": "penal",
        "nature": "Cognizable | Non-Bailable",
        "summary": (
            "Whoever assaults or uses criminal force to any woman, intending to outrage or knowing it to be likely that he will thereby outrage her modesty. "
            "Includes Section 354A (Sexual harassment), 354B (Assault with intent to disrobe), 354C (Voyeurism), 354D (Stalking)."
        ),
        "punishment": "Imprisonment not less than 1 year extending to 5 years + Fine",
        "court": "Any Magistrate",
        "keywords": ["354", "outraging modesty", "molestation", "chedchad", "sexual harassment", "stalking", "354a", "354d", "74 bns"]
    },
    "IPC_441_447": {
        "act": "Indian Penal Code (IPC)",
        "section": "447 (read with 441)",
        "new_act": "Bharatiya Nyaya Sanhita (BNS)",
        "new_section": "329(3)",
        "title": "Punishment for Criminal Trespass & Illegal Land/Property Possession",
        "category": "penal",
        "nature": "Cognizable | Bailable | Compoundable",
        "summary": (
            "Whoever enters into or upon property in the possession of another with intent to commit an offence or to intimidate, insult or annoy any person in possession, "
            "or unlawfully remaining there having lawfully entered. For house-trespass (Section 448), punishment extends to 1 year."
        ),
        "punishment": "Imprisonment up to 3 months, or fine up to ₹500, or both. House-trespass: 1 year.",
        "court": "Any Magistrate",
        "keywords": ["criminal trespass", "illegal possession", "kabza", "land grabbing", "ghar me ghusna", "tenant refusal to vacate"]
    },
    "IT_ACT_66D": {
        "act": "Information Technology Act, 2000",
        "section": "66D (read with 66C)",
        "new_act": "Information Technology Act, 2000 (with Section 318 BNS)",
        "new_section": "66D",
        "title": "Punishment for Cheating by Personation by using Computer Resource / Cyber Fraud",
        "category": "cyber",
        "nature": "Cognizable | Bailable | Triable by Magistrate",
        "summary": (
            "Whoever by means of any communication device or computer resource cheats by personating (e.g. fake bank calls, OTP fraud, phishing, "
            "crypto scam, fake lottery/investment fraud). "
            "EMERGENCY REMEDY: Dial National Cyber Crime Helpline '1930' immediately to freeze the money in the receiver's bank/wallet within the golden hour, "
            "and file a complaint on https://cybercrime.gov.in."
        ),
        "punishment": "Imprisonment up to 3 years + Fine up to ₹1,00,000",
        "court": "Court of Judicial Magistrate First Class / Chief Judicial Magistrate",
        "keywords": ["cyber fraud", "online scam", "otp fraud", "upi scam", "bank fraud", "1930", "cybercrime", "phishing", "fake link"]
    },
    "NI_ACT_138": {
        "act": "Negotiable Instruments Act, 1881",
        "section": "138",
        "new_act": "Negotiable Instruments Act, 1881",
        "new_section": "138",
        "title": "Dishonour of Cheque for Insufficiency, etc., of Funds (Cheque Bounce)",
        "category": "commercial_criminal",
        "nature": "Non-Cognizable | Bailable | Compoundable",
        "summary": (
            "Where any cheque drawn by a person on an account maintained by him for payment of any amount of money to another person from out of that account "
            "for the discharge of any legally enforceable debt is returned by the bank unpaid. "
            "PROCEDURE: 1. Cheque presented within validity (3 months). 2. Legal Notice in writing sent to drawer within 30 days of receiving bank memo. "
            "3. Drawer given 15 days to pay. 4. If payment not made within 15 days, Criminal Complaint filed before Magistrate within 30 days."
        ),
        "punishment": "Imprisonment up to 2 years, or fine up to twice the amount of the cheque, or both",
        "court": "Judicial / Metropolitan Magistrate Court having jurisdiction where payee's bank account is located",
        "keywords": ["cheque bounce", "138 ni act", "dishonour of cheque", "bounced cheque", "legal notice for cheque"]
    },
    "PWDVA_2005": {
        "act": "Protection of Women from Domestic Violence Act, 2005",
        "section": "Sections 12, 18, 19, 20, 22",
        "new_act": "Protection of Women from Domestic Violence Act, 2005",
        "new_section": "PWDVA 2005",
        "title": "Civil & Criminal Remedies for Domestic Violence against Women",
        "category": "women_rights",
        "nature": "Civil Protection with Criminal Penalties for Breach",
        "summary": (
            "Protects wives, live-in partners, mothers, or sisters from physical, sexual, verbal, emotional, or economic abuse by domestic relatives. "
            "Key reliefs available before Judicial Magistrate: "
            "1. Protection Orders (Section 18) - restraining abuser from committing violence or contacting victim. "
            "2. Residence Orders (Section 19) - right to reside in shared household; restraining eviction. "
            "3. Monetary Relief (Section 20) - expenses, medical costs, maintenance. "
            "4. Compensation (Section 22) - for emotional distress. "
            "Breach of Protection Order is a COGNIZABLE and NON-BAILABLE criminal offence under Section 31 (up to 1 year jail)."
        ),
        "punishment": "Breach of order: Imprisonment up to 1 year + Fine ₹20,000",
        "court": "Court of Judicial Magistrate First Class / Metropolitan Magistrate",
        "keywords": ["domestic violence", "gharelu hinsa", "pwdva", "protection order", "wife beating", "residence order", "181 helpline"]
    }
}


def lookup_exact_section(code_type: str, section_num: str) -> Optional[Dict[str, Any]]:
    """
    Looks up a section by code type ('ipc', 'crpc', 'bns', 'bnss', 'it', 'ni') and section number ('302', '154', '41a', etc.).
    """
    clean_sec = section_num.upper().replace(" ", "").replace("_", "").replace("SECTION", "").replace("SEC", "")
    target_key_patterns = [
        f"IPC_{clean_sec}",
        f"CRPC_{clean_sec}",
        f"BNS_{clean_sec}",
        f"BNSS_{clean_sec}",
        f"IT_ACT_{clean_sec}",
        f"NI_ACT_{clean_sec}",
    ]

    for key, data in LEGAL_STATUTES.items():
        k_norm = key.replace("_", "").upper()
        if clean_sec in k_norm or k_norm in [p.replace("_", "").upper() for p in target_key_patterns]:
            return data
        # Check title and section fields
        if str(data.get("section", "")).upper() == clean_sec or str(data.get("new_section", "")).upper() == clean_sec:
            return data

    return None


def extract_section_references(query: str) -> List[Dict[str, Any]]:
    """
    Extracts all statutory references mentioned in a query text.
    Handles: 'IPC 302', 'Section 420', 'CrPC 154', 'BNS 103', '41A', '125 CrPC', etc.
    """
    matches = []
    # Pattern to match: optional act name + section + number
    patterns = [
        r'\b(?:ipc|indian penal code)\s*(?:section|sec)?\s*(\d+[a-z]?)\b',
        r'\b(?:crpc|code of criminal procedure|cr\.p\.c\.)\s*(?:section|sec)?\s*(\d+[a-z]?(?:\(\d+\))?)\b',
        r'\b(?:bns|bharatiya nyaya sanhita)\s*(?:section|sec)?\s*(\d+[a-z]?)\b',
        r'\b(?:bnss|bharatiya nagarik suraksha sanhita)\s*(?:section|sec)?\s*(\d+[a-z]?)\b',
        r'\b(?:section|sec|dhara|dhārā)\s*(\d+[a-z]?)\b',
    ]

    for pat in patterns:
        for m in re.finditer(pat, query, re.I):
            sec_num = m.group(1)
            # Find in database
            for key, data in LEGAL_STATUTES.items():
                if data["section"].lower() == sec_num.lower() or data.get("new_section", "").lower() == sec_num.lower():
                    if data not in matches:
                        matches.append(data)
                elif f"_{sec_num.upper()}" in key:
                    if data not in matches:
                        matches.append(data)

    return matches


def search_legal_statutes(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Performs keyword & semantic ranking over Indian Legal Statutes.
    """
    q_lower = query.lower()
    scored = []

    # 1. First check explicit section numbers
    direct_hits = extract_section_references(query)
    for hit in direct_hits:
        scored.append((100.0, hit))

    # Semantic synonym / concept triggers:
    concept_map = {
        ("cheat", "fraud", "scam", "dhokha", "thag", "paise le liye", "money transferred", "defraud"): ["IPC_420", "IT_ACT_66D", "IPC_406"],
        ("theft", "steal", "stolen", "chori", "loot", "snatch", "chura"): ["IPC_379", "BNS_304", "CRPC_154"],
        ("fir", "police", "daroga", "thana", "shikayat", "complaint", "refuse"): ["CRPC_154", "CRPC_154_3", "CRPC_156_3"],
        ("bail", "zamanat", "jail", "arrest", "custody", "girftar", "remand", "hawaalat"): ["CRPC_436", "CRPC_437", "CRPC_438", "CRPC_439", "CRPC_41A", "CRPC_50"],
        ("marpeet", "assault", "beaten", "hit", "injury", "hurt", "chot", "haddi"): ["IPC_323", "IPC_325", "IPC_307"],
        ("threat", "dhamki", "jaan se marne", "threaten", "intimidat"): ["IPC_506", "IPC_504"],
        ("murder", "hatya", "qatl", "jaan se mar"): ["IPC_302", "IPC_307"],
        ("dowry", "dahej", "cruelty", "husband", "in laws", "sasural", "domestic violence", "gharelu hinsa"): ["IPC_498A", "IPC_304B", "PWDVA_2005"],
        ("rape", "balatkar", "molest", "chedchad", "sexual", "stalk", "eve tease"): ["IPC_376", "IPC_354"],
        ("cheque", "check", "bounce", "dishonour", "138"): ["NI_ACT_138"],
        ("maintenance", "kharcha", "patni ka kharcha"): ["CRPC_125"],
        ("landlord", "tenant", "kirayedar", "makan malik", "kabza", "trespass", "evict"): ["IPC_441_447"],
        ("quash", "cancel fir", "false fir"): ["CRPC_482"],
    }

    concept_boosts = set()
    for triggers, keys in concept_map.items():
        if any(tr in q_lower for tr in triggers):
            for k in keys:
                concept_boosts.add(k)

    # 2. Score remaining provisions based on keywords and titles
    for key, item in LEGAL_STATUTES.items():
        if item in [h[1] for h in scored]:
            continue

        score = 0.0

        if key in concept_boosts:
            score += 40.0

        # Keyword match
        for kw in item.get("keywords", []):
            if kw in q_lower:
                score += 15.0

        # Title match
        title_lower = item.get("title", "").lower()
        title_words = [w for w in title_lower.split() if len(w) > 3]
        for tw in title_words:
            if tw in q_lower:
                score += 5.0

        # Summary match
        summary_lower = item.get("summary", "").lower()
        if any(term in q_lower for term in ["fir", "police", "arrest", "bail", "cheat", "theft", "murder", "assault", "threat", "dowry", "scam"]):
            for term in ["fir", "police", "arrest", "bail", "cheat", "theft", "murder", "assault", "threat", "dowry", "scam"]:
                if term in q_lower and term in summary_lower:
                    score += 8.0

        if score > 0:
            scored.append((score, item))

    # Sort descending
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]


def format_statutes_for_llm(statutes: List[Dict[str, Any]]) -> str:
    """
    Formats statutory records into high-density context for LLM prompt.
    """
    if not statutes:
        return ""

    blocks = []
    for s in statutes:
        ipc_crpc_part = f"{s.get('act', 'Act')} - Section {s.get('section', '')}"
        bns_part = f"Corresponding BNS/BNSS: {s.get('new_act', '')} Section {s.get('new_section', '')}" if s.get('new_section') else ""
        nature_part = f"Nature: {s.get('nature', 'Statutory')}"
        punishment_part = f"Punishment: {s.get('punishment', 'N/A')}"
        court_part = f"Jurisdiction/Court: {s.get('court', 'Competent Court')}"
        summary_part = f"Provisions & Rules: {s.get('summary', '')}"

        extra = ""
        if s.get("zero_fir_note"):
            extra += f"\nNote: {s.get('zero_fir_note')}"

        block = (
            f"=== [{ipc_crpc_part}] ===\n"
            f"Title: {s.get('title', '')}\n"
            f"{bns_part}\n"
            f"{nature_part} | {punishment_part}\n"
            f"{court_part}\n"
            f"{summary_part}{extra}\n"
        )
        blocks.append(block)

    return "\n".join(blocks)
