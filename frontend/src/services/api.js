/**
 * CareAgent API Client Service
 * Centralized client for all backend communication.
 * Handles JWT authentication, request headers, and error handling.
 */

const API_BASE = import.meta.env?.VITE_API_BASE_URL || '/api';

class ApiClient {
  constructor() {
    this.token = null;
  }

  setToken(token) {
    this.token = token;
  }

  getToken() {
    return this.token;
  }

  getHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...(options.headers || {})
      }
    };

    try {
      const res = await fetch(url, config);
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(errorData.detail || `Request failed with status ${res.status}`);
      }
      return await res.json();
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  }

  // --- Authentication ---
  auth = {
    login: (username, password) => 
      this.request('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password })
      }),
    switchDemoRole: (role) => 
      this.request('/auth/switch-demo-role', {
        method: 'POST',
        body: JSON.stringify({ role })
      }),
    getMe: () => this.request('/auth/me')
  };

  // --- Patient EHR Records ---
  patients = {
    getProfile: () => this.request('/patients/profile'),
    getConditions: () => this.request('/patients/conditions')
  };

  // --- Agentic AI Chat ---
  chat = {
    sendMessage: (message, patient_id = null) => 
      this.request('/chat/send', {
        method: 'POST',
        body: JSON.stringify({ message, patient_id })
      })
  };

  // --- Lab Reports & Diagnostics ---
  reports = {
    getLatest: () => this.request('/reports/latest'),
    getTrends: (testName = 'HbA1c') => 
      this.request(`/reports/trends?test_name=${encodeURIComponent(testName)}`),
    upload: (reportData) => 
      this.request('/reports/upload', {
        method: 'POST',
        body: JSON.stringify(reportData)
      })
  };

  // --- Appointments ---
  appointments = {
    getMy: () => this.request('/appointments/my'),
    getSlots: (department = null, doctor = null) => {
      const params = new URLSearchParams();
      if (department) params.append('department', department);
      if (doctor) params.append('doctor', doctor);
      const query = params.toString() ? `?${params.toString()}` : '';
      return this.request(`/appointments/slots${query}`);
    },
    stage: (slotId, reason = 'Routine consultation') => 
      this.request('/appointments/stage', {
        method: 'POST',
        body: JSON.stringify({ slot_id: slotId, reason })
      }),
    confirm: (stageId) => 
      this.request('/appointments/confirm', {
        method: 'POST',
        body: JSON.stringify({ stage_id: stageId })
      }),
    cancel: (appointmentId) => 
      this.request(`/appointments/${appointmentId}`, {
        method: 'DELETE'
      })
  };

  // --- Medications & Adherence ---
  medications = {
    getPrescribed: () => this.request('/medications/prescribed'),
    getSchedule: () => this.request('/medications/schedule'),
    getAdherence: () => this.request('/medications/adherence'),
    logAdherence: (medicationId, status, notes = null) => 
      this.request('/medications/adherence/log', {
        method: 'POST',
        body: JSON.stringify({ medication_id: medicationId, status, notes })
      })
  };

  // --- Vitals Monitoring (v2.0) ---
  vitals = {
    log: (vitalType, value, unit, notes = null) => 
      this.request('/vitals/log', {
        method: 'POST',
        body: JSON.stringify({ vital_type: vitalType, value, unit, notes })
      }),
    getHistory: (vitalType = 'blood_pressure', limit = 30) => 
      this.request(`/vitals/history?vital_type=${encodeURIComponent(vitalType)}&limit=${limit}`),
    getSummary: () => this.request('/vitals/summary'),
    getAlerts: () => this.request('/vitals/alerts')
  };

  // --- Notifications & Reminders (v2.0) ---
  notifications = {
    getAll: (unreadOnly = false, limit = 50) => 
      this.request(`/notifications/?unread_only=${unreadOnly}&limit=${limit}`),
    markAsRead: (id) => 
      this.request(`/notifications/${id}/read`, { method: 'POST' }),
    markAllRead: () => 
      this.request('/notifications/read-all', { method: 'POST' }),
    getPreferences: () => this.request('/notifications/preferences'),
    updatePreferences: (prefs) => 
      this.request('/notifications/preferences', {
        method: 'PUT',
        body: JSON.stringify(prefs)
      })
  };

  // --- Health Dashboard & Summary (v2.0) ---
  health = {
    getDashboard: () => this.request('/health/dashboard'),
    getRiskStratification: (patientId) => 
      this.request(`/health/risk-stratification?patient_id=${encodeURIComponent(patientId)}`)
  };

  // --- Doctor Clinical Portal ---
  doctor = {
    getPatients: () => this.request('/doctor/patients'),
    getAIBriefing: (patientId) => 
      this.request(`/doctor/patient/${patientId}/ai-briefing`),
    authorizePrescription: (prescriptionData) => 
      this.request('/doctor/prescriptions/authorize', {
        method: 'POST',
        body: JSON.stringify(prescriptionData)
      }),
    getAuditLogs: () => this.request('/doctor/audit-logs')
  };
}

export const api = new ApiClient();
export default api;
