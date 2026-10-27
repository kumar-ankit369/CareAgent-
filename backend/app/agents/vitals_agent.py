"""
agents/vitals_agent.py — Vitals Monitoring Agent
Analyses patient-reported vital signs, detects anomalies, generates clinical guidance,
and surfaces trend summaries for both the patient and physician portals.
"""
from typing import List, Optional, Dict, Any
from backend.app.db.database import db

REFERENCE_RANGES = {
    "blood_pressure": {
        "optimal": "< 120/80 mmHg",
        "normal": "120-129/< 80 mmHg",
        "elevated": "130-139/80-89 mmHg",
        "high_stage1": "130-139/80-89 mmHg",
        "high_stage2": ">= 140/90 mmHg",
        "hypertensive_crisis": ">= 180/120 mmHg"
    },
    "heart_rate": {"normal": "60-100 bpm", "bradycardia": "< 60 bpm", "tachycardia": "> 100 bpm"},
    "spo2": {"normal": ">= 95%", "low": "90-94%", "critical": "< 90%"},
    "temperature": {"normal": "36.1-37.2°C / 97-99°F", "fever": "> 38°C / 100.4°F"},
    "glucose": {"fasting_normal": "70-99 mg/dL", "pre_diabetic": "100-125 mg/dL", "diabetic": ">= 126 mg/dL"},
    "weight": {"note": "Reference is patient-specific baseline"}
}


class VitalsAgent:
    """
    Handles vital sign analysis, trend summaries, and intelligent clinical messaging.
    All methods are stateless class methods — the agent reads from/writes to the shared db.
    """

    @classmethod
    def get_latest_vitals(cls, patient_id: str) -> Dict[str, Any]:
        """Returns the most recent reading of each vital type for a patient."""
        patient_vitals = [v for v in db.vitals if v["patient_id"] == patient_id]
        latest: Dict[str, Any] = {}
        for v in reversed(patient_vitals):  # newest first
            if v["vital_type"] not in latest:
                latest[v["vital_type"]] = v
        return latest

    @classmethod
    def get_vital_trend(cls, patient_id: str, vital_type: str, limit: int = 10) -> Dict[str, Any]:
        """Returns the trend for a specific vital type with a clinical summary note."""
        readings = [
            v for v in db.vitals
            if v["patient_id"] == patient_id and v["vital_type"] == vital_type
        ][-limit:]

        if not readings:
            return {"vital_type": vital_type, "readings": [], "trend": "no_data", "clinical_note": "No readings recorded yet."}

        latest = readings[-1]
        alert_count = sum(1 for r in readings if r.get("alert_level") not in ("normal", None))

        if alert_count == 0:
            trend = "stable"
            note = f"All recent {vital_type.replace('_', ' ')} readings are within normal range."
        elif alert_count <= len(readings) // 3:
            trend = "mostly_stable"
            note = f"{alert_count} of your last {len(readings)} readings were elevated. Monitor closely."
        else:
            trend = "worsening"
            note = f"⚠️ {alert_count} of your last {len(readings)} readings were outside normal range. Please consult your doctor."

        ref = REFERENCE_RANGES.get(vital_type, {})

        return {
            "vital_type": vital_type,
            "readings": readings,
            "latest": latest,
            "trend": trend,
            "alert_count": alert_count,
            "reference_range": ref,
            "clinical_note": note
        }

    @classmethod
    def get_critical_alerts(cls, patient_id: str) -> List[Dict[str, Any]]:
        """Returns all critical vital readings for a patient, newest first."""
        return [
            v for v in reversed(db.vitals)
            if v["patient_id"] == patient_id
            and v.get("alert_level") in ("critical_high", "critical_low")
        ]

    @classmethod
    def generate_vitals_summary_for_doctor(cls, patient_id: str) -> str:
        """
        Generates a concise vitals narrative for the physician's pre-visit briefing.
        """
        latest = cls.get_latest_vitals(patient_id)
        if not latest:
            return "No patient-reported vitals on file."

        lines = ["**Patient-Reported Vitals Summary:**"]
        for vtype, reading in latest.items():
            alert = reading.get("alert_level", "normal")
            flag = " ⚠️" if alert not in ("normal", None) else " ✅"
            lines.append(
                f"• **{vtype.replace('_', ' ').title()}**: {reading['value']} {reading['unit']}{flag} "
                f"({reading['timestamp'][:10]})"
            )

        critical = cls.get_critical_alerts(patient_id)
        if critical:
            lines.append(f"\n⚠️ **{len(critical)} critical vital alert(s) on record** — immediate review recommended.")

        return "\n".join(lines)
