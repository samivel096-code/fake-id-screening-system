# Implementation Plan: AI-Based Fake Identity & Document Screening System

Build and finalize a complete, production-quality full-stack web application for authorized officers to screen identity and official documents against reference templates, performing multi-stage automated validation checks.

## User Review Required

> [!IMPORTANT]
> **Core Authenticity Principle (Strict Rule)**:
> The system strictly distinguishes **Template Match** from **Legal Authenticity**. A 100% template match is reported as `Template Match: 100%` and classified as `LIKELY AUTHENTIC` (with the mandatory disclaimer that template matching alone does not establish legal authenticity), while `VERIFIED` is reserved strictly for authoritative government source verification. All mock verification providers are explicitly badged `DEMO ONLY — NOT OFFICIAL VERIFICATION`.

> [!NOTE]
> **Runtime Environment**:
> Windows 11 with Python 3.14, Node.js v24, OpenCV, and hardware-accelerated `winocr` (Windows Media OCR) + `pytesseract`. All backend packages and frontend dependencies are verified and functional.

---

## Proposed Changes

### 1. Backend Core & Services Refinement

#### [MODIFY] [`backend/app/services/integrity_analysis_service.py`](file:///c:/Users/laptop/Downloads/AI_Document_Screening_App%205555/backend/app/services/integrity_analysis_service.py)
- Refine the Error Level Analysis (ELA) and noise inconsistency algorithms to prevent false positives on clean vector lines, header borders, and normal font edges.
- Mask out extreme-aspect-ratio divider lines and standard text gradients before evaluating background compression anomalies.
- Accurately flag genuine digital splicing/tampering (e.g. the spliced patch in the demo altered Aadhaar) with bounding boxes, high severity, and descriptive tags (`Potential alteration indicators detected. Manual review recommended.`).

#### [MODIFY] [`backend/app/services/qr_service.py`](file:///c:/Users/laptop/Downloads/AI_Document_Screening_App%205555/backend/app/services/qr_service.py)
- Ensure robust OpenCV QRCodeDetector decoding across raw JSON, UIDAI XML, key-value, and text payloads.
- Format QR analysis output according to Section 15 specifications:
  - `QR Detected: YES / NO`
  - `Readable: YES / NO`
  - `Data: AVAILABLE / NOT AVAILABLE`
  - `Visible Data Match: MATCH / MISMATCH`
  - `Authorized Verification: NOT AVAILABLE (DEMO ONLY)`
- Implement Section 16 mismatch notes: When visible name and QR name differ, flag `QR INFORMATION MISMATCH` and append `"The information encoded in the QR code does not match the corresponding visible document information."`

#### [MODIFY] [`backend/app/services/verification_service.py`](file:///c:/Users/laptop/Downloads/AI_Document_Screening_App%205555/backend/app/services/verification_service.py)
- Ensure strict compliance with the 4 result classifications:
  - `VERIFIED`: Authoritative verification provider confirms document (or simulated demo mode enabled).
  - `LIKELY AUTHENTIC`: High template match, consistent OCR, matching QR, required fields detected, no significant alteration indicators, authoritative source unavailable.
  - `SUSPICIOUS / LIKELY ALTERED`: Major template mismatch, QR mismatch, significant data mismatch, multiple alteration indicators, or missing required fields.
  - `UNABLE TO VERIFY`: Image unreadable, OCR fails, or verification cannot be completed reliably.
- Inject the exact Section 22 legal disclaimer into all screening responses:
  `"IMPORTANT: Template and document checks are consistent, but design matching alone does not establish legal authenticity. Use an authorized verification source where available. NEVER display '100% REAL' just because the design matches."`

#### [MODIFY] [`backend/app/utils/seed_data.py`](file:///c:/Users/laptop/Downloads/AI_Document_Screening_App%205555/backend/app/utils/seed_data.py)
- Expand pre-configured template profiles to cover all 16 document types specified in Section 4 (Aadhaar, PAN Card, Driving Licence, Passport, Voter ID, Birth Certificate, Death Certificate, Caste Certificate, Income Certificate, Community Certificate, Educational Certificate, Vehicle Registration Certificate, Government Certificate, Business Certificate, Invoice, Other / Custom Document).
- Ensure generated synthetic demo documents (`demo_aadhaar_valid.png`, `demo_aadhaar_altered.png`, `demo_pan_valid.png`, `demo_blurry_unreadable.png`) have clean, high-fidelity layouts and predictable test outcomes.

---

### 2. Frontend UI/UX & Components

#### [MODIFY] [`frontend/src/pages/VerifyDocumentPage.tsx`](file:///c:/Users/laptop/Downloads/AI_Document_Screening_App%205555/frontend/src/pages/VerifyDocumentPage.tsx)
- Add explicit Image Quality Success confirmation card (Section 9):
  - `✓ Document completely visible`
  - `✓ Resolution sufficient`
  - `✓ Text readable`
  - `✓ Blur acceptable`
  - `✓ Lighting acceptable`
  - `✓ Document orientation acceptable`
- Add dedicated QR Verification Status card (Section 15 & 16) displaying QR detected status, readability, visible data match, and authorized verification tag.
- Add Document Type Mismatch alert banner (Section 12) if the uploaded document does not match the selected document type.
- Add Print/Export Verification Report layout for officers.

#### [MODIFY] [`frontend/src/components/VisualReviewViewer.tsx`](file:///c:/Users/laptop/Downloads/AI_Document_Screening_App%205555/frontend/src/components/VisualReviewViewer.tsx)
- Enhance interactive issue inspection (Section 24 & 25): Clicking any flagged issue highlights and pulses the exact region on the document canvas.
- Support side-by-side comparison between the authorized reference sample and normalized uploaded document, plus the alignment difference heatmap overlay.

#### [MODIFY] [`frontend/src/components/DataComparisonTable.tsx`](file:///c:/Users/laptop/Downloads/AI_Document_Screening_App%205555/frontend/src/components/DataComparisonTable.tsx)
- Confirm sensitive identifier masking (`XXXX XXXX 1012` for Aadhaar, `XXXXX1234F` for PAN) in both visible and QR fields.
- Format match states clearly: `MATCH`, `PARTIAL MATCH`, `MISMATCH`, `NOT FOUND`, `NOT AVAILABLE`.

#### [MODIFY] [`frontend/src/pages/BulkScreeningPage.tsx`](file:///c:/Users/laptop/Downloads/AI_Document_Screening_App%205555/frontend/src/pages/BulkScreeningPage.tsx)
- Ensure batch processing shows real-time progress bar (e.g. `Processing 32/50`), aggregate cards (Verified, Likely Authentic, Suspicious, Needs Review, Unable to Verify), and filter to inspect only documents requiring attention (Section 28).

#### [MODIFY] [`frontend/src/pages/DashboardPage.tsx`](file:///c:/Users/laptop/Downloads/AI_Document_Screening_App%205555/frontend/src/pages/DashboardPage.tsx)
- Ensure all 7 cards (Total Documents, Processing, Verified, Likely Authentic, Suspicious, Unable to Verify, Needs Review) and 5 charts (Daily Document Processing, Status Distribution, Document Types, Suspicious Documents, QR Verification Results) are visually rich and responsive.

---

## Verification Plan

### Automated & Backend Service Tests
1. Test Image Quality Service:
   - Valid image returns `acceptable = True` with high scores.
   - Blurry image (`demo_blurry_unreadable.png`) returns `acceptable = False`, halts screening with `"DOCUMENT NOT CLEAR"`, and lists specific defect reasons.
2. Test OCR & QR extraction:
   - `demo_aadhaar_valid.png`: Name, DOB, Aadhaar UID extracted; QR decoded; data matches 100%.
   - `demo_aadhaar_altered.png`: Visible Name = `VIKRAM SINGH (TAMPERED)`, QR Name = `ORIGINAL HOLDER RAJESH`; triggers `QR INFORMATION MISMATCH` and `MISMATCH` note.
3. Test Template Matching & Integrity:
   - Valid document produces high template match score without false compression alarms.
   - Spliced patch in altered document is detected and flagged on canvas coordinates.
4. Test Result Classification:
   - Valid Aadhaar -> `LIKELY AUTHENTIC` with template match score and legal disclaimer.
   - Altered Aadhaar -> `SUSPICIOUS / LIKELY ALTERED` with manual review recommended.
   - Blurry Document -> `UNABLE TO VERIFY` / `DOCUMENT NOT CLEAR`.

### Browser & UI Verification
1. Launch Backend API (`uvicorn app.main:app --port 8000`) and Frontend Dev Server (`npm.cmd run dev`).
2. Run Browser Subagent to:
   - Verify login with officer credentials (`officer@screening.gov` / `Officer@123`).
   - Navigate to Dashboard and verify all 7 cards and charts.
   - Execute 1-Click screening for:
     a. Authentic Sample Aadhaar -> verify `LIKELY AUTHENTIC` outcome, score card, and Section 22 disclaimer.
     b. Tampered Aadhaar -> verify `SUSPICIOUS / LIKELY ALTERED`, visual canvas highlighting of flagged spliced patch and QR mismatch.
     c. Blurry Document -> verify `DOCUMENT NOT CLEAR` rejection screen with reasons and `[ Upload Clear Image ]`.
   - Test Document Comparison view (Side-by-Side and Alignment Heatmap Overlay).
   - Test Bulk Screening batch upload simulation.
   - Test Verification History search and filtering.
   - Test Reference Templates management.
