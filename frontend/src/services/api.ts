import { User, DashboardStats, TemplateItem, VerificationResult, DemoDocItem } from '../types';

const API_BASE = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '');

function getHeaders(isFormData = false): Record<string, string> {
  const token = localStorage.getItem('auth_token');
  const headers: Record<string, string> = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  if (!isFormData) {
    headers['Content-Type'] = 'application/json';
  }
  return headers;
}

export const api = {
  // Auth
  async login(user_id_or_email: string, password: string): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id_or_email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(err.detail || 'Authentication failed');
    }
    const data = await res.json();
    localStorage.setItem('auth_token', data.access_token);
    localStorage.setItem('auth_user', JSON.stringify(data.user));
    return data;
  },

  async quickSwitchRole(role: string): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${API_BASE}/auth/quick-switch/${role}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) {
      throw new Error('Could not switch role');
    }
    const data = await res.json();
    localStorage.setItem('auth_token', data.access_token);
    localStorage.setItem('auth_user', JSON.stringify(data.user));
    return data;
  },

  async getMe(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to get user profile');
    return res.json();
  },

  logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
  },

  getStoredUser(): User | null {
    try {
      const u = localStorage.getItem('auth_user');
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  },

  // Document Upload
  async uploadDocument(file: File, documentType: string) {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('document_type', documentType);

    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      headers: getHeaders(true),
      body: fd,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  async batchUpload(files: File[], documentType: string) {
    const fd = new FormData();
    files.forEach(f => fd.append('files', f));
    fd.append('document_type', documentType);

    const res = await fetch(`${API_BASE}/documents/batch-upload`, {
      method: 'POST',
      headers: getHeaders(true),
      body: fd,
    });
    if (!res.ok) {
      throw new Error('Batch upload failed');
    }
    return res.json();
  },

  // Verification
  async runVerification(
    documentId: string,
    documentType: string,
    templateId?: string,
    allowDemoAuth = false
  ): Promise<VerificationResult> {
    const res = await fetch(`${API_BASE}/verification/run`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        document_id: documentId,
        document_type: documentType,
        template_id: templateId || null,
        allow_demo_authoritative_provider: allowDemoAuth,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Verification run failed' }));
      throw new Error(err.detail || 'Verification run failed');
    }
    return res.json();
  },

  async getVerification(id: string): Promise<VerificationResult> {
    const res = await fetch(`${API_BASE}/verification/${id}`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Verification record not found');
    return res.json();
  },

  async getVerificationHistory(search?: string, status?: string, documentType?: string) {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (status) params.append('status', status);
    if (documentType) params.append('document_type', documentType);

    const res = await fetch(`${API_BASE}/verification/history?${params.toString()}`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to load history');
    return res.json();
  },

  async submitOfficerReview(
    verificationId: string,
    decision: 'APPROVED' | 'FLAGGED' | 'OVERRIDDEN',
    notes: string,
    newStatus?: string
  ) {
    const res = await fetch(`${API_BASE}/verification/${verificationId}/review`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ decision, notes, new_status: newStatus }),
    });
    if (!res.ok) throw new Error('Failed to submit officer review');
    return res.json();
  },

  // Dashboard
  async getDashboardStats(): Promise<DashboardStats> {
    const res = await fetch(`${API_BASE}/dashboard/statistics`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to load dashboard statistics');
    return res.json();
  },

  // Templates
  async getTemplates(): Promise<TemplateItem[]> {
    const res = await fetch(`${API_BASE}/templates/`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to load templates');
    return res.json();
  },

  async learnTemplateFromSample(formData: FormData) {
    const res = await fetch(`${API_BASE}/templates/learn-from-sample`, {
      method: 'POST',
      headers: getHeaders(true),
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Template learning failed' }));
      throw new Error(err.detail || 'Template learning failed');
    }
    return res.json();
  },

  async toggleTemplateStatus(id: string, status: string) {
    const res = await fetch(`${API_BASE}/templates/${id}/status?status=${status}`, {
      method: 'PUT',
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to update status');
    return res.json();
  },

  async deleteTemplate(id: string) {
    const res = await fetch(`${API_BASE}/templates/${id}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to delete template');
    return res.json();
  },

  // Demo
  async getDemoDocuments(): Promise<DemoDocItem[]> {
    const res = await fetch(`${API_BASE}/demo/documents`);
    if (!res.ok) throw new Error('Failed to load demo documents');
    return res.json();
  },

  async loadDemoDocument(demoId: string) {
    const res = await fetch(`${API_BASE}/demo/load/${demoId}`, {
      method: 'POST',
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to load demo file');
    return res.json();
  },
};
