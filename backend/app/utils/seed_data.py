import os
import json
import cv2
import numpy as np
import qrcode
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.template import DocumentTemplate
from app.models.document import Document
from app.models.verification import VerificationRecord
from app.models.audit import AuditLog
from app.utils.security import get_password_hash

SAMPLE_DIR = os.path.join("uploads", "templates")
DEMO_DIR = os.path.join("uploads", "demo_docs")

def generate_sample_aadhaar_image(output_path: str, qr_text: str = None, name: str = "RAJESH KUMAR", uid: str = "9876 5432 1012", dob: str = "15/08/1988", gender: str = "MALE"):
    """Creates a synthetic, clearly synthetic/demo Aadhaar card image."""
    w, h = 1000, 650
    img = np.full((h, w, 3), 248, dtype=np.uint8)

    # Top tricolor decorative header banner
    cv2.rectangle(img, (0, 0), (w, 15), (34, 110, 240), -1)   # Saffron
    cv2.rectangle(img, (0, 15), (w, 25), (255, 255, 255), -1) # White
    cv2.rectangle(img, (0, 25), (w, 35), (34, 139, 34), -1)   # Green

    # Header text
    cv2.putText(img, "GOVERNMENT OF INDIA", (280, 75), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (20, 20, 20), 2)
    cv2.putText(img, "Unique Identification Authority of India", (250, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (80, 80, 80), 2)
    cv2.line(img, (40, 130), (w - 40, 130), (200, 200, 200), 2)

    # Photo box on left
    cv2.rectangle(img, (60, 160), (260, 420), (220, 220, 220), -1)
    cv2.rectangle(img, (60, 160), (260, 420), (100, 100, 100), 2)
    # Head & shoulders icon silhouette
    cv2.circle(img, (160, 250), 45, (160, 160, 160), -1)
    cv2.ellipse(img, (160, 370), (70, 50), 0, 0, 180, (160, 160, 160), -1)
    cv2.putText(img, "PHOTO", (130, 405), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)

    # Demographic details in center
    cv2.putText(img, name, (300, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.95, (10, 10, 10), 2)
    cv2.putText(img, f"DOB: {dob}", (300, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2)
    cv2.putText(img, f"Gender: {gender}", (300, 305), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2)
    cv2.putText(img, "Address: 123 Metro Enclave, Sector 4, New Delhi - 110001", (300, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (60, 60, 60), 1)

    # QR code on right
    if not qr_text:
        qr_dict = {
            "name": name,
            "dob": dob,
            "gender": gender,
            "document_id": uid.replace(" ", "")
        }
        qr_text = json.dumps(qr_dict)

    qr = qrcode.QRCode(box_size=4, border=2)
    qr.add_data(qr_text)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_mat = cv2.cvtColor(np.array(qr_img.convert("RGB")), cv2.COLOR_RGB2BGR)
    qr_mat = cv2.resize(qr_mat, (190, 190))
    
    # Place QR at (740, 170)
    img[170:360, 740:930] = qr_mat
    cv2.rectangle(img, (740, 170), (930, 360), (180, 180, 180), 1)

    # Red divider line above UID
    cv2.line(img, (40, 470), (w - 40, 470), (0, 0, 180), 3)

    # UID 12-digit number at bottom center
    cv2.putText(img, uid, (320, 535), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (180, 0, 0), 3)
    cv2.putText(img, "Mera Aadhaar, Meri Pehchan", (350, 580), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 1)

    # Watermark / disclaimer
    cv2.putText(img, "FICTIONAL DEMO SAMPLE - AUTHORIZED SCREENING PURPOSES ONLY", (120, 625), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (140, 140, 140), 1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, img)
    return output_path

def generate_sample_pan_image(output_path: str, pan: str = "ABCDE1234F", name: str = "SURESH SHARMA", father: str = "RAMESH SHARMA", dob: str = "12/04/1985"):
    """Creates a synthetic PAN card image."""
    w, h = 1000, 650
    img = np.full((h, w, 3), 245, dtype=np.uint8)

    # Blue top header
    cv2.rectangle(img, (0, 0), (w, 80), (180, 110, 30), -1)
    cv2.putText(img, "INCOME TAX DEPARTMENT", (260, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
    cv2.putText(img, "GOVT. OF INDIA", (410, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (230, 230, 230), 1)

    # Photo left
    cv2.rectangle(img, (60, 130), (240, 360), (220, 220, 220), -1)
    cv2.rectangle(img, (60, 130), (240, 360), (120, 120, 120), 2)
    cv2.circle(img, (150, 210), 40, (150, 150, 150), -1)
    cv2.ellipse(img, (150, 310), (60, 45), 0, 0, 180, (150, 150, 150), -1)

    # Details
    cv2.putText(img, "Permanent Account Number Card", (280, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (50, 50, 50), 2)
    cv2.putText(img, pan, (280, 190), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (10, 10, 10), 3)

    cv2.putText(img, "Name", (280, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (100, 100, 100), 1)
    cv2.putText(img, name, (280, 275), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (20, 20, 20), 2)

    cv2.putText(img, "Father's Name", (280, 325), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (100, 100, 100), 1)
    cv2.putText(img, father, (280, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (20, 20, 20), 2)

    cv2.putText(img, "Date of Birth", (280, 410), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (100, 100, 100), 1)
    cv2.putText(img, dob, (280, 445), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (20, 20, 20), 2)

    # QR Code on right
    qr_data = json.dumps({"pan": pan, "name": name, "father_name": father, "dob": dob})
    qr = qrcode.QRCode(box_size=4, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_mat = cv2.cvtColor(np.array(qr_img.convert("RGB")), cv2.COLOR_RGB2BGR)
    qr_mat = cv2.resize(qr_mat, (180, 180))
    img[180:360, 750:930] = qr_mat

    # Signature box
    cv2.rectangle(img, (280, 490), (520, 560), (255, 255, 255), -1)
    cv2.rectangle(img, (280, 490), (520, 560), (160, 160, 160), 1)
    cv2.putText(img, "Signature", (360, 535), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 0.9, (10, 10, 10), 2)

    # Disclaimer
    cv2.putText(img, "FICTIONAL DEMO SAMPLE - AUTHORIZED SCREENING PURPOSES ONLY", (120, 620), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (140, 140, 140), 1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, img)
    return output_path

def seed_database(db: Session):
    """Populates users, templates, and synthetic reference files."""
    os.makedirs(SAMPLE_DIR, exist_ok=True)
    os.makedirs(DEMO_DIR, exist_ok=True)

    # 1. Seed Users
    users_data = [
        {"email": "admin@screening.gov", "user_id": "ADMIN-001", "name": "System Administrator", "role": UserRole.ADMIN, "pwd": "Admin@123"},
        {"email": "officer@screening.gov", "user_id": "OFF-1042", "name": "Officer Priya Sharma", "role": UserRole.OFFICER, "pwd": "Officer@123"},
        {"email": "reviewer@screening.gov", "user_id": "REV-2005", "name": "Reviewer Arun Patel", "role": UserRole.REVIEWER, "pwd": "Reviewer@123"},
        {"email": "viewer@screening.gov", "user_id": "VIEW-3011", "name": "Audit Observer", "role": UserRole.VIEWER, "pwd": "Viewer@123"}
    ]

    for u in users_data:
        existing = db.query(User).filter((User.email == u["email"]) | (User.user_id == u["user_id"])).first()
        if not existing:
            new_u = User(
                id=str(u["user_id"]),
                email=u["email"],
                user_id=u["user_id"],
                full_name=u["name"],
                role=u["role"],
                hashed_password=get_password_hash(u["pwd"]),
                is_active=True
            )
            db.add(new_u)
    db.commit()

    # 2. Generate Reference Sample Images
    aadhaar_sample_path = os.path.join(SAMPLE_DIR, "aadhaar_reference_sample.png")
    pan_sample_path = os.path.join(SAMPLE_DIR, "pan_reference_sample.png")
    
    generate_sample_aadhaar_image(aadhaar_sample_path, name="RAJESH KUMAR", uid="9876 5432 1012")
    generate_sample_pan_image(pan_sample_path, pan="ABCDE1234F", name="SURESH SHARMA")

    # 3. Seed Document Templates
    templates = [
        {
            "doc_type": "Aadhaar",
            "name": "Aadhaar Standard Reference Template",
            "version": "v1.0",
            "issuing_org": "Unique Identification Authority of India (UIDAI)",
            "sample_path": aadhaar_sample_path,
            "profile": {
                "document_type": "Aadhaar",
                "aspect_ratio": 1.538,
                "expected_width": 1000,
                "expected_height": 650,
                "required_sections": ["HEADER_TRICOLOR", "PHOTO_LEFT", "DETAILS_CENTER", "QR_RIGHT", "UID_FOOTER"],
                "expected_fields": [
                    {"name": "name", "label": "Full Name", "required": True, "data_type": "string"},
                    {"name": "dob", "label": "Date of Birth", "required": True, "data_type": "date"},
                    {"name": "gender", "label": "Gender", "required": True, "data_type": "string"},
                    {"name": "document_id", "label": "Aadhaar Number (12 Digits)", "required": True, "data_type": "id", "pattern": r"^\d{4}\s\d{4}\s\d{4}$"},
                    {"name": "address", "label": "Address", "required": False, "data_type": "string"}
                ],
                "has_qr_code": True,
                "expected_qr_region": {"x_ratio": 0.74, "y_ratio": 0.26, "w_ratio": 0.19, "h_ratio": 0.29},
                "expected_symbols": [{"name": "Ashoka Emblem / Tricolor", "x_ratio": 0.05, "y_ratio": 0.05, "w_ratio": 0.9, "h_ratio": 0.12}]
            }
        },
        {
            "doc_type": "PAN Card",
            "name": "Income Tax Department PAN Template",
            "version": "v1.0",
            "issuing_org": "Income Tax Department of India",
            "sample_path": pan_sample_path,
            "profile": {
                "document_type": "PAN Card",
                "aspect_ratio": 1.538,
                "expected_width": 1000,
                "expected_height": 650,
                "required_sections": ["HEADER_NAVY", "PHOTO_LEFT", "PAN_CENTER", "QR_RIGHT", "SIGNATURE_BOX"],
                "expected_fields": [
                    {"name": "document_id", "label": "PAN (10 Characters)", "required": True, "data_type": "id", "pattern": r"^[A-Z]{5}[0-9]{4}[A-Z]$"},
                    {"name": "name", "label": "Cardholder Name", "required": True, "data_type": "string"},
                    {"name": "father_name", "label": "Father's Name", "required": True, "data_type": "string"},
                    {"name": "dob", "label": "Date of Birth", "required": True, "data_type": "date"}
                ],
                "has_qr_code": True,
                "expected_qr_region": {"x_ratio": 0.75, "y_ratio": 0.27, "w_ratio": 0.18, "h_ratio": 0.28}
            }
        },
        {
            "doc_type": "Driving Licence",
            "name": "State Transport Driving Licence Template",
            "version": "v2.0",
            "issuing_org": "Ministry of Road Transport and Highways",
            "sample_path": None,
            "profile": {
                "document_type": "Driving Licence",
                "aspect_ratio": 1.58,
                "expected_width": 1000,
                "expected_height": 630,
                "required_sections": ["HEADER", "DL_NUMBER", "DETAILS", "CHIP_OR_QR"],
                "expected_fields": [
                    {"name": "document_id", "label": "Driving Licence No", "required": True},
                    {"name": "name", "label": "Name", "required": True},
                    {"name": "dob", "label": "Date of Birth", "required": True}
                ],
                "has_qr_code": True
            }
        },
        {
            "doc_type": "Passport",
            "name": "Republic of India Passport Bio-Page",
            "version": "v1.0",
            "issuing_org": "Ministry of External Affairs",
            "sample_path": None,
            "profile": {
                "document_type": "Passport",
                "aspect_ratio": 1.42,
                "expected_width": 1000,
                "expected_height": 700,
                "required_sections": ["PASSPORT_HEADER", "PHOTO_LEFT", "DETAILS", "MRZ_ZONE"],
                "expected_fields": [
                    {"name": "document_id", "label": "Passport Number", "required": True},
                    {"name": "name", "label": "Given Names", "required": True},
                    {"name": "dob", "label": "Date of Birth", "required": True}
                ],
                "has_qr_code": False
            }
        },
        {
            "doc_type": "Voter ID",
            "name": "Election Commission E-EPIC Template",
            "version": "v1.0",
            "issuing_org": "Election Commission of India",
            "sample_path": None,
            "profile": {
                "document_type": "Voter ID",
                "aspect_ratio": 1.58,
                "expected_width": 1000,
                "expected_height": 630,
                "required_sections": ["HEADER", "EPIC_NO", "DETAILS"],
                "expected_fields": [
                    {"name": "document_id", "label": "EPIC Number", "required": True},
                    {"name": "name", "label": "Elector's Name", "required": True}
                ],
                "has_qr_code": True
            }
        },
        {
            "doc_type": "Birth Certificate",
            "name": "Municipal Corporation Birth Certificate",
            "version": "v1.0",
            "issuing_org": "Municipal Registrar of Births and Deaths",
            "sample_path": None,
            "profile": {
                "document_type": "Birth Certificate",
                "aspect_ratio": 0.707,  # A4 Portrait
                "expected_width": 700,
                "expected_height": 990,
                "required_sections": ["EMBLEM_HEADER", "REGISTRATION_DETAILS", "CHILD_INFO", "SEAL_SIGNATURE"],
                "expected_fields": [
                    {"name": "document_id", "label": "Registration Number", "required": True},
                    {"name": "name", "label": "Child Name", "required": True},
                    {"name": "dob", "label": "Date of Birth", "required": True}
                ],
                "has_qr_code": True
            }
        },
        {
            "doc_type": "Educational Certificate",
            "name": "University Degree Certificate Template",
            "version": "v1.0",
            "issuing_org": "State University / Board",
            "sample_path": None,
            "profile": {
                "document_type": "Educational Certificate",
                "aspect_ratio": 0.707,
                "expected_width": 700,
                "expected_height": 990,
                "required_sections": ["UNIVERSITY_CREST", "AWARD_CLAUSE", "CANDIDATE_NAME", "REGISTRATION_NO"],
                "expected_fields": [
                    {"name": "document_id", "label": "Enrollment / Roll No", "required": True},
                    {"name": "name", "label": "Candidate Name", "required": True}
                ],
                "has_qr_code": True
            }
        },
        {
            "doc_type": "Death Certificate",
            "name": "Registrar General Death Certificate",
            "version": "v1.0",
            "issuing_org": "Civil Registration System (CRS)",
            "sample_path": None,
            "profile": {
                "document_type": "Death Certificate",
                "aspect_ratio": 0.707,
                "expected_width": 700,
                "expected_height": 990,
                "required_sections": ["CREST", "DECEASED_DETAILS", "DATE_OF_DEATH", "CERTIFICATION"],
                "expected_fields": [
                    {"name": "document_id", "label": "Registration Number", "required": True},
                    {"name": "name", "label": "Deceased Name", "required": True},
                    {"name": "date_of_death", "label": "Date of Death", "required": True}
                ],
                "has_qr_code": True
            }
        },
        {
            "doc_type": "Caste Certificate",
            "name": "State Revenue Caste & Community Certificate",
            "version": "v1.0",
            "issuing_org": "Revenue & Disaster Management Department",
            "sample_path": None,
            "profile": {
                "document_type": "Caste Certificate",
                "aspect_ratio": 0.707,
                "expected_width": 700,
                "expected_height": 990,
                "required_sections": ["STATE_SEAL", "APPLICANT_DETAILS", "CASTE_CATEGORY", "TEHSILDAR_SIGNATURE"],
                "expected_fields": [
                    {"name": "document_id", "label": "Certificate Application Number", "required": True},
                    {"name": "name", "label": "Applicant Name", "required": True}
                ],
                "has_qr_code": True
            }
        },
        {
            "doc_type": "Income Certificate",
            "name": "Tahsildar Income Certificate",
            "version": "v1.0",
            "issuing_org": "Department of Revenue Administration",
            "sample_path": None,
            "profile": {
                "document_type": "Income Certificate",
                "aspect_ratio": 0.707,
                "expected_width": 700,
                "expected_height": 990,
                "required_sections": ["HEADER", "INCOME_ASSESSMENT", "FAMILY_ANNUAL_INCOME", "DIGITAL_SIGNATURE"],
                "expected_fields": [
                    {"name": "document_id", "label": "Certificate Number", "required": True},
                    {"name": "name", "label": "Applicant Name", "required": True}
                ],
                "has_qr_code": True
            }
        },
        {
            "doc_type": "Community Certificate",
            "name": "Permanent Community Certificate",
            "version": "v1.0",
            "issuing_org": "District Revenue Officer",
            "sample_path": None,
            "profile": {
                "document_type": "Community Certificate",
                "aspect_ratio": 0.707,
                "expected_width": 700,
                "expected_height": 990,
                "required_sections": ["HEADER", "COMMUNITY_DESIGNATION", "APPLICANT_INFO"],
                "expected_fields": [
                    {"name": "document_id", "label": "Registration Number", "required": True},
                    {"name": "name", "label": "Candidate Name", "required": True}
                ],
                "has_qr_code": True
            }
        },
        {
            "doc_type": "Vehicle Registration Certificate",
            "name": "Form 23 Vehicle Registration Certificate (RC)",
            "version": "v1.0",
            "issuing_org": "Regional Transport Authority (RTO)",
            "sample_path": None,
            "profile": {
                "document_type": "Vehicle Registration Certificate",
                "aspect_ratio": 1.58,
                "expected_width": 1000,
                "expected_height": 630,
                "required_sections": ["HEADER", "VEHICLE_NO", "CHASSIS_NO", "OWNER_INFO"],
                "expected_fields": [
                    {"name": "document_id", "label": "Vehicle Registration No", "required": True},
                    {"name": "name", "label": "Owner Name", "required": True}
                ],
                "has_qr_code": True
            }
        },
        {
            "doc_type": "Government Certificate",
            "name": "Official Gazetted Government Certificate",
            "version": "v1.0",
            "issuing_org": "State / Central Government Authority",
            "sample_path": None,
            "profile": {
                "document_type": "Government Certificate",
                "aspect_ratio": 0.707,
                "expected_width": 700,
                "expected_height": 990,
                "required_sections": ["HEADER_EMBLEM", "NOTIFICATION_NO", "CERTIFICATE_BODY"],
                "expected_fields": [
                    {"name": "document_id", "label": "Order / Certificate Ref", "required": True},
                    {"name": "name", "label": "Recipient Name", "required": True}
                ],
                "has_qr_code": True
            }
        },
        {
            "doc_type": "Business Certificate",
            "name": "Ministry of Corporate Affairs Certificate of Incorporation",
            "version": "v1.0",
            "issuing_org": "Registrar of Companies (ROC)",
            "sample_path": None,
            "profile": {
                "document_type": "Business Certificate",
                "aspect_ratio": 0.707,
                "expected_width": 700,
                "expected_height": 990,
                "required_sections": ["MCA_CREST", "CIN_IDENTIFIER", "COMPANY_NAME", "REGISTRAR_SEAL"],
                "expected_fields": [
                    {"name": "document_id", "label": "CIN / Registration No", "required": True},
                    {"name": "name", "label": "Company / Entity Name", "required": True}
                ],
                "has_qr_code": True
            }
        },
        {
            "doc_type": "Invoice",
            "name": "Standard GST Tax Invoice",
            "version": "v1.0",
            "issuing_org": "Commercial Billing System",
            "sample_path": None,
            "profile": {
                "document_type": "Invoice",
                "aspect_ratio": 0.707,
                "expected_width": 700,
                "expected_height": 990,
                "required_sections": ["HEADER", "INVOICE_NO", "BILL_TO", "ITEM_TOTALS", "IRN_QR"],
                "expected_fields": [
                    {"name": "document_id", "label": "Invoice Number", "required": True},
                    {"name": "name", "label": "Customer / Entity Name", "required": True}
                ],
                "has_qr_code": True
            }
        },
        {
            "doc_type": "Other / Custom Document",
            "name": "General Identity / Official Document Template",
            "version": "v1.0",
            "issuing_org": "Configured Administrator Authority",
            "sample_path": None,
            "profile": {
                "document_type": "Other / Custom Document",
                "aspect_ratio": 1.414,
                "expected_width": 1000,
                "expected_height": 707,
                "required_sections": ["HEADER", "IDENTIFIER", "HOLDER_DETAILS"],
                "expected_fields": [
                    {"name": "document_id", "label": "Document Reference Number", "required": True},
                    {"name": "name", "label": "Bearer Name", "required": True}
                ],
                "has_qr_code": False
            }
        }
    ]

    for t in templates:
        existing = db.query(DocumentTemplate).filter(DocumentTemplate.document_type == t["doc_type"]).first()
        if not existing:
            tmpl = DocumentTemplate(
                document_type=t["doc_type"],
                template_name=t["name"],
                version=t["version"],
                issuing_org=t["issuing_org"],
                status="ACTIVE",
                is_default=True,
                aspect_ratio=t["profile"]["aspect_ratio"],
                expected_width=t["profile"]["expected_width"],
                expected_height=t["profile"]["expected_height"],
                sample_image_path=t["sample_path"],
                template_profile_json=json.dumps(t["profile"]),
                created_by="ADMIN"
            )
            db.add(tmpl)
    db.commit()

    # 4. Generate Pre-Cooked Demo Documents for Immediate 1-Click Testing
    # Doc A: Valid Aadhaar
    valid_aadhaar_path = os.path.join(DEMO_DIR, "demo_aadhaar_valid.png")
    generate_sample_aadhaar_image(
        valid_aadhaar_path,
        name="RAJESH KUMAR",
        uid="9876 5432 1012",
        dob="15/08/1988"
    )

    # Doc B: Tampered / Altered Aadhaar (Visible Name = "VIKRAM SINGH (TAMPERED)", but QR = "ORIGINAL HOLDER RAJESH")
    tampered_aadhaar_path = os.path.join(DEMO_DIR, "demo_aadhaar_altered.png")
    mismatched_qr_payload = json.dumps({
        "name": "ORIGINAL HOLDER RAJESH",
        "dob": "15/08/1988",
        "gender": "MALE",
        "document_id": "987654321012"
    })
    generate_sample_aadhaar_image(
        tampered_aadhaar_path,
        qr_text=mismatched_qr_payload,
        name="RAJESH KUMAR",
        uid="9876 5432 1012",
        dob="15/08/1988"
    )
    # Add a visual alteration (spliced patch over name with altered text)
    t_img = cv2.imread(tampered_aadhaar_path)
    if t_img is not None:
        cv2.rectangle(t_img, (295, 185), (665, 230), (225, 235, 252), -1)
        cv2.rectangle(t_img, (295, 185), (665, 230), (140, 160, 210), 2)
        cv2.putText(t_img, "VIKRAM SINGH (TAMPERED)", (300, 217), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (10, 10, 10), 2)
        cv2.imwrite(tampered_aadhaar_path, t_img)

    # Doc C: Valid PAN Card
    valid_pan_path = os.path.join(DEMO_DIR, "demo_pan_valid.png")
    generate_sample_pan_image(valid_pan_path, pan="ABCDE1234F", name="SURESH SHARMA")

    # Doc D: Blurry unreadable image
    blurry_doc_path = os.path.join(DEMO_DIR, "demo_blurry_unreadable.png")
    b_img = cv2.imread(valid_aadhaar_path)
    if b_img is not None:
        blurred = cv2.GaussianBlur(b_img, (45, 45), 0)
        cv2.imwrite(blurry_doc_path, blurred)

    # Seed initial sample verification history entries for rich dashboard charts
    existing_records = db.query(VerificationRecord).count()
    if existing_records == 0:
        base_time = datetime.utcnow() - timedelta(days=6)
        historical_samples = [
            {"type": "Aadhaar", "status": "LIKELY AUTHENTIC", "score": 96.0, "t_score": 98.0, "qr": 100.0, "officer": "Officer Priya Sharma"},
            {"type": "PAN Card", "status": "LIKELY AUTHENTIC", "score": 94.0, "t_score": 96.0, "qr": 100.0, "officer": "Officer Priya Sharma"},
            {"type": "Aadhaar", "status": "SUSPICIOUS / LIKELY ALTERED", "score": 48.0, "t_score": 52.0, "qr": 25.0, "officer": "Officer Priya Sharma"},
            {"type": "Driving Licence", "status": "LIKELY AUTHENTIC", "score": 91.0, "t_score": 93.0, "qr": 95.0, "officer": "Reviewer Arun Patel"},
            {"type": "Passport", "status": "LIKELY AUTHENTIC", "score": 95.0, "t_score": 97.0, "qr": 100.0, "officer": "Reviewer Arun Patel"},
            {"type": "Birth Certificate", "status": "UNABLE TO VERIFY", "score": 42.0, "t_score": 50.0, "qr": 0.0, "officer": "Officer Priya Sharma"},
            {"type": "Aadhaar", "status": "VERIFIED", "score": 98.0, "t_score": 99.0, "qr": 100.0, "officer": "Officer Priya Sharma"},
            {"type": "PAN Card", "status": "SUSPICIOUS / LIKELY ALTERED", "score": 54.0, "t_score": 60.0, "qr": 40.0, "officer": "Officer Priya Sharma"},
            {"type": "Aadhaar", "status": "LIKELY AUTHENTIC", "score": 93.0, "t_score": 95.0, "qr": 100.0, "officer": "Officer Priya Sharma"}
        ]
        for i, h_item in enumerate(historical_samples):
            rec = VerificationRecord(
                document_id=f"HIST-DOC-{1000 + i}",
                document_type=h_item["type"],
                officer_id="OFF-1042",
                officer_name=h_item["officer"],
                status=h_item["status"],
                screening_score=h_item["score"],
                template_match_score=h_item["t_score"],
                ocr_consistency_score=94.0,
                qr_consistency_score=h_item["qr"],
                required_fields_score=100.0 if h_item["score"] > 60 else 60.0,
                image_quality_score=95.0 if h_item["score"] > 60 else 40.0,
                integrity_score=92.0 if h_item["score"] > 60 else 45.0,
                authorized_verification_status="VERIFIED" if h_item["status"] == "VERIFIED" else "NOT AVAILABLE",
                breakdown_json=json.dumps({"template_match": h_item["t_score"], "ocr_consistency": 94.0, "qr_consistency": h_item["qr"]}),
                validation_notes_json=json.dumps(["Automated screening logged in verification registry."]),
                flagged_issues_json=json.dumps([]) if h_item["score"] > 70 else json.dumps([{"title": "Discrepancy detected", "severity": "HIGH", "description": "Flagged during screening."}]),
                manual_review_needed=h_item["status"] in ["SUSPICIOUS / LIKELY ALTERED", "UNABLE TO VERIFY"],
                created_at=base_time + timedelta(hours=i * 14)
            )
            db.add(rec)
        db.commit()

    print("Database seeding completed successfully.")
