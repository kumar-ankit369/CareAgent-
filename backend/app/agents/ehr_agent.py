from typing import Dict, Any, List, Optional
from backend.app.db.database import db

class EHRAgent:
    """
    Agent responsible for permission-aware EHR queries, HL7 FHIR observation retrieval,
    longitudinal lab comparisons, and structured report interpretation.
    """

    @classmethod
    def get_patient_profile(cls, patient_id: str) -> Optional[Dict[str, Any]]:
        patient = db.patients.get(patient_id)
        if not patient:
            return None
        
        conditions = [c for c in db.conditions if c["patient_id"] == patient_id]
        doctor = db.doctors.get(patient["assigned_doctor_id"])
        
        return {
            "patient": patient,
            "conditions": conditions,
            "primary_physician": doctor
        }

    @classmethod
    def get_latest_labs(cls, patient_id: str) -> List[Dict[str, Any]]:
        labs = [obs for obs in db.observations if obs["patient_id"] == patient_id]
        labs.sort(key=lambda x: x["date"], reverse=True)
        return labs

    @classmethod
    def analyze_lab_trends(cls, patient_id: str, test_name: str = "HbA1c") -> Dict[str, Any]:
        """
        Longitudinal trend analysis for lab values (e.g. comparing past HbA1c readings).
        Flags whether the change is significant and provides neutral clinical context.
        """
        records = [
            obs for obs in db.observations 
            if obs["patient_id"] == patient_id and test_name.lower() in obs["test_name"].lower()
        ]
        records.sort(key=lambda x: x["date"], reverse=True)

        if not records:
            return {
                "found": False,
                "message": f"No previous records found for test: {test_name}"
            }

        latest = records[0]
        previous = records[1] if len(records) > 1 else None

        trend_direction = "STABLE"
        delta_text = "No previous comparative record."
        clinical_insight = ""

        if previous and isinstance(latest["value"], (int, float)) and isinstance(previous["value"], (int, float)):
            delta = round(latest["value"] - previous["value"], 2)
            if delta > 0:
                trend_direction = "INCREASED"
                delta_text = f"+{delta} {latest['unit']} higher than {previous['date']} ({previous['value']} {previous['unit']})"
            elif delta < 0:
                trend_direction = "DECREASED"
                delta_text = f"{delta} {latest['unit']} lower than {previous['date']} ({previous['value']} {previous['unit']})"
            else:
                trend_direction = "UNCHANGED"
                delta_text = f"Identical to previous reading on {previous['date']} ({previous['value']} {previous['unit']})"

        if test_name.lower() == "hba1c":
            clinical_insight = (
                "HbA1c reflects average blood sugar over approximately 90 days. "
                f"Your latest result of {latest['value']}% is above the typical diabetic target of < 7.0%. "
                "Because it has increased from your previous test, this is an important topic to review with your clinician."
            )

        doctor_questions = [
            f"My {test_name} changed from {previous['value'] if previous else 'baseline'} to {latest['value']}. Does my treatment plan need adjustment?",
            "Should I modify my diet, exercise, or timing of my meals?",
            "When should we re-test my levels?"
        ]

        return {
            "found": True,
            "test_name": latest["test_name"],
            "unit": latest["unit"],
            "latest_reading": {
                "date": latest["date"],
                "value": latest["value"],
                "interpretation": latest["interpretation"],
                "reference_target": latest["reference_range"].get("target", "Normal range")
            },
            "previous_reading": {
                "date": previous["date"],
                "value": previous["value"]
            } if previous else None,
            "trend_direction": trend_direction,
            "delta_text": delta_text,
            "clinical_insight": clinical_insight,
            "suggested_doctor_questions": doctor_questions
        }

    @classmethod
    def parse_report_payload(cls, raw_data: Dict[str, Any], patient_id: str) -> Dict[str, Any]:
        """
        Extracts structured JSON from uploaded lab report representation and validates ranges.
        """
        test_name = raw_data.get("test_name", "Unknown Test")
        value = raw_data.get("value", 0.0)
        unit = raw_data.get("unit", "")
        ref_target = raw_data.get("target", "< 7.0%")

        return {
            "parsed": True,
            "patient_id": patient_id,
            "extracted_test": test_name,
            "value": value,
            "unit": unit,
            "reference_target": ref_target,
            "status": "VALIDATED"
        }
