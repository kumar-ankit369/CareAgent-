import re
from typing import Dict, Any, List, Optional
from backend.app.agents.safety_guard import SafetyGuard
from backend.app.agents.ehr_agent import EHRAgent
from backend.app.agents.appointment_agent import AppointmentAgent
from backend.app.agents.medication_agent import MedicationAgent
from backend.app.core.config import settings
from backend.app.db.database import db

class AgentOrchestrator:
    """
    Central AI Agent Orchestrator.
    Routes patient queries to specialized agents, enforces safety invariants,
    and returns rich markdown responses with structured interactive action payloads.
    """

    @classmethod
    async def process_patient_message(cls, patient_id: str, message: str) -> Dict[str, Any]:
        user_text = message.strip()
        text_lower = user_text.lower()

        # Step 1: Safety & Clinical Guardrails (Short-circuit on emergency or non-prescribing violations)
        guard_result = SafetyGuard.evaluate_query(user_text)
        if guard_result and guard_result.get("short_circuit"):
            db.log_audit(
                actor_id=patient_id,
                actor_role="patient",
                action="SAFETY_GUARDRAIL_TRIGGERED",
                resource=f"SafetyGuard/{guard_result['guardrail_triggered']}",
                details=f"Query triggered {guard_result['severity']} guardrail: {user_text[:50]}..."
            )
            return {
                "agent": "SafetyGuard",
                "response": guard_result["response"],
                "action_card": guard_result.get("action_card"),
                "guardrail": guard_result["guardrail_triggered"]
            }

        # Step 2: Complex Cross-Agent Intent: Visit Preparation & High Sugar + Appointment Scenario
        if ("sugar" in text_lower or "hba1c" in text_lower or "report" in text_lower) and ("appointment" in text_lower or "tomorrow" in text_lower or "what should i do" in text_lower):
            trend = EHRAgent.analyze_lab_trends(patient_id, "HbA1c")
            apts = AppointmentAgent.get_upcoming_appointments(patient_id)
            meds = MedicationAgent.get_prescribed_medications(patient_id)
            
            apt_context = f"You have an upcoming visit on **{apts[0]['datetime']}** with **{apts[0]['doctor_name']}** ({apts[0]['department']})." if apts else "I recommend scheduling a follow-up consultation with your doctor."
            
            response = (
                f"### Clinical Summary & Action Plan\n\n"
                f"I reviewed your records regarding your elevated blood sugar readings:\n\n"
                f"**1. Lab Analysis:**\n"
                f"• Latest **HbA1c**: **{trend['latest_reading']['value']}%** (Tested on {trend['latest_reading']['date']})\n"
                f"• Previous: **{trend['previous_reading']['value']}%** ({trend['delta_text']})\n"
                f"• Clinical Context: {trend['clinical_insight']}\n\n"
                f"**2. Your Upcoming Appointment:**\n"
                f"{apt_context}\n\n"
                f"**3. Current Approved Medications:**\n"
                + "\n".join([f"• {m['name']} ({m['dose']}) - {m['frequency']}" for m in meds]) +
                f"\n\n**4. Recommended Questions for Your Doctor:**\n"
                + "\n".join([f"• {q}" for q in trend.get("suggested_doctor_questions", [])]) +
                f"\n\n*Note: Please do not modify your Metformin dose without your doctor's explicit direction.*"
            )

            db.log_audit(patient_id, "patient", "AGENT_RECORDS_ANALYSIS", "CrossAgent/VisitSummary", "Synthesized HbA1c + Appointment briefing")
            return {
                "agent": "ClinicalOrchestrator",
                "response": response,
                "action_card": {
                    "type": "LAB_TREND_CARD",
                    "title": "HbA1c Longitudinal Comparison",
                    "latest": trend['latest_reading']['value'],
                    "previous": trend['previous_reading']['value'] if trend.get('previous_reading') else None,
                    "unit": "%",
                    "trend": trend['trend_direction']
                }
            }

        # Step 3: Lab Reports / Test Results Intent
        if any(w in text_lower for w in ["lab", "blood report", "hba1c", "cholesterol", "test result", "sugar", "glucose"]):
            test_type = "Cholesterol" if "cholesterol" in text_lower else "HbA1c"
            trend = EHRAgent.analyze_lab_trends(patient_id, test_type)
            all_labs = EHRAgent.get_latest_labs(patient_id)
            
            if "compare" in text_lower or "trend" in text_lower or "hba1c" in text_lower:
                response = (
                    f"### Latest {trend['test_name']} Report\n\n"
                    f"• **Most Recent Value:** **{trend['latest_reading']['value']} {trend['unit']}** ({trend['latest_reading']['date']})\n"
                    f"• **Status:** {trend['latest_reading']['interpretation']}\n"
                    f"• **Comparison:** {trend['delta_text']}\n\n"
                    f"{trend['clinical_insight']}\n\n"
                    f"**Suggested Doctor Discussion Points:**\n"
                    + "\n".join([f"• {q}" for q in trend.get("suggested_doctor_questions", [])])
                )
            else:
                lines = [f"• **{lab['test_name']}**: {lab['value']} {lab['unit']} ({lab['date']}) — *{lab['interpretation']}*" for lab in all_labs[:4]]
                response = (
                    f"### Your Recent Hospital Laboratory Results\n\n"
                    + "\n".join(lines) +
                    f"\n\nWould you like me to explain any of these tests or compare them with your historical results?"
                )

            db.log_audit(patient_id, "patient", "AGENT_EHR_QUERY", "Observation", f"Retrieved lab observations for {test_type}")
            return {
                "agent": "EHRAgent",
                "response": response,
                "action_card": {
                    "type": "LAB_CARD",
                    "title": f"Recent {test_type} Analysis",
                    "value": trend['latest_reading']['value'] if trend.get('found') else "View in Records",
                    "unit": trend.get('unit', "")
                }
            }

        # Step 4: Appointment Intent
        if any(w in text_lower for w in ["appointment", "book", "schedule", "slot", "doctor", "cardiology", "dermatology"]):
            if "book" in text_lower or "slot" in text_lower or "schedule" in text_lower:
                dept = "Dermatology" if "dermatology" in text_lower else ("Cardiology" if "cardiology" in text_lower else None)
                slots = AppointmentAgent.get_available_slots(department=dept)
                
                if not slots:
                    return {
                        "agent": "AppointmentAgent",
                        "response": f"I didn't find open slots matching {dept or 'your request'} right now. Would you like me to check other departments?",
                    }

                response = (
                    f"### Available Appointment Openings\n\n"
                    f"I found the following openings matching your request:\n\n"
                )
                for idx, s in enumerate(slots[:3], 1):
                    response += f"{idx}. **{s['doctor_name']}** ({s['department']}) — {s['datetime']}\n"
                
                response += (
                    f"\nTo select a slot, click one of the options below. "
                    f"**Remember: Booking will require your confirmation before it is locked in.**"
                )

                return {
                    "agent": "AppointmentAgent",
                    "response": response,
                    "action_card": {
                        "type": "SLOT_SELECTION_CARD",
                        "title": "Select an Available Slot",
                        "slots": slots[:3]
                    }
                }
            else:
                # Show upcoming appointments
                apts = AppointmentAgent.get_upcoming_appointments(patient_id)
                if apts:
                    apt = apts[0]
                    response = (
                        f"### Your Next Scheduled Appointment\n\n"
                        f"• **Physician:** {apt['doctor_name']}\n"
                        f"• **Department:** {apt['department']}\n"
                        f"• **Date & Time:** {apt['datetime']}\n"
                        f"• **Location:** {apt['location']}\n"
                        f"• **Purpose:** {apt['reason']}\n\n"
                        f"Would you like to reschedule, prepare clinical questions, or book an additional appointment?"
                    )
                else:
                    response = "You currently have no upcoming appointments scheduled. Would you like to book one?"
                
                db.log_audit(patient_id, "patient", "AGENT_APPOINTMENT_QUERY", "Appointment", "Queried upcoming appointments")
                return {
                    "agent": "AppointmentAgent",
                    "response": response,
                    "action_card": {
                        "type": "APPOINTMENT_CARD",
                        "appointment": apts[0] if apts else None
                    }
                }

        # Step 5: Medication & Adherence Intent
        if any(w in text_lower for w in ["medicine", "medication", "pill", "prescription", "adherence", "remind", "dose"]):
            meds = MedicationAgent.get_prescribed_medications(patient_id)
            sched = MedicationAgent.get_medication_schedule(patient_id)
            adh = MedicationAgent.calculate_adherence_summary(patient_id)

            med_lines = [f"• **{m['name']}** ({m['dose']}): {m['frequency']}. *{m['instructions']}*" for m in meds]
            sched_lines = [f"• **{s['time']}** — {s['medication_name']} ({s['dose']})" for s in sched]

            response = (
                f"### Your Clinician-Approved Medications\n\n"
                + "\n".join(med_lines) +
                f"\n\n**Daily Intake Timetable:**\n"
                + "\n".join(sched_lines) +
                f"\n\n**Adherence Performance:**\n"
                f"{adh['summary']}\n\n"
                f"You can log your daily medication directly using the buttons below."
            )

            db.log_audit(patient_id, "patient", "AGENT_MEDICATION_QUERY", "MedicationRequest", "Retrieved approved medications and adherence")
            return {
                "agent": "MedicationAgent",
                "response": response,
                "action_card": {
                    "type": "MEDICATION_SCHEDULE_CARD",
                    "medications": meds,
                    "adherence_rate": adh["adherence_rate_pct"]
                }
            }

        # Step 6: Summary / Clinical Visit Preparation Intent
        if any(w in text_lower for w in ["summary", "history", "prepare", "overview"]):
            profile = EHRAgent.get_patient_profile(patient_id)
            apts = AppointmentAgent.get_upcoming_appointments(patient_id)
            meds = MedicationAgent.get_prescribed_medications(patient_id)
            labs = EHRAgent.get_latest_labs(patient_id)

            response = (
                f"### Patient Health Summary: {profile['patient']['name']}\n\n"
                f"• **Active Conditions:** " + ", ".join([c["name"] for c in profile["conditions"]]) + "\n"
                f"• **Allergies:** " + ", ".join(profile["patient"]["allergies"]) + "\n"
                f"• **Current Prescriptions:** " + ", ".join([f"{m['name']} {m['dose']}" for m in meds]) + "\n"
                f"• **Next Scheduled Visit:** " + (f"{apts[0]['doctor_name']} ({apts[0]['datetime']})" if apts else "None scheduled") + "\n"
                f"• **Recent Lab Focus:** HbA1c {labs[0]['value']}% on {labs[0]['date']} ({labs[0]['interpretation']})\n\n"
                f"I can help you prepare questions for your doctor or review specific test details."
            )
            return {
                "agent": "ClinicalOrchestrator",
                "response": response,
                "action_card": {"type": "SUMMARY_CARD", "patient_id": patient_id}
            }

        # Step 7: Live Gemini LLM Generation (if GEMINI_API_KEY is configured in backend/.env)
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            llm_reply = cls._generate_llm_response(patient_id, user_text)
            if llm_reply:
                db.log_audit(patient_id, "patient", "AGENT_LLM_GENERATION", "Gemini", f"Generated grounded response for query: {user_text[:60]}")
                return {
                    "agent": "CareAgent-AI (Gemini)",
                    "response": llm_reply,
                    "action_card": None
                }

        # Step 8: General Hospital Assistant fallback
        return {
            "agent": "HospitalAssistant",
            "response": (
                f"Hello! I am your **CareAgent Hospital Assistant**.\n\n"
                f"Here are a few things I can assist you with:\n"
                f"• 📊 **Medical Data:** \"Show my latest blood report\" or \"What does my HbA1c result mean?\"\n"
                f"• 📅 **Appointments:** \"When is my next appointment?\" or \"Book an appointment with cardiology\"\n"
                f"• 💊 **Medications:** \"What medicines am I currently taking?\" or \"Log my morning dose\"\n"
                f"• 📋 **Visit Prep:** \"Summarize my medical history for my next appointment\"\n\n"
                f"How can I assist you today?"
            ),
            "action_card": None
        }

    @classmethod
    def _generate_llm_response(cls, patient_id: str, user_text: str) -> Optional[str]:
        """
        Invokes Google Gemini with clinical EHR context grounding and strict safety guardrails.
        Falls back to None if the package is not installed or API call fails.
        """
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(settings.GEMINI_MODEL)

            profile = EHRAgent.get_patient_profile(patient_id)
            meds = MedicationAgent.get_prescribed_medications(patient_id)
            labs = EHRAgent.get_latest_labs(patient_id)
            conds = [c["name"] for c in profile.get("conditions", [])]

            lab_summaries = [
                f"{l.get('test_name')}: {l.get('value')}{l.get('unit')} ({l.get('interpretation')})"
                for l in labs[:3]
            ]
            labs_str = ', '.join(lab_summaries) if lab_summaries else 'None'

            system_context = (
                "You are CareAgent, an enterprise clinical AI assistant for a hospital.\n"
                "PATIENT CONTEXT (FHIR Records):\n"
                f"- Name: {profile['patient']['name']}, Age: {profile['patient']['birth_date']}\n"
                f"- Known Conditions: {', '.join(conds) if conds else 'None'}\n"
                f"- Prescribed Medications: {', '.join([m['name'] + ' ' + m['dose'] for m in meds])}\n"
                f"- Recent Labs: {labs_str}\n\n"
                "CRITICAL CLINICAL SAFETY RULES:\n"
                "1. NEVER prescribe new medications, change dosages, or suggest discontinued drugs.\n"
                "2. If the user presents emergency symptoms, immediately advise calling 911 / emergency services.\n"
                "3. Provide empathetic, clear, evidence-based health explanations.\n"
                "4. Always suggest discussing findings with their licensed physician.\n"
                "5. Format responses in clean GitHub markdown with bullet points and bold highlights.\n"
            )


            prompt = f"{system_context}\n\nPATIENT QUERY: {user_text}"
            res = model.generate_content(prompt)
            if res and res.text:
                return res.text.strip()
        except Exception as e:
            # Silently fallback to built-in rules if Gemini is unreachable or error occurs
            return None
        return None

