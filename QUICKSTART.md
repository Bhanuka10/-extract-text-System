# Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1️⃣ Install Dependencies
```bash
pip install pandas openpyxl PyPDF2 python-docx spacy
python -m spacy download en_core_web_sm
```

### 2️⃣ Add Your Resumes
Place resume files (PDF, DOCX, or TXT) in the `resumes/` folder

### 3️⃣ Run the Parser
```bash
python main.py
```

## 📊 View Results
Open `HR_Candidate_Database.xlsx` to see:
- Extracted candidate information
- Skills matched
- Relevance scores
- Sorted by best matches

## 🧪 Test with Sample Data
```bash
# Windows PowerShell
Copy-Item data\*.txt resumes\

# Then run
python main.py
```

## ⚙️ Customize Skills
Edit `TARGET_SKILLS` in `main.py` to match your job requirements.

---
**Need Help?** Check the full [README.md](README.md) for detailed documentation.
