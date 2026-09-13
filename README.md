# AI-Based Fake Identity & Document Screening System

Demo/authorized screening starter application based on the supplied specification.

## Stack
- React + TypeScript + Vite
- FastAPI + Python
- OpenCV
- Tesseract OCR
- PostgreSQL-ready configuration

## Run backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Tesseract must also be installed on the operating system.

## Run frontend
```bash
cd frontend
npm install
npm run dev
```

This project is a screening/demo system. It must not claim legal authenticity from template matching alone.
