import re
from typing import Dict, Any, Optional

class SafetyGuard:
    """
    Hospital clinical safety guardrail.
    Enforces:
    1. Emergency symptom short-circuit detection (bypasses standard conversational RAG).
    2. Strict non-prescription / dosage modification invariant (AI never alters doses).
    """

    EMERGENCY_PATTERNS = [
        r"\bchest\s+(?:pain|pressure|tightness|crushing)\b",
        r"\b(?:left\s+arm|jaw|neck)\s+(?:pain|numbness|tingling)\b",
        r"\b(?:can'?t|cannot|unable\s+to)\s+breathe\b",
        r"\bsevere\s+(?:shortness\s+of\s+breath|dyspnea)\b",
        r"\b(?:face|facial)\s+(?:droop|drooping|numbness)\b",
        r"\b(?:sudden|slurred)\s+speech\b",
        r"\bpassed\s+out|lost\s+consciousness|fainted\b",
        r"\bextreme\s+bleeding|coughing\s+blood\b",
        r"\banaphylaxis|throat\s+closing\b"
    ]

    MEDICATION_MODIFICATION_PATTERNS = [
        r"\b(?:double|increase|decrease|change|stop|alter|prescribe)\s+(?:my\s+)?(?:dose|dosage|medication|medicine|pill)\b",
        r"\bcan\s+i\s+(?:double|take\s+two|skip|stop|reduce)\b",
        r"\bmissed\s+(?:my\s+)?(?:morning|evening|afternoon|scheduled)?\s*(?:dose|medicine|medication|pill).*?(?:double|take\s+two|what\s+should\s+i\s+do)\b",
        r"\bprescribe\s+(?:me|something)\b",
        r"\bwhat\s+(?:can|should)\s+i\s+take\s+for\b"
    ]

    @classmethod
    def evaluate_query(cls, user_message: str) -> Optional[Dict[str, Any]]:
        text = user_message.lower().strip()

        # 1. Check for Emergency
        for pattern in cls.EMERGENCY_PATTERNS:
            if re.search(pattern, text):
                return {
                    "guardrail_triggered": "EMERGENCY_TRIAGE",
                    "severity": "CRITICAL",
                    "short_circuit": True,
                    "response": (
                        "🚨 **URGENT MEDICAL ALERT: IMMEDIATE ATTENTION REQUIRED**\n\n"
                        "Based on the symptoms you reported (such as acute chest discomfort, difficulty breathing, or neurological symptoms), "
                        "this could represent a medical emergency.\n\n"
                        "**IMMEDIATE ACTION STEPS:**\n"
                        "1. **Call 911 (or your local emergency services) immediately.** Do not drive yourself to the emergency department.\n"
                        "2. Our hospital emergency hotline: **+1 (800) 555-9111**.\n"
                        "3. Unlock your door and sit in a comfortable resting position while awaiting first responders.\n\n"
                        "*The AI Assistant cannot evaluate or manage acute medical emergencies.*"
                    ),
                    "action_card": {
                        "type": "EMERGENCY_CALL_CARD",
                        "title": "Call Hospital Emergency Department",
                        "phone": "+1-800-555-9111",
                        "hotline_label": "Emergency Direct Line: 911"
                    }
                }

        # 2. Check for Medication Modification / Self-Prescription Invariant
        for pattern in cls.MEDICATION_MODIFICATION_PATTERNS:
            if re.search(pattern, text):
                return {
                    "guardrail_triggered": "MEDICATION_SAFETY_INVARIANT",
                    "severity": "WARNING",
                    "short_circuit": True,
                    "response": (
                        "⚠️ **Clinical Medication Safety Notice**\n\n"
                        "As a hospital AI assistant, **I am not permitted to prescribe medications or change your dosages.** "
                        "Medication regimens must only be modified by your attending physician.\n\n"
                        "**Approved Hospital Clinical Guidance for Missed Doses:**\n"
                        "• **Never double up:** Do not take two doses at once to make up for a missed dose.\n"
                        "• If your next scheduled dose is several hours away, take your prescribed dose as soon as remembered.\n"
                        "• If it is almost time for your next regular dose, skip the missed dose and resume your standard timetable.\n\n"
                        "Would you like me to send a direct clinical message to **Dr. Robert Chen** or connect you to the hospital pharmacy helpline?"
                    ),
                    "action_card": {
                        "type": "CLINICAL_ESCALATION_CARD",
                        "title": "Contact Prescribing Clinician",
                        "doctor": "Dr. Robert Chen",
                        "department": "Cardiology",
                        "phone": "+1-555-019-2000"
                    }
                }

        return None
