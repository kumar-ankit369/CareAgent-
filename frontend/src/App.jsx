import React, { useState, useEffect, useRef } from 'react';
import { 
  HeartPulse, User, Stethoscope, MessageSquare, FileText, Calendar, 
  Pill, AlertTriangle, CheckCircle, ShieldAlert, ArrowUpRight, ArrowDownRight,
  TrendingUp, Clock, PhoneCall, Sparkles, Send, RefreshCw, Plus, X, ChevronRight,
  Activity, Check, AlertCircle, Eye, LogOut, Bell, Thermometer, Droplets
} from 'lucide-react';
import { api } from './services/api';

export default function App() {
  // Global Role & Auth State
  const [role, setRole] = useState('patient'); // 'patient' or 'doctor'
  const [authToken, setAuthToken] = useState(null);
  const [activeTab, setActiveTab] = useState('chat'); // 'chat', 'reports', 'medications', 'appointments', 'vitals', 'notifications'

  // Patient Data State
  const [profile, setProfile] = useState(null);
  const [labs, setLabs] = useState([]);
  const [labTrend, setLabTrend] = useState(null);
  const [medications, setMedications] = useState([]);
  const [adherence, setAdherence] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [availableSlots, setAvailableSlots] = useState([]);

  // Vitals & Notifications State (v2.0)
  const [vitalsSummary, setVitalsSummary] = useState({});
  const [vitalsHistory, setVitalsHistory] = useState([]);
  const [selectedVitalType, setSelectedVitalType] = useState('blood_pressure');
  const [notifications, setNotifications] = useState([]);
  const [unreadNotifsCount, setUnreadNotifsCount] = useState(0);
  const [healthDashboard, setHealthDashboard] = useState(null);
  const [patientRisk, setPatientRisk] = useState(null);
  const [isLogVitalModalOpen, setIsLogVitalModalOpen] = useState(false);
  const [vitalForm, setVitalForm] = useState({
    vital_type: 'blood_pressure',
    value: '120/80',
    unit: 'mmHg',
    notes: 'Morning routine measurement'
  });

  // Chat State
  const [chatMessages, setChatMessages] = useState([
    {
      sender: 'agent',
      text: "Hello John! I'm your **CareAgent Hospital Assistant**.\n\nI can help you review your latest blood reports, track your vitals, check upcoming doctor visits, guide you on your clinician-approved medications, and prepare questions for your care team.\n\nHow can I help you today?",
      action_card: null,
      time: 'Just now'
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [isAgentTyping, setIsAgentTyping] = useState(false);
  const messagesEndRef = useRef(null);

  // Staged Booking Confirmation Modal / State
  const [stagedBooking, setStagedBooking] = useState(null);

  // Doctor Portal State
  const [doctorPatients, setDoctorPatients] = useState([]);
  const [selectedPatientId, setSelectedPatientId] = useState('pat-101');
  const [doctorBriefing, setDoctorBriefing] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [isPrescriptionModalOpen, setIsPrescriptionModalOpen] = useState(false);
  const [newMedForm, setNewMedForm] = useState({
    name: 'Empagliflozin',
    dose: '10 mg',
    frequency: 'Once daily in the morning',
    scheduled_times: ['08:00 AM'],
    purpose: 'Adjunctive glycemic control & cardiorenal protection',
    instructions: 'Take in morning with water.'
  });

  // Simulated Lab Upload Modal State
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [uploadForm, setUploadForm] = useState({
    test_name: 'HbA1c',
    value: 7.6,
    unit: '%',
    date: new Date().toISOString().split('T')[0]
  });

  // Switch role handler
  const handleSwitchRole = async (targetRole) => {
    try {
      const data = await api.auth.switchDemoRole(targetRole);
      api.setToken(data.access_token);
      setAuthToken(data.access_token);
      setRole(targetRole);
      if (targetRole === 'doctor') {
        fetchDoctorData(data.access_token);
      } else {
        fetchPatientData(data.access_token);
      }
    } catch (err) {
      console.error('Role switch failed:', err);
    }
  };

  // Initial Data Load
  useEffect(() => {
    handleSwitchRole('patient');
  }, []);

  const fetchPatientData = async (token = authToken) => {
    try {
      if (token) api.setToken(token);
      const [
        profRes, labsRes, trendRes, medsRes, adhRes, aptsRes, slotsRes,
        vitalsSumRes, vitalsHistRes, notifsRes, dashRes
      ] = await Promise.all([
        api.patients.getProfile().catch(() => null),
        api.reports.getLatest().catch(() => []),
        api.reports.getTrends('HbA1c').catch(() => null),
        api.medications.getPrescribed().catch(() => []),
        api.medications.getAdherence().catch(() => null),
        api.appointments.getMy().catch(() => []),
        api.appointments.getSlots().catch(() => []),
        api.vitals.getSummary().catch(() => ({ latest_readings: {} })),
        api.vitals.getHistory(selectedVitalType, 20).catch(() => ({ readings: [] })),
        api.notifications.getAll(false, 30).catch(() => ({ notifications: [], unread_count: 0 })),
        api.health.getDashboard().catch(() => null)
      ]);

      if (profRes) setProfile(profRes);
      if (labsRes) setLabs(labsRes);
      if (trendRes) setLabTrend(trendRes);
      if (medsRes) setMedications(medsRes);
      if (adhRes) setAdherence(adhRes);
      if (aptsRes) setAppointments(aptsRes);
      if (slotsRes) setAvailableSlots(slotsRes);
      if (vitalsSumRes?.latest_readings) setVitalsSummary(vitalsSumRes.latest_readings);
      if (vitalsHistRes?.readings) setVitalsHistory(vitalsHistRes.readings);
      if (notifsRes) {
        setNotifications(notifsRes.notifications || []);
        setUnreadNotifsCount(notifsRes.unread_count || 0);
      }
      if (dashRes) setHealthDashboard(dashRes);
    } catch (err) {
      console.error('Error fetching patient data:', err);
    }
  };

  const fetchDoctorData = async (token = authToken) => {
    try {
      if (token) api.setToken(token);
      const [patients, logs] = await Promise.all([
        api.doctor.getPatients().catch(() => []),
        api.doctor.getAuditLogs().catch(() => [])
      ]);

      setDoctorPatients(patients || []);
      setAuditLogs(logs || []);
      if (patients && patients.length > 0) {
        loadDoctorBriefing(patients[0].profile.id, token);
      }
    } catch (err) {
      console.error('Error fetching doctor data:', err);
    }
  };

  const loadDoctorBriefing = async (patientId, token = authToken) => {
    setSelectedPatientId(patientId);
    try {
      if (token) api.setToken(token);
      const [briefing, risk] = await Promise.all([
        api.doctor.getAIBriefing(patientId).catch(() => null),
        api.health.getRiskStratification(patientId).catch(() => null)
      ]);
      if (briefing) setDoctorBriefing(briefing);
      if (risk) setPatientRisk(risk);
    } catch (err) {
      console.error('Error loading briefing:', err);
    }
  };


  // Scroll chat to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, isAgentTyping]);

  // Send message to Agent Orchestrator
  const handleSendMessage = async (customText = null) => {
    const textToSend = customText || inputQuery;
    if (!textToSend.trim()) return;

    const userMsg = {
      sender: 'user',
      text: textToSend,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setChatMessages((prev) => [...prev, userMsg]);
    if (!customText) setInputQuery('');
    setIsAgentTyping(true);

    try {
      const data = await api.chat.sendMessage(textToSend, role === 'doctor' ? selectedPatientId : null);

      const agentMsg = {
        sender: 'agent',
        text: data.response,
        action_card: data.action_card,
        guardrail: data.guardrail,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setChatMessages((prev) => [...prev, agentMsg]);
      // Refresh patient metrics in case of background updates
      fetchPatientData();
    } catch (err) {
      setChatMessages((prev) => [
        ...prev,
        {
          sender: 'agent',
          text: "I experienced a temporary communication issue with the hospital server. Please try again.",
          time: 'Just now'
        }
      ]);
    } finally {
      setIsAgentTyping(false);
    }
  };

  // Action Handlers
  const handleStageSlot = async (slotId) => {
    try {
      const data = await api.appointments.stage(slotId, "Consultation");
      if (data.success) {
        setStagedBooking(data.appointment || data.staged_booking);
      }
    } catch (err) {
      alert('Could not hold appointment slot: ' + (err.message || ''));
    }
  };

  const handleConfirmAppointment = async (stageId) => {
    try {
      const data = await api.appointments.confirm(stageId);
      if (data.success) {
        setStagedBooking(null);
        fetchPatientData();
        setChatMessages((prev) => [
          ...prev,
          {
            sender: 'agent',
            text: data.message,
            time: 'Just now'
          }
        ]);
        setActiveTab('appointments');
      }
    } catch (err) {
      alert('Error confirming appointment: ' + (err.message || ''));
    }
  };

  const handleLogAdherence = async (medicationId, status) => {
    try {
      const data = await api.medications.logAdherence(medicationId, status);
      if (data.success) {
        fetchPatientData();
      }
    } catch (err) {
      console.error('Error logging adherence:', err);
    }
  };

  const handleUploadLab = async (e) => {
    e.preventDefault();
    try {
      const data = await api.reports.upload({
        test_name: uploadForm.test_name,
        value: parseFloat(uploadForm.value),
        unit: uploadForm.unit,
        date: uploadForm.date
      });
      if (data.success) {
        setIsUploadModalOpen(false);
        fetchPatientData();
        setChatMessages((prev) => [
          ...prev,
          {
            sender: 'agent',
            text: `📊 **Lab Document Ingested:** ${data.message}\n\n${data.trend_analysis?.clinical_insight || ''}`,
            time: 'Just now'
          }
        ]);
        setActiveTab('reports');
      }
    } catch (err) {
      alert('Lab upload failed: ' + (err.message || ''));
    }
  };

  const handleAuthorizeNewPrescription = async (e) => {
    e.preventDefault();
    try {
      const data = await api.doctor.authorizePrescription({
        patient_id: selectedPatientId,
        name: newMedForm.name,
        dose: newMedForm.dose,
        frequency: newMedForm.frequency,
        scheduled_times: newMedForm.scheduled_times,
        instructions: newMedForm.instructions,
        purpose: newMedForm.purpose
      });
      if (data.success) {
        setIsPrescriptionModalOpen(false);
        fetchDoctorData();
        alert(data.message);
      }
    } catch (err) {
      alert('Prescription authorization failed: ' + (err.message || ''));
    }
  };

  // Vitals & Notifications Handlers (v2.0)
  const handleLogVital = async (e) => {
    e.preventDefault();
    try {
      const data = await api.vitals.log(vitalForm.vital_type, vitalForm.value, vitalForm.unit, vitalForm.notes);
      if (data.success) {
        setIsLogVitalModalOpen(false);
        fetchPatientData();
        if (data.warning) {
          alert(data.warning);
        }
      }
    } catch (err) {
      alert('Failed to log vital sign: ' + (err.message || ''));
    }
  };

  const handleMarkNotificationRead = async (id) => {
    try {
      await api.notifications.markAsRead(id);
      setNotifications((prev) => prev.map((n) => n.id === id ? { ...n, read: true } : n));
      setUnreadNotifsCount((prev) => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Error marking notification read:', err);
    }
  };

  const handleMarkAllNotificationsRead = async () => {
    try {
      await api.notifications.markAllRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
      setUnreadNotifsCount(0);
    } catch (err) {
      console.error('Error marking all notifications read:', err);
    }
  };


  return (
    <div className="min-h-screen flex flex-col bg-slate-100">
      {/* 1. Header with Hospital Branding & Instant Role Switcher */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-teal-600 flex items-center justify-center text-white shadow-md shadow-teal-500/20">
              <HeartPulse className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg text-slate-900 tracking-tight">CareAgent</span>
                <span className="bg-teal-100 text-teal-800 text-xs font-semibold px-2 py-0.5 rounded-full">
                  Hospital AI v1.0
                </span>
                <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2 py-0.5 rounded-full">
                  HL7 FHIR R4
                </span>
              </div>
              <p className="text-xs text-slate-500">St. Jude Medical Center Platform</p>
            </div>
          </div>

          {/* Quick Dual-Portal Role Switcher */}
          <div className="flex items-center space-x-3 bg-slate-100 p-1 rounded-xl border border-slate-200">
            <button
              onClick={() => handleSwitchRole('patient')}
              className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                role === 'patient'
                  ? 'bg-white text-teal-700 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <User className="w-3.5 h-3.5 text-teal-600" />
              <span>Patient: John Doe</span>
            </button>
            <button
              onClick={() => handleSwitchRole('doctor')}
              className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                role === 'doctor'
                  ? 'bg-white text-blue-700 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Stethoscope className="w-3.5 h-3.5 text-blue-600" />
              <span>Doctor: Dr. Robert Chen</span>
            </button>
          </div>
        </div>
      </header>

      {/* 2. Main Content Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        {role === 'patient' ? (
          /* ========================================================================= */
          /* PATIENT PORTAL INTERFACE                                                  */
          /* ========================================================================= */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Nav & Quick Patient Metrics (4 cols) */}
            <div className="lg:col-span-4 space-y-6">
              {/* Patient Profile Card */}
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 rounded-full bg-teal-50 border-2 border-teal-200 flex items-center justify-center text-teal-700 font-bold text-lg">
                      JD
                    </div>
                    <div>
                      <h2 className="font-bold text-slate-900">{profile?.patient?.name || 'John Doe'}</h2>
                      <p className="text-xs text-slate-500">ID: {profile?.patient?.id || 'pat-101'} • Male, 48 yrs</p>
                    </div>
                  </div>
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                    Active EHR
                  </span>
                </div>

                <div className="mt-4 pt-4 border-t border-slate-100 grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <span className="text-slate-400 block">Attending Doctor</span>
                    <span className="font-semibold text-slate-800">{profile?.primary_physician?.name || 'Dr. Robert Chen'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Allergies</span>
                    <span className="font-semibold text-rose-600">Penicillin</span>
                  </div>
                  <div className="col-span-2">
                    <span className="text-slate-400 block">Diagnosed Conditions</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {profile?.conditions?.map((c) => (
                        <span key={c.id} className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-[11px] font-medium">
                          {c.name}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                {healthDashboard && (
                  <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between bg-teal-50/70 p-3 rounded-xl border border-teal-100">
                    <div>
                      <span className="text-[11px] font-bold text-teal-900 block">Overall Health Score</span>
                      <span className="text-xs text-teal-700">Status: <strong>{healthDashboard.health_score?.status || 'Good'}</strong></span>
                    </div>
                    <div className="text-right">
                      <span className="text-xl font-extrabold text-teal-800">{healthDashboard.health_score?.score || 88}</span>
                      <span className="text-xs text-teal-600 font-bold">/100</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Navigation Tabs */}
              <div className="bg-white rounded-2xl p-2 border border-slate-200 shadow-sm flex flex-col space-y-1">
                {[
                  { id: 'chat', label: 'AI Health Assistant', icon: MessageSquare, badge: 'Live Agent' },
                  { id: 'reports', label: 'My Lab Reports & Trends', icon: FileText, badge: `${labs.length} Tests` },
                  { id: 'medications', label: 'Medications & Daily Intake', icon: Pill, badge: `${adherence?.adherence_rate_pct || 100}% Adherence` },
                  { id: 'appointments', label: 'Hospital Appointments', icon: Calendar, badge: `${appointments.length} Scheduled` },
                  { id: 'vitals', label: 'Vitals & Daily Logs', icon: Activity, badge: `${vitalsHistory.length || 0} Logged` },
                  { id: 'notifications', label: 'Alerts & Reminders', icon: Bell, badge: `${unreadNotifsCount} New` },
                ].map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`flex items-center justify-between p-3 rounded-xl text-sm font-medium transition-all ${
                        activeTab === tab.id
                          ? 'bg-teal-50 text-teal-800 font-semibold'
                          : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <Icon className={`w-4 h-4 ${activeTab === tab.id ? 'text-teal-600' : 'text-slate-400'}`} />
                        <span>{tab.label}</span>
                      </div>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        activeTab === tab.id ? 'bg-teal-200/60 text-teal-900' : 'bg-slate-100 text-slate-500'
                      }`}>
                        {tab.badge}
                      </span>
                    </button>
                  );
                })}
              </div>


              {/* Quick Clinical Guidance & Safety Card */}
              <div className="bg-amber-50/70 border border-amber-200 rounded-2xl p-4 text-xs text-amber-900 space-y-2">
                <div className="flex items-center space-x-2 font-bold text-amber-950">
                  <ShieldAlert className="w-4 h-4 text-amber-600" />
                  <span>Clinical Safety Standard</span>
                </div>
                <p>
                  CareAgent provides information, flags trends, and prepares you for doctor visits. 
                  <strong> It cannot independently modify medication doses or diagnose conditions.</strong>
                </p>
                <p className="text-amber-800 font-medium">
                  Emergency: In case of acute chest pain, breathlessness, or stroke symptoms, dial <strong>911</strong> immediately.
                </p>
              </div>
            </div>

            {/* Right Main Panel (8 cols) */}
            <div className="lg:col-span-8">
              {/* TAB 1: AI HEALTH ASSISTANT CHAT */}
              {activeTab === 'chat' && (
                <div className="bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col h-[700px] overflow-hidden">
                  {/* Chat Top Banner */}
                  <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></div>
                      <span className="font-semibold text-sm text-slate-800">CareAgent Multi-Agent Orchestrator</span>
                    </div>
                    <span className="text-xs text-slate-400">Permission-Aware EHR Querying</span>
                  </div>

                  {/* Chat Messages Container */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {chatMessages.map((msg, i) => (
                      <div
                        key={i}
                        className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
                      >
                        <div
                          className={`max-w-[85%] rounded-2xl p-4 text-sm leading-relaxed shadow-sm ${
                            msg.sender === 'user'
                              ? 'bg-teal-600 text-white rounded-tr-none'
                              : msg.guardrail === 'EMERGENCY_TRIAGE'
                              ? 'bg-rose-50 border-2 border-rose-300 text-rose-950 rounded-tl-none'
                              : msg.guardrail === 'MEDICATION_SAFETY_INVARIANT'
                              ? 'bg-amber-50 border border-amber-300 text-amber-950 rounded-tl-none'
                              : 'bg-slate-50 border border-slate-200 text-slate-800 rounded-tl-none'
                          }`}
                        >
                          <div className="whitespace-pre-line prose prose-sm max-w-none">
                            {msg.text}
                          </div>

                          {/* ACTION CARDS (Rendered dynamically based on agent tool outputs) */}
                          {msg.action_card && (
                            <div className="mt-3 pt-3 border-t border-slate-200/60">
                              {/* Emergency Call Card */}
                              {msg.action_card.type === 'EMERGENCY_CALL_CARD' && (
                                <div className="bg-rose-600 text-white rounded-xl p-3 flex items-center justify-between">
                                  <div>
                                    <span className="font-bold block text-sm">{msg.action_card.title}</span>
                                    <span className="text-xs opacity-90">{msg.action_card.hotline_label}</span>
                                  </div>
                                  <a
                                    href={`tel:${msg.action_card.phone}`}
                                    className="bg-white text-rose-700 px-3 py-1.5 rounded-lg font-bold text-xs flex items-center space-x-1 shadow"
                                  >
                                    <PhoneCall className="w-3.5 h-3.5" />
                                    <span>Call 911 Now</span>
                                  </a>
                                </div>
                              )}

                              {/* Lab Trend Action Card */}
                              {msg.action_card.type === 'LAB_TREND_CARD' && (
                                <div className="bg-white rounded-xl p-3 border border-slate-200 text-slate-800 space-y-2">
                                  <div className="flex items-center justify-between text-xs font-bold">
                                    <span className="text-slate-600">{msg.action_card.title}</span>
                                    <span className="text-rose-600 flex items-center">
                                      <TrendingUp className="w-3.5 h-3.5 mr-1" /> Elevated (+0.6%)
                                    </span>
                                  </div>
                                  <div className="grid grid-cols-2 gap-2 text-center">
                                    <div className="bg-slate-50 p-2 rounded-lg">
                                      <span className="text-[11px] text-slate-400 block">May 15</span>
                                      <span className="text-base font-bold text-slate-700">6.8%</span>
                                    </div>
                                    <div className="bg-rose-50 p-2 rounded-lg border border-rose-200">
                                      <span className="text-[11px] text-rose-600 block font-medium">Aug 28 (Latest)</span>
                                      <span className="text-base font-bold text-rose-700">7.4%</span>
                                    </div>
                                  </div>
                                </div>
                              )}

                              {/* Slot Selection Card */}
                              {msg.action_card.type === 'SLOT_SELECTION_CARD' && (
                                <div className="space-y-2">
                                  <span className="text-xs font-bold text-slate-700 block">Available Openings:</span>
                                  <div className="space-y-1.5">
                                    {msg.action_card.slots.map((slot) => (
                                      <div
                                        key={slot.id}
                                        className="bg-white rounded-xl p-2.5 border border-slate-200 flex items-center justify-between hover:border-teal-400 transition-all"
                                      >
                                        <div className="text-xs">
                                          <span className="font-semibold text-slate-900 block">{slot.doctor_name}</span>
                                          <span className="text-slate-500">{slot.department} • {slot.datetime}</span>
                                        </div>
                                        <button
                                          onClick={() => handleStageSlot(slot.id)}
                                          className="bg-teal-600 text-white text-xs px-3 py-1 rounded-lg font-medium hover:bg-teal-700 shadow-sm"
                                        >
                                          Select Slot
                                        </button>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}

                              {/* Medication Schedule Card */}
                              {msg.action_card.type === 'MEDICATION_SCHEDULE_CARD' && (
                                <div className="bg-teal-50/70 rounded-xl p-3 border border-teal-200 text-slate-800 space-y-2">
                                  <div className="flex items-center justify-between text-xs">
                                    <span className="font-bold text-teal-900">Current Regimen Adherence</span>
                                    <span className="font-bold text-emerald-700">{msg.action_card.adherence_rate}%</span>
                                  </div>
                                  <div className="w-full bg-slate-200 rounded-full h-2">
                                    <div
                                      className="bg-emerald-500 h-2 rounded-full transition-all"
                                      style={{ width: `${msg.action_card.adherence_rate}%` }}
                                    ></div>
                                  </div>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                        <span className="text-[10px] text-slate-400 mt-1 px-1">{msg.time}</span>
                      </div>
                    ))}

                    {/* Agent typing indicator */}
                    {isAgentTyping && (
                      <div className="flex items-center space-x-2 text-slate-400 text-xs p-2">
                        <Sparkles className="w-4 h-4 text-teal-600 animate-spin" />
                        <span>CareAgent is reasoning across records & protocols...</span>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </div>

                  {/* Suggested Prompts Pill Bar */}
                  <div className="px-4 py-2 bg-slate-50 border-t border-slate-100 flex items-center space-x-2 overflow-x-auto text-xs">
                    <span className="text-slate-400 whitespace-nowrap font-medium">Quick Prompts:</span>
                    <button
                      onClick={() => handleSendMessage("Show my latest blood report and compare with previous.")}
                      className="bg-white border border-slate-200 text-slate-700 px-2.5 py-1 rounded-full whitespace-nowrap hover:bg-teal-50 hover:border-teal-300 transition-all"
                    >
                      📊 "Show latest blood report"
                    </button>
                    <button
                      onClick={() => handleSendMessage("I have an appointment next week and my sugar report is high. What should I do?")}
                      className="bg-white border border-slate-200 text-slate-700 px-2.5 py-1 rounded-full whitespace-nowrap hover:bg-teal-50 hover:border-teal-300 transition-all"
                    >
                      🩺 "Sugar report high + appointment"
                    </button>
                    <button
                      onClick={() => handleSendMessage("Can I take double dose of Metformin because I missed morning?")}
                      className="bg-white border border-slate-200 text-slate-700 px-2.5 py-1 rounded-full whitespace-nowrap hover:bg-teal-50 hover:border-teal-300 transition-all"
                    >
                      ⚠️ "Can I double missed dose?"
                    </button>
                    <button
                      onClick={() => handleSendMessage("I feel acute crushing pressure in my chest and my left arm hurts.")}
                      className="bg-white border border-rose-200 text-rose-700 px-2.5 py-1 rounded-full whitespace-nowrap hover:bg-rose-50 transition-all"
                    >
                      🚨 "Acute chest pain (Emergency)"
                    </button>
                  </div>

                  {/* Chat Input Bar */}
                  <div className="p-3 border-t border-slate-200 bg-white">
                    <form
                      onSubmit={(e) => {
                        e.preventDefault();
                        handleSendMessage();
                      }}
                      className="flex items-center space-x-2"
                    >
                      <input
                        type="text"
                        value={inputQuery}
                        onChange={(e) => setInputQuery(e.target.value)}
                        placeholder="Ask about your lab reports, medications, appointments, or symptoms..."
                        className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:bg-white transition-all"
                      />
                      <button
                        type="submit"
                        disabled={!inputQuery.trim() || isAgentTyping}
                        className="bg-teal-600 text-white p-2.5 rounded-xl hover:bg-teal-700 transition-all disabled:opacity-50 shadow-md shadow-teal-600/20"
                      >
                        <Send className="w-4 h-4" />
                      </button>
                    </form>
                  </div>
                </div>
              )}

              {/* TAB 2: MY LAB REPORTS & OBSERVATIONS */}
              {activeTab === 'reports' && (
                <div className="space-y-6">
                  {/* Top Action Bar */}
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-bold text-slate-900">FHIR Diagnostic Reports & Observations</h3>
                      <p className="text-xs text-slate-500">Continuous lab tracking and reference-range evaluations</p>
                    </div>
                    <button
                      onClick={() => setIsUploadModalOpen(true)}
                      className="bg-teal-600 text-white text-xs font-semibold px-3 py-2 rounded-xl flex items-center space-x-2 hover:bg-teal-700 shadow-sm"
                    >
                      <Plus className="w-4 h-4" />
                      <span>Ingest New Lab Report</span>
                    </button>
                  </div>

                  {/* Longitudinal HbA1c Highlight Card */}
                  {labTrend && labTrend.found && (
                    <div className="bg-gradient-to-br from-teal-900 to-slate-900 text-white rounded-2xl p-6 shadow-md">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold uppercase tracking-wider text-teal-300">
                          Longitudinal Trend Spotlight
                        </span>
                        <span className="bg-rose-500/20 text-rose-300 text-xs px-2.5 py-1 rounded-full font-semibold border border-rose-500/30">
                          {labTrend.trend_direction} ({labTrend.delta_text})
                        </span>
                      </div>
                      <div className="mt-4 flex items-baseline space-x-3">
                        <span className="text-4xl font-extrabold tracking-tight">{labTrend.latest_reading.value}%</span>
                        <span className="text-sm text-teal-200">Latest HbA1c ({labTrend.latest_reading.date})</span>
                      </div>
                      <p className="mt-3 text-xs text-slate-300 leading-relaxed max-w-2xl">
                        {labTrend.clinical_insight}
                      </p>

                      <div className="mt-4 pt-4 border-t border-slate-700/60 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                        <div className="bg-white/5 rounded-xl p-3">
                          <span className="text-slate-400 block text-[11px]">Previous Baseline</span>
                          <span className="font-bold text-white text-sm">{labTrend.previous_reading?.value || '6.8'}%</span>
                          <span className="text-[10px] text-slate-400 block">{labTrend.previous_reading?.date || 'May 15'}</span>
                        </div>
                        <div className="bg-white/5 rounded-xl p-3">
                          <span className="text-slate-400 block text-[11px]">Diabetic Target Range</span>
                          <span className="font-bold text-teal-300 text-sm">{labTrend.latest_reading.reference_target}</span>
                          <span className="text-[10px] text-slate-400 block">General Guideline</span>
                        </div>
                        <div className="bg-white/5 rounded-xl p-3">
                          <span className="text-slate-400 block text-[11px]">Recommended Action</span>
                          <span className="font-bold text-amber-300 text-sm">Discuss with Dr. Chen</span>
                          <span className="text-[10px] text-slate-400 block">At upcoming appointment</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* All Recent Lab Cards Grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {labs.map((lab) => (
                      <div key={lab.id} className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="text-xs text-slate-400 block uppercase font-medium">{lab.category}</span>
                            <h4 className="font-bold text-slate-900">{lab.test_name}</h4>
                          </div>
                          <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold ${
                            lab.interpretation.includes('High') || lab.interpretation.includes('Elevated')
                              ? 'bg-amber-100 text-amber-800'
                              : 'bg-emerald-100 text-emerald-800'
                          }`}>
                            {lab.interpretation}
                          </span>
                        </div>

                        <div className="flex items-baseline space-x-2">
                          <span className="text-2xl font-bold text-slate-900">{lab.value}</span>
                          <span className="text-xs font-semibold text-slate-500">{lab.unit}</span>
                        </div>

                        <div className="text-xs text-slate-500 pt-2 border-t border-slate-100 flex items-center justify-between">
                          <span>Target: {lab.reference_range?.target || '< 200 mg/dL'}</span>
                          <span>Tested: {lab.date}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* TAB 3: MEDICATIONS & ADHERENCE */}
              {activeTab === 'medications' && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-bold text-slate-900">Clinician-Authorized Prescriptions</h3>
                    <p className="text-xs text-slate-500">Strictly approved by attending physicians; dosage changes require clinical review</p>
                  </div>

                  {/* Adherence Summary Bar */}
                  {adherence && (
                    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex items-center justify-between">
                      <div>
                        <span className="text-xs text-slate-400 font-medium block">Adherence Performance</span>
                        <h4 className="text-2xl font-black text-teal-700">{adherence.adherence_rate_pct}%</h4>
                        <p className="text-xs text-slate-500 mt-1">{adherence.summary}</p>
                      </div>
                      <div className="w-20 h-20 rounded-full border-4 border-teal-500 flex items-center justify-center font-bold text-sm text-teal-700 bg-teal-50">
                        {adherence.adherence_rate_pct}%
                      </div>
                    </div>
                  )}

                  {/* Medication Regimen Cards */}
                  <div className="space-y-4">
                    {medications.map((med) => (
                      <div key={med.id} className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center font-bold">
                              <Pill className="w-5 h-5" />
                            </div>
                            <div>
                              <h4 className="font-bold text-slate-900 text-base">{med.name}</h4>
                              <span className="text-xs text-slate-500">{med.dose} • {med.frequency}</span>
                            </div>
                          </div>
                          <span className="bg-teal-100 text-teal-800 text-xs px-2.5 py-1 rounded-full font-semibold">
                            Authorized: {med.prescriber_name}
                          </span>
                        </div>

                        <p className="text-xs text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100">
                          <strong>Instructions:</strong> {med.instructions}
                        </p>

                        <div className="pt-2 flex items-center justify-between text-xs">
                          <div className="flex items-center space-x-2 text-slate-500">
                            <Clock className="w-3.5 h-3.5" />
                            <span>Scheduled: {med.scheduled_times.join(', ')}</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => handleLogAdherence(med.id, 'taken')}
                              className="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded-lg font-semibold flex items-center space-x-1 shadow-sm transition-all"
                            >
                              <Check className="w-3.5 h-3.5" />
                              <span>Mark as Taken</span>
                            </button>
                            <button
                              onClick={() => handleLogAdherence(med.id, 'skipped')}
                              className="bg-slate-100 hover:bg-slate-200 text-slate-600 px-3 py-1.5 rounded-lg font-semibold transition-all"
                            >
                              <span>Skip</span>
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* TAB 4: APPOINTMENTS */}
              {activeTab === 'appointments' && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-bold text-slate-900">Hospital Appointments & Calendar</h3>
                    <p className="text-xs text-slate-500">Bookings require explicit patient confirmation before committing to the schedule</p>
                  </div>

                  {/* Scheduled Visits */}
                  <div className="space-y-3">
                    <h4 className="text-xs font-bold uppercase text-slate-400 tracking-wider">Upcoming Scheduled Visits</h4>
                    {appointments.map((apt) => (
                      <div key={apt.id} className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex items-center justify-between">
                        <div className="space-y-1">
                          <div className="flex items-center space-x-2">
                            <span className="font-bold text-slate-900">{apt.doctor_name}</span>
                            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full font-medium">
                              {apt.department}
                            </span>
                          </div>
                          <p className="text-xs text-slate-500">{apt.datetime} • {apt.location}</p>
                          <p className="text-xs text-slate-600 italic">Purpose: {apt.reason}</p>
                        </div>
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                          Confirmed
                        </span>
                      </div>
                    ))}
                  </div>

                  {/* Available Openings for Booking */}
                  <div className="space-y-3 pt-4">
                    <h4 className="text-xs font-bold uppercase text-slate-400 tracking-wider">Available Openings Across Departments</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {availableSlots.map((slot) => (
                        <div key={slot.id} className="bg-white rounded-2xl p-4 border border-slate-200 shadow-sm flex items-center justify-between">
                          <div className="text-xs">
                            <span className="font-bold text-slate-900 block">{slot.doctor_name}</span>
                            <span className="text-teal-700 font-medium">{slot.department}</span>
                            <span className="text-slate-500 block mt-1">{slot.datetime}</span>
                          </div>
                          <button
                            onClick={() => handleStageSlot(slot.id)}
                            className="bg-teal-600 text-white text-xs px-3 py-1.5 rounded-xl font-semibold hover:bg-teal-700 transition-all shadow-sm"
                          >
                            Book Slot
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}


              {/* TAB 5: VITALS MONITORING */}
              {activeTab === 'vitals' && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-bold text-slate-900">Vitals & Biometric Telemetry</h3>
                      <p className="text-xs text-slate-500">Track and monitor your self-measured vitals. Automated alert evaluation protects patient safety.</p>
                    </div>
                    <button
                      onClick={() => setIsLogVitalModalOpen(true)}
                      className="bg-teal-600 hover:bg-teal-700 text-white text-xs font-semibold px-3 py-2 rounded-xl flex items-center space-x-1.5 shadow-sm transition-all"
                    >
                      <Plus className="w-4 h-4" />
                      <span>Log Vital Reading</span>
                    </button>
                  </div>

                  {/* Summary Metric Cards */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {[
                      { type: 'blood_pressure', label: 'Blood Pressure', defaultUnit: 'mmHg', icon: Activity, sample: vitalsSummary?.blood_pressure?.value || '120/80' },
                      { type: 'heart_rate', label: 'Heart Rate', defaultUnit: 'bpm', icon: HeartPulse, sample: vitalsSummary?.heart_rate?.value || '72' },
                      { type: 'glucose', label: 'Blood Glucose', defaultUnit: 'mg/dL', icon: Droplets, sample: vitalsSummary?.glucose?.value || '118' },
                      { type: 'spo2', label: 'Oxygen Saturation', defaultUnit: '%', icon: Thermometer, sample: vitalsSummary?.spo2?.value || '98' }
                    ].map((card) => {
                      const Icon = card.icon;
                      const reading = vitalsSummary[card.type];
                      const isAlert = reading?.alert_level && reading.alert_level !== 'normal';
                      return (
                        <div
                          key={card.type}
                          onClick={async () => {
                            setSelectedVitalType(card.type);
                            const res = await api.vitals.getHistory(card.type, 20).catch(() => ({ readings: [] }));
                            if (res?.readings) setVitalsHistory(res.readings);
                          }}
                          className={`bg-white rounded-2xl p-4 border cursor-pointer transition-all ${
                            selectedVitalType === card.type ? 'border-teal-500 shadow-md ring-1 ring-teal-500' : 'border-slate-200 hover:border-slate-300'
                          }`}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-[11px] font-bold text-slate-500 uppercase">{card.label}</span>
                            <Icon className={`w-4 h-4 ${isAlert ? 'text-amber-500' : 'text-teal-600'}`} />
                          </div>
                          <div className="flex items-baseline space-x-1">
                            <span className="text-xl font-bold text-slate-900">{reading ? reading.value : card.sample}</span>
                            <span className="text-xs text-slate-400">{reading ? reading.unit : card.defaultUnit}</span>
                          </div>
                          <div className="mt-2 flex items-center justify-between">
                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                              isAlert ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'
                            }`}>
                              {reading?.alert_level ? reading.alert_level.replace('_', ' ').toUpperCase() : 'NORMAL'}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Vitals History Table */}
                  <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-bold uppercase text-slate-400 tracking-wider">
                        Recent History: {selectedVitalType.replace('_', ' ').toUpperCase()}
                      </h4>
                      <span className="text-xs text-slate-500">{vitalsHistory.length} readings recorded</span>
                    </div>

                    <div className="divide-y divide-slate-100">
                      {vitalsHistory.length === 0 ? (
                        <p className="text-xs text-slate-400 py-3 text-center">No readings logged yet for this vital sign.</p>
                      ) : (
                        vitalsHistory.map((item) => (
                          <div key={item.id} className="py-2.5 flex items-center justify-between text-xs">
                            <div>
                              <span className="font-bold text-slate-800 text-sm">{item.value} {item.unit}</span>
                              <span className="text-slate-400 block text-[11px]">{new Date(item.timestamp).toLocaleString()}</span>
                              {item.notes && <p className="text-slate-500 text-[11px] italic mt-0.5">{item.notes}</p>}
                            </div>
                            <span className={`px-2.5 py-1 rounded-full text-[11px] font-bold ${
                              item.alert_level === 'critical_high' || item.alert_level === 'critical_low'
                                ? 'bg-rose-100 text-rose-800'
                                : item.alert_level?.includes('elevated') || item.alert_level?.includes('high')
                                ? 'bg-amber-100 text-amber-800'
                                : 'bg-emerald-100 text-emerald-800'
                            }`}>
                              {item.alert_level ? item.alert_level.replace('_', ' ').toUpperCase() : 'NORMAL'}
                            </span>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 6: NOTIFICATIONS & REMINDERS */}
              {activeTab === 'notifications' && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-bold text-slate-900">Hospital Alerts & Reminders</h3>
                      <p className="text-xs text-slate-500">In-app notifications for medication intake, upcoming visits, and diagnostic results</p>
                    </div>
                    {unreadNotifsCount > 0 && (
                      <button
                        onClick={handleMarkAllNotificationsRead}
                        className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold px-3 py-1.5 rounded-xl transition-all"
                      >
                        Mark All as Read
                      </button>
                    )}
                  </div>

                  <div className="space-y-2.5">
                    {notifications.length === 0 ? (
                      <div className="bg-white rounded-2xl p-8 border border-slate-200 text-center text-slate-400 text-xs">
                        No notifications to display right now.
                      </div>
                    ) : (
                      notifications.map((notif) => (
                        <div
                          key={notif.id}
                          className={`bg-white rounded-2xl p-4 border transition-all flex items-start justify-between ${
                            notif.read ? 'border-slate-200 opacity-75' : 'border-teal-200 bg-teal-50/20 shadow-sm'
                          }`}
                        >
                          <div className="flex items-start space-x-3">
                            <div className={`p-2 rounded-xl mt-0.5 ${
                              notif.type === 'medication' ? 'bg-emerald-100 text-emerald-700' :
                              notif.type === 'vital_alert' ? 'bg-rose-100 text-rose-700' :
                              notif.type === 'lab_result' ? 'bg-purple-100 text-purple-700' :
                              'bg-blue-100 text-blue-700'
                            }`}>
                              <Bell className="w-4 h-4" />
                            </div>
                            <div>
                              <div className="flex items-center space-x-2">
                                <h4 className="font-bold text-xs text-slate-900">{notif.title}</h4>
                                {!notif.read && (
                                  <span className="w-2 h-2 rounded-full bg-teal-600"></span>
                                )}
                              </div>
                              <p className="text-xs text-slate-600 mt-1">{notif.message}</p>
                              <span className="text-[10px] text-slate-400 mt-1 block">
                                {new Date(notif.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                              </span>
                            </div>
                          </div>
                          {!notif.read && (
                            <button
                              onClick={() => handleMarkNotificationRead(notif.id)}
                              className="text-[11px] font-semibold text-teal-700 hover:text-teal-900 bg-teal-100/70 hover:bg-teal-100 px-2.5 py-1 rounded-lg transition-all"
                            >
                              Mark Read
                            </button>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (

          /* ========================================================================= */
          /* DOCTOR PORTAL INTERFACE                                                   */
          /* ========================================================================= */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Assigned Patients List (4 cols) */}
            <div className="lg:col-span-4 space-y-4">
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <div>
                  <h3 className="font-bold text-slate-900">Physician Roster</h3>
                  <p className="text-xs text-slate-500">Dr. Robert Chen • Cardiology Outpatient</p>
                </div>

                <div className="space-y-2">
                  {doctorPatients.map((p) => (
                    <div
                      key={p.profile.id}
                      onClick={() => loadDoctorBriefing(p.profile.id)}
                      className={`p-3 rounded-xl border cursor-pointer transition-all ${
                        selectedPatientId === p.profile.id
                          ? 'bg-blue-50 border-blue-300 shadow-sm'
                          : 'bg-white border-slate-200 hover:bg-slate-50'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-sm text-slate-900">{p.profile.name}</span>
                        <span className="text-xs font-semibold text-blue-700 bg-blue-100 px-2 py-0.5 rounded-full">
                          {p.adherence_rate}% Adherence
                        </span>
                      </div>
                      <div className="mt-1 text-xs text-slate-500 space-y-0.5">
                        <p>{p.conditions.join(', ')}</p>
                        <p className="text-slate-400">Next Visit: {p.next_appointment}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Real-Time Audit Log Card */}
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-xs uppercase text-slate-400 tracking-wider">HIPAA Audit Trail</h4>
                  <span className="text-[10px] bg-emerald-100 text-emerald-800 font-semibold px-2 py-0.5 rounded-full">
                    Immutable
                  </span>
                </div>
                <div className="space-y-2 max-h-48 overflow-y-auto text-[11px]">
                  {auditLogs.slice(-6).reverse().map((log) => (
                    <div key={log.id} className="p-2 rounded-lg bg-slate-50 border border-slate-100">
                      <div className="flex justify-between font-semibold text-slate-700">
                        <span>{log.action}</span>
                        <span className="text-slate-400 text-[10px]">{log.actor_role}</span>
                      </div>
                      <p className="text-slate-500 text-[10px] truncate">{log.details}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* AI Clinical Briefing & Action Center (8 cols) */}
            <div className="lg:col-span-8 space-y-6">
              {/* Top Action Bar for Clinician */}
              <div className="flex items-center justify-between bg-white rounded-2xl p-4 border border-slate-200 shadow-sm">
                <div>
                  <h3 className="font-bold text-slate-900">Clinical Decision Support & Authorizations</h3>
                  <p className="text-xs text-slate-500">Automated pre-visit intelligence synthesis</p>
                </div>
                <button
                  onClick={() => setIsPrescriptionModalOpen(true)}
                  className="bg-blue-600 text-white text-xs font-semibold px-3 py-2 rounded-xl flex items-center space-x-1.5 hover:bg-blue-700 shadow-sm"
                >
                  <Plus className="w-4 h-4" />
                  <span>Authorize Prescription</span>
                </button>
              </div>

              {/* Patient Risk Stratification Card (v2.0) */}
              {patientRisk && (
                <div className={`rounded-2xl p-4 border flex items-center justify-between shadow-sm ${
                  patientRisk.risk_tier === 'high' ? 'bg-rose-50 border-rose-200' :
                  patientRisk.risk_tier === 'medium' ? 'bg-amber-50 border-amber-200' :
                  'bg-emerald-50 border-emerald-200'
                }`}>
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-slate-700">Patient Risk Stratification</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                        patientRisk.risk_tier === 'high' ? 'bg-rose-200 text-rose-900' :
                        patientRisk.risk_tier === 'medium' ? 'bg-amber-200 text-amber-900' :
                        'bg-emerald-200 text-emerald-900'
                      }`}>
                        {patientRisk.risk_tier} RISK (Score: {patientRisk.risk_score})
                      </span>
                    </div>
                    <p className="text-xs text-slate-700">
                      <strong>Contributing Factors:</strong> {patientRisk.contributing_factors?.length ? patientRisk.contributing_factors.join(', ') : 'No elevated risk factors detected.'}
                    </p>
                    <p className="text-[11px] text-slate-500 italic">Recommendation: {patientRisk.recommendation}</p>
                  </div>
                </div>
              )}

              {/* AI Clinical Intelligence Briefing */}
              {doctorBriefing && (

                <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <div className="flex items-center space-x-2">
                      <Sparkles className="w-5 h-5 text-blue-600" />
                      <span className="font-bold text-slate-900">AI Clinical Pre-Visit Synthesis</span>
                    </div>
                    <span className="text-xs text-slate-400">Generated on-demand via EHR & Observation models</span>
                  </div>

                  <div className="prose prose-sm max-w-none text-slate-700 whitespace-pre-line leading-relaxed">
                    {doctorBriefing.briefing_markdown}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* ========================================================================= */}
      {/* 3. MODALS (STAGED BOOKING CONFIRMATION, UPLOAD LAB, AUTHORIZE RX)         */}
      {/* ========================================================================= */}

      {/* Modal 1: 2-Step Appointment Booking Confirmation (Human In The Loop) */}
      {stagedBooking && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl p-6 max-w-md w-full shadow-2xl border border-slate-200 space-y-4 animate-in fade-in zoom-in duration-150">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-teal-700">
                <Calendar className="w-5 h-5" />
                <h4 className="font-bold text-slate-900">Confirm Appointment Booking</h4>
              </div>
              <button onClick={() => setStagedBooking(null)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="bg-teal-50 border border-teal-200 rounded-2xl p-4 text-xs space-y-2">
              <div className="flex justify-between">
                <span className="text-teal-900 font-bold">Doctor:</span>
                <span className="text-slate-800">{stagedBooking.doctor_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-teal-900 font-bold">Department:</span>
                <span className="text-slate-800">{stagedBooking.department}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-teal-900 font-bold">Date & Time:</span>
                <span className="text-slate-800 font-semibold">{stagedBooking.datetime}</span>
              </div>
            </div>

            <p className="text-xs text-slate-500">
              ⚠️ In accordance with hospital protocol, booking is staged in an uncommitted state until you explicitly click confirm below.
            </p>

            <div className="flex items-center space-x-3 pt-2">
              <button
                onClick={() => handleConfirmAppointment(stagedBooking.stage_id)}
                className="flex-1 bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold py-2.5 rounded-xl shadow-md transition-all"
              >
                Yes, Confirm & Book
              </button>
              <button
                onClick={() => setStagedBooking(null)}
                className="px-4 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold py-2.5 rounded-xl transition-all"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal 2: Ingest/Simulate Lab Report */}
      {isUploadModalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl p-6 max-w-md w-full shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-teal-700">
                <FileText className="w-5 h-5" />
                <h4 className="font-bold text-slate-900">Ingest New Lab Report</h4>
              </div>
              <button onClick={() => setIsUploadModalOpen(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUploadLab} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Test Name</label>
                <input
                  type="text"
                  value={uploadForm.test_name}
                  onChange={(e) => setUploadForm({ ...uploadForm, test_name: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 focus:ring-2 focus:ring-teal-500 focus:outline-none"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Value</label>
                  <input
                    type="number"
                    step="0.1"
                    value={uploadForm.value}
                    onChange={(e) => setUploadForm({ ...uploadForm, value: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 focus:ring-2 focus:ring-teal-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Unit</label>
                  <input
                    type="text"
                    value={uploadForm.unit}
                    onChange={(e) => setUploadForm({ ...uploadForm, unit: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 focus:ring-2 focus:ring-teal-500 focus:outline-none"
                  />
                </div>
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Collection Date</label>
                <input
                  type="date"
                  value={uploadForm.date}
                  onChange={(e) => setUploadForm({ ...uploadForm, date: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 focus:ring-2 focus:ring-teal-500 focus:outline-none"
                />
              </div>

              <div className="pt-3">
                <button
                  type="submit"
                  className="w-full bg-teal-600 hover:bg-teal-700 text-white font-bold py-2.5 rounded-xl shadow-md transition-all text-xs"
                >
                  Process & Store in FHIR Record
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal 3: Doctor Clinician Prescription Authorization */}
      {isPrescriptionModalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl p-6 max-w-lg w-full shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-blue-700">
                <Stethoscope className="w-5 h-5" />
                <h4 className="font-bold text-slate-900">Clinician Prescription Authorization</h4>
              </div>
              <button onClick={() => setIsPrescriptionModalOpen(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAuthorizeNewPrescription} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Medication Name</label>
                  <input
                    type="text"
                    value={newMedForm.name}
                    onChange={(e) => setNewMedForm({ ...newMedForm, name: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Dosage</label>
                  <input
                    type="text"
                    value={newMedForm.dose}
                    onChange={(e) => setNewMedForm({ ...newMedForm, dose: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Frequency</label>
                <input
                  type="text"
                  value={newMedForm.frequency}
                  onChange={(e) => setNewMedForm({ ...newMedForm, frequency: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Clinical Purpose</label>
                <input
                  type="text"
                  value={newMedForm.purpose}
                  onChange={(e) => setNewMedForm({ ...newMedForm, purpose: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Instructions</label>
                <textarea
                  rows="2"
                  value={newMedForm.instructions}
                  onChange={(e) => setNewMedForm({ ...newMedForm, instructions: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                ></textarea>
              </div>

              <div className="pt-3">
                <button
                  type="submit"
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2.5 rounded-xl shadow-md transition-all text-xs"
                >
                  Sign & Authorize Prescription
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal 4: Patient Vitals Logger (v2.0) */}
      {isLogVitalModalOpen && (

        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl p-6 max-w-md w-full shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-teal-700">
                <Activity className="w-5 h-5" />
                <h4 className="font-bold text-slate-900">Log Vital Sign Reading</h4>
              </div>
              <button onClick={() => setIsLogVitalModalOpen(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleLogVital} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Vital Sign</label>
                <select
                  value={vitalForm.vital_type}
                  onChange={(e) => {
                    const vt = e.target.value;
                    const defaultUnits = {
                      blood_pressure: 'mmHg',
                      heart_rate: 'bpm',
                      glucose: 'mg/dL',
                      spo2: '%',
                      temperature: '°F',
                      weight: 'kg'
                    };
                    setVitalForm({ ...vitalForm, vital_type: vt, unit: defaultUnits[vt] || '' });
                  }}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 focus:ring-2 focus:ring-teal-500 focus:outline-none"
                >
                  <option value="blood_pressure">Blood Pressure (e.g. 120/80)</option>
                  <option value="heart_rate">Heart Rate (bpm)</option>
                  <option value="glucose">Blood Glucose (mg/dL)</option>
                  <option value="spo2">Oxygen Saturation SpO2 (%)</option>
                  <option value="temperature">Body Temperature (°F)</option>
                  <option value="weight">Body Weight (kg)</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Measurement Value</label>
                  <input
                    type="text"
                    required
                    value={vitalForm.value}
                    onChange={(e) => setVitalForm({ ...vitalForm, value: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 focus:ring-2 focus:ring-teal-500 focus:outline-none"
                    placeholder="e.g. 120/80 or 75"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Unit</label>
                  <input
                    type="text"
                    readOnly
                    value={vitalForm.unit}
                    className="w-full bg-slate-100 border border-slate-200 rounded-xl p-2.5 text-slate-500"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Observation Notes</label>
                <input
                  type="text"
                  value={vitalForm.notes}
                  onChange={(e) => setVitalForm({ ...vitalForm, notes: e.target.value })}
                  placeholder="e.g. Morning resting reading"
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 focus:ring-2 focus:ring-teal-500 focus:outline-none"
                />
              </div>

              <div className="pt-3">
                <button
                  type="submit"
                  className="w-full bg-teal-600 hover:bg-teal-700 text-white font-bold py-2.5 rounded-xl shadow-md transition-all text-xs"
                >
                  Save & Evaluate Reading
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

