
# 🇳🇵 SarkaarSathi — Nepal's AI Government Assistant

> AI-powered legal assistant that helps Nepali citizens understand their rights, navigate government services, and generate official complaint letters in Nepali language.

---

## 🔥 What is SarkaarSathi?

SarkaarSathi is a Multi-Agent RAG system built specifically for Nepal. Most Nepali citizens don't know their legal rights, miss out on government benefits, and waste days in government office queues. SarkaarSathi solves this by combining 4 AI agents with a RAG knowledge base of official Nepal government documents — giving every citizen instant access to legal guidance in Nepali or English, for free.

---

## 🤖 How It Works

4-agent pipeline:

- **Agent 1 — Validator**: Classifies input as VALID, EMOTIONAL, NONSENSE, MEDICAL, or OTHER
- **Agent 2 — Router**: Classifies problem into LABOUR, CITIZENSHIP, LAND, CONSUMER, or RIGHTS
- **Agent 3 — Specialist (RAG)**: Searches ChromaDB vector DB → analyzes laws → case strength
- **Agent 4 — Letter Generator**: Drafts official complaint letter in Nepali with Bikram Sambat date

---

## 🏗️ Architecture
User Input (Nepali/English)
↓
Validation Agent — rejects nonsense/emotional/medical
↓
Router Agent — LABOUR / CITIZENSHIP / LAND / CONSUMER / RIGHTS
↓
Specialist Agent — ChromaDB RAG → law analysis → case strength
↓
Letter Generator — official Nepali complaint letter
↓
User edits → downloads PDF

---

## ✨ Features

- 🤖 4 AI agents in orchestrated pipeline
- 📚 RAG grounded in 608 pages of official Nepal law
- 🇳🇵 Full Nepali language support (Devanagari script)
- ⚖️ Legal case strength analysis (Strong / Medium / Weak)
- 📋 Step-by-step action plan for each problem
- ✉️ Auto-generated official complaint letter in Nepali
- 📄 Download complaint letter as PDF with proper Nepali font
- ✏️ Editable letter before downloading
- 📅 Correct Bikram Sambat (BS) date in letters
- 🛡️ Smart input validation
- 📌 Exact source citations with document name and page number

---

## 📚 RAG Knowledge Base

| Document | Language |
|---|---|
| Constitution of Nepal 2072 | English |
| Constitution of Nepal 2072 | Nepali |
| Labour Act 2074 | English |
| Labour Act 2074 | Nepali |
| Citizenship Act 2063 | Nepali |

Total: 608 pages of searchable Nepal law

---

## 💡 Example Queries

- "My employer hasn't paid my salary for 3 months"
- "Police kept me in jail for 5 days without charges"
- "My landlord won't return my deposit of Rs 50,000"
- "I bought a phone for Rs 45,000 but it stopped working after 2 days"
- "मेरो जग्गा छिमेकीले मिचेको छ"
- "मेरो कम्पनीले बिना कारण तलब काटेको छ"

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| AI Agent Brain | Groq API + LLaMA 3.3 70B |
| Vector Database | ChromaDB |
| Embeddings | all-MiniLM-L6-v2 |
| Frontend | Streamlit |
| PDF Generation | ReportLab |
| PDF Parsing | PyPDF2 |
| Nepali Date | nepali library |
| Language | Python 3.12 |

---

## 📁 Project Structure
SarkaarSathi/
├── app.py                  # Main app — all 4 agents
├── ingest.py               # PDF ingestion and RAG setup
├── Mukta-Regular.ttf       # Nepali font for PDF generation
├── docs/                   # Nepal law PDF documents
│   ├── Constitution-of-Nepal_2072_Eng.pdf
│   ├── Constitution-of-Nepal_2072_Nepali.pdf
│   ├── The-Labor-Act-2017-2074.pdf
│   ├── Labour-Act-Nepali.pdf
│   └── Citizenship-Act-2063.pdf
├── db/                     # ChromaDB vector database (auto-generated)
├── requirements.txt
├── .env                    # API keys (not committed)
└── README.md

---

## 🚀 Getting Started

**1. Clone the repo**
```bash
git clone https://github.com/Dipendra367/SarkaarSathi.git
cd SarkaarSathi
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your Groq API key**

Create a `.env` file:
GROQ_API_KEY=your-groq-api-key-here
Get your free key at: https://console.groq.com

**4. Add Nepal law PDFs to docs/ folder**

**5. Ingest documents**
```bash
python ingest.py
```

**6. Run the app**
```bash
streamlit run app.py
```

---

## 🌍 Impact

- 30 million Nepali citizens who struggle with government services
- Rural citizens who can't afford lawyers
- Workers who don't know their Labour Act rights
- Anyone who has wasted a day in a government office queue

---

## 👨‍💻 Built By

**Dipendra Thapa**
Final-year Software Engineering Student
Pokhara University, Gandaki Pradesh, Nepal
GitHub: github.com/Dipendra367

---

## ⚠️ Disclaimer

SarkaarSathi provides AI-generated legal guidance based on official Nepal government documents. This is not a substitute for professional legal advice. For serious legal matters, please consult a qualified lawyer.

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 📸 Screenshots

### 🏠 Home — Input Your Problem
<img width="1920" height="940" alt="Screenshot from 2026-05-24 23-26-24" src="https://github.com/user-attachments/assets/abf7f31c-7463-4d41-bb2a-7dec68766f63" />


### ⚖️ Legal Analysis — Case Strength + Action Steps
<img width="1920" height="940" alt="Screenshot from 2026-05-24 23-28-30" src="https://github.com/user-attachments/assets/efa008f0-7e83-46d2-b20c-49b23b921b8b" />


### ✉️ Official Complaint Letter in Nepali
<img width="1920" height="940" alt="Screenshot from 2026-05-24 23-28-42" src="https://github.com/user-attachments/assets/d1ca8b97-5b52-4c3b-8da2-af60f39aebd3" />

