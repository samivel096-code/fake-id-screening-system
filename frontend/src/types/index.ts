export type UserRole = 'ADMIN' | 'OFFICER' | 'REVIEWER' | 'VIEWER';

export interface User {
  id: string;
  email: string;
  user_id: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
}

export interface AuthState {
  user: User | null;
  token: string | null;
}

export interface QualityCheckDetail {
  status: 'PASS' | 'FAIL' | 'WARN';
  score: number;
  detail: string;
}

export interface ImageQuality {
  acceptable: boolean;
  summary: string;
  overall_score: number;
  blur_score: number;
  brightness: number;
  contrast: number;
  glare_ratio: number;
  shadow_ratio: number;
  estimated_tilt: number;
  width: number;
  height: number;
  aspect_ratio: number;
  reasons: string[];
  checks: Record<string, QualityCheckDetail>;
}

export interface FlaggedIssue {
  id: string;
  type: 'TEMPLATE_MISMATCH' | 'QR_MISMATCH' | 'INTEGRITY_ANOMALY' | 'MISSING_FIELD' | 'QUALITY_WARNING' | 'OCR_WARNING';
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  description: string;
  region?: {
    x: number;
    y: number;
    width: number;
    height: number;
    x_ratio?: number;
    y_ratio?: number;
    w_ratio?: number;
    h_ratio?: number;
  };
}

export interface DataComparisonRow {
  field: string;
  extracted_value: string;
  reference_or_qr_value: string;
  result: 'MATCH' | 'PARTIAL MATCH' | 'MISMATCH' | 'NOT FOUND' | 'NOT AVAILABLE';
  details?: string;
}

export interface ScoreBreakdown {
  template_match: number;
  ocr_consistency: number;
  qr_consistency: number;
  required_fields: number;
  image_quality: number;
  integrity_screening: number;
  authorized_verification: string;
  template_details?: {
    layout?: number;
    field_positions?: number;
    typography_layout?: number;
    symbols?: number;
    qr_position?: number;
    dimensions?: number;
  };
}

export interface VerificationResult {
  id: string;
  document_id: string;
  document_type: string;
  template_id?: string;
  template_name?: string;
  officer_id?: string;
  officer_name?: string;
  status: 'VERIFIED' | 'LIKELY AUTHENTIC' | 'SUSPICIOUS / LIKELY ALTERED' | 'UNABLE TO VERIFY';
  screening_score: number;
  breakdown: ScoreBreakdown;
  validation_notes: string[];
  recommendation: string;
  legal_disclaimer: string;
  flagged_issues: FlaggedIssue[];
  data_comparison: DataComparisonRow[];
  extracted_fields: Record<string, any>;
  qr_analysis: {
    detected: boolean;
    readable: boolean;
    data_available?: boolean;
    visible_data_match?: string;
    authorized_verification?: string;
    discrepancies?: string[];
    format?: string;
    raw_data?: string;
    parsed_data?: Record<string, any>;
  };
  image_quality?: ImageQuality;
  integrity_screening?: {
    integrity_score: number;
    indicator_count: number;
    indicators: string[];
  };
  normalized_image_url?: string;
  overlay_image_url?: string;
  sample_image_url?: string;
  text_boxes?: Array<{
    text: string;
    box: { x: number; y: number; width: number; height: number };
  }>;
  qr_box?: {
    x: number;
    y: number;
    width: number;
    height: number;
    polygon?: number[][];
  };
  manual_review_needed: boolean;
  officer_review_decision?: 'APPROVED' | 'FLAGGED' | 'OVERRIDDEN' | null;
  officer_notes?: string | null;
  reviewed_by?: string | null;
  reviewed_at?: string | null;
  created_at: string;
}

export interface TemplateItem {
  id: string;
  document_type: string;
  template_name: string;
  version: string;
  issuing_org?: string;
  status: 'ACTIVE' | 'INACTIVE';
  is_default: boolean;
  aspect_ratio?: number;
  expected_width?: number;
  expected_height?: number;
  sample_image_url?: string;
  profile: {
    document_type: string;
    version: string;
    aspect_ratio: number;
    expected_width: number;
    expected_height: number;
    required_sections: string[];
    expected_fields: Array<{
      name: string;
      label: string;
      required: boolean;
      data_type?: string;
    }>;
    has_qr_code: boolean;
    expected_qr_region?: Record<string, number>;
    expected_symbols?: Array<Record<string, any>>;
  };
  created_by: string;
  created_at: string;
  updated_at?: string;
}

export interface DashboardStats {
  total_documents: number;
  processing: number;
  verified: number;
  likely_authentic: number;
  suspicious: number;
  unable_to_verify: number;
  needs_review: number;
  daily_processing: Array<{
    date: string;
    processed: number;
    verified: number;
    suspicious: number;
  }>;
  status_distribution: Array<{
    name: string;
    value: number;
    color: string;
  }>;
  document_type_distribution: Array<{
    name: string;
    count: number;
  }>;
  qr_verification_stats: {
    match_rate: number;
    total_scanned: number;
    mismatches: number;
  };
  recent_verifications: Array<{
    id: string;
    document_id: string;
    document_type: string;
    status: string;
    screening_score: number;
    officer_name: string;
    created_at: string;
  }>;
}

export interface DemoDocItem {
  id: string;
  title: string;
  document_type: string;
  filename: string;
  expected_outcome: string;
  description: string;
  url: string;
}
