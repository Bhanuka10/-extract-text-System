import os
import re
import pandas as pd
import spacy
import PyPDF2
from docx import Document
from datetime import datetime
from pathlib import Path

# Load the "Brain" (Pre-trained NLP model)
try:
    nlp = spacy.load("en_core_web_sm")
except:
    print("Error: Spacy model not found. Please run: python -m spacy download en_core_web_sm")
    exit(1)

# --- CONFIGURATION: SKILLS TO LOOK FOR ---
# Based on your Job Descriptions
TARGET_SKILLS = [
    # Technical Skills
    "Python", "Java", "JavaScript", "C++", "C#", "SQL", "React", "Angular", "Node.js",
    "Django", "Flask", "Spring", "AWS", "Azure", "Docker", "Kubernetes", "Git",
    # HR Skills
    "Recruitment", "Labor Laws", "Employee Relations", "HRMS", "Talent Acquisition",
    "Performance Management", "Onboarding", "HR Analytics",
    # Marketing Skills
    "Digital Marketing", "SEO", "SEM", "Google Analytics", "Campaigns", "Social Media",
    "Content Marketing", "Email Marketing", "PPC", "Brand Management",
    # Finance/Accounting Skills
    "Invoicing", "Taxation", "Audit", "Financial Reporting", "Excel", "QuickBooks",
    "SAP", "Budgeting", "Forecasting", "GAAP", "Financial Analysis",
    # Soft Skills
    "Leadership", "Communication", "Team Management", "Problem Solving", "Project Management"
]

# Education keywords
EDUCATION_KEYWORDS = [
    "Bachelor", "Master", "PhD", "B.Tech", "M.Tech", "MBA", "BBA", "B.Sc", "M.Sc",
    "B.A", "M.A", "B.Com", "M.Com", "Engineering", "Computer Science", "Business Administration",
    "Finance", "Marketing", "Human Resources", "Diploma", "Certificate"
]

def extract_text_from_pdf(filepath):
    """Reads PDF files"""
    text = ""
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF {filepath}: {e}")
    return text

def extract_text_from_docx(filepath):
    """Reads Word (.docx) files"""
    text = ""
    try:
        doc = Document(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX {filepath}: {e}")
    return text

def extract_text_from_txt(filepath):
    """Reads simple Text (.txt) files"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading TXT {filepath}: {e}")
        return ""

def clean_text(text):
    """Removes extra spaces and newlines for easier processing"""
    return " ".join(text.split())

def extract_education(text):
    """Extract education information from resume text"""
    education_list = []
    text_lower = text.lower()
    
    for edu in EDUCATION_KEYWORDS:
        if edu.lower() in text_lower:
            education_list.append(edu)
    
    return ", ".join(list(set(education_list))) if education_list else "Not Found"

def extract_experience_years(text):
    """Extract years of experience from resume"""
    # Pattern for "X years of experience" or "X+ years"
    patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
        r'(?:experience|exp)\s*(?:of\s*)?(\d+)\+?\s*(?:years?|yrs?)',
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:in|of)',
    ]
    
    text_lower = text.lower()
    years = []
    
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        years.extend([int(m) for m in matches])
    
    # Also try to calculate from dates (e.g., 2018-2021)
    date_pattern = r'(\d{4})\s*[-–—]\s*(\d{4}|present|current)'
    date_matches = re.findall(date_pattern, text_lower, re.IGNORECASE)
    
    if date_matches:
        total_years = 0
        current_year = datetime.now().year
        for start, end in date_matches:
            start_year = int(start)
            end_year = current_year if end.lower() in ['present', 'current'] else int(end)
            total_years += max(0, end_year - start_year)
        if total_years > 0:
            years.append(total_years)
    
    return max(years) if years else 0

def extract_name_improved(text):
    """Improved name extraction using multiple strategies"""
    doc = nlp(text[:1000])  # Check first 1000 chars where name usually appears
    
    # Strategy 1: Look for PERSON entities
    person_names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    
    if person_names:
        # Return the first person name that looks like a full name (2-4 words)
        for name in person_names:
            word_count = len(name.split())
            if 2 <= word_count <= 4:
                return name
        return person_names[0]  # Fallback to first person found
    
    # Strategy 2: Look for "Name:" pattern
    name_pattern = r'(?:Name|Full Name|Candidate Name)\s*[:\-]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
    match = re.search(name_pattern, text[:500], re.IGNORECASE)
    if match:
        return match.group(1)
    
    return "Unknown"

def calculate_candidate_score(details):
    """Calculate a relevance score for the candidate (0-100)"""
    score = 0
    
    # Skills matching (40 points max)
    skills_list = details.get('Skills', '').split(', ')
    skills_count = len([s for s in skills_list if s])
    score += min(40, skills_count * 4)
    
    # Experience (30 points max)
    experience = details.get('Experience_Years', 0)
    if experience > 0:
        score += min(30, experience * 3)
    
    # Education (20 points max)
    education = details.get('Education', '')
    if 'PhD' in education or 'Master' in education:
        score += 20
    elif 'Bachelor' in education or 'B.Tech' in education or 'B.Sc' in education:
        score += 15
    elif education != "Not Found":
        score += 10
    
    # Contact info completeness (10 points)
    if details.get('Email'):
        score += 5
    if details.get('Phone'):
        score += 5
    
    return min(100, score)

def extract_details(text):
    """
    Comprehensive extraction of candidate information.
    """
    # 1. Email Extraction (Regex)
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email = re.findall(email_pattern, text)
    
    # 2. Phone Extraction (Broad Regex for various formats)
    phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
    phone = re.findall(phone_pattern, text)
    
    # 3. Skills Extraction (Keyword Matching)
    found_skills = []
    text_lower = text.lower()
    for skill in TARGET_SKILLS:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    # Remove duplicates while preserving order
    found_skills = list(dict.fromkeys(found_skills))
            
    # 4. Name Extraction (Improved)
    name = extract_name_improved(text)
    
    # 5. Education Extraction
    education = extract_education(text)
    
    # 6. Experience Extraction
    experience_years = extract_experience_years(text)
    
    # 7. Build details dictionary
    details = {
        "Name": name,
        "Email": email[0] if email else "Not Found",
        "Phone": phone[0] if phone else "Not Found",
        "Skills": ", ".join(found_skills) if found_skills else "Not Found",
        "Skills_Count": len(found_skills),
        "Education": education,
        "Experience_Years": experience_years,
    }
    
    # 8. Calculate candidate score
    details["Relevance_Score"] = calculate_candidate_score(details)
    
    return details

def create_detailed_field_data(details, filename):
    """
    Create detailed rows with field identification for each piece of information.
    """
    detailed_data = []
    name = details.get("Name", "Unknown")
    
    # Add row for each field
    detailed_data.append({
        "Candidate_Name": name,
        "Field": "Name",
        "Value": details.get("Name", "Not Found"),
        "Filename": filename
    })
    
    detailed_data.append({
        "Candidate_Name": name,
        "Field": "Email",
        "Value": details.get("Email", "Not Found"),
        "Filename": filename
    })
    
    detailed_data.append({
        "Candidate_Name": name,
        "Field": "Phone",
        "Value": details.get("Phone", "Not Found"),
        "Filename": filename
    })
    
    detailed_data.append({
        "Candidate_Name": name,
        "Field": "Skills",
        "Value": details.get("Skills", "Not Found"),
        "Filename": filename
    })
    
    detailed_data.append({
        "Candidate_Name": name,
        "Field": "Skills_Count",
        "Value": str(details.get("Skills_Count", 0)),
        "Filename": filename
    })
    
    detailed_data.append({
        "Candidate_Name": name,
        "Field": "Education",
        "Value": details.get("Education", "Not Found"),
        "Filename": filename
    })
    
    detailed_data.append({
        "Candidate_Name": name,
        "Field": "Experience_Years",
        "Value": str(details.get("Experience_Years", 0)),
        "Filename": filename
    })
    
    detailed_data.append({
        "Candidate_Name": name,
        "Field": "Relevance_Score",
        "Value": str(details.get("Relevance_Score", 0)),
        "Filename": filename
    })
    
    return detailed_data

def main():
    # FOLDER SETUP
    input_folder = "resumes" # Put all PDFs, DOCXs, TXTs here
    output_file = "HR_Candidate_Database.xlsx"
    
    # Create resumes folder if it doesn't exist
    Path(input_folder).mkdir(exist_ok=True)
    
    data_list = []
    detailed_data_list = []
    
    print("="*60)
    print("  AUTOMATED RESUME PARSING & CANDIDATE SCREENING SYSTEM")
    print("="*60)
    print(f"\nScanning folder: {input_folder}")
    print(f"Looking for: PDF, DOCX, TXT files\n")
    
    # Check if folder has files
    files = [f for f in os.listdir(input_folder) if f.endswith(('.pdf', '.docx', '.txt'))]
    if not files:
        print(f"⚠️  No resume files found in '{input_folder}' folder.")
        print("   Please add PDF, DOCX, or TXT files and run again.")
        return
    
    print(f"Found {len(files)} resume file(s). Processing...\n")
    
    for filename in files:
        filepath = os.path.join(input_folder, filename)
        
        # A. DETECT FILE TYPE & READ
        raw_text = ""
        if filename.endswith(".pdf"):
            raw_text = extract_text_from_pdf(filepath)
        elif filename.endswith(".docx"):
            raw_text = extract_text_from_docx(filepath)
        elif filename.endswith(".txt"):
            raw_text = extract_text_from_txt(filepath)
        else:
            continue # Skip files that aren't resumes
            
        # B. CLEAN & EXTRACT
        if raw_text:
            cleaned_text = clean_text(raw_text)
            details = extract_details(cleaned_text)
            details["Filename"] = filename # Add filename for reference
            data_list.append(details)
            
            # Create detailed field data
            field_data = create_detailed_field_data(details, filename)
            detailed_data_list.extend(field_data)
            
            print(f"✓ Processed: {filename} (Score: {details['Relevance_Score']}%)")
        else:
            print(f"✗ Failed to extract text from: {filename}")
            
    # C. SAVE TO EXCEL
    if data_list:
        # Create summary dataframe
        df_summary = pd.DataFrame(data_list)
        
        # Sort by relevance score (highest first)
        df_summary = df_summary.sort_values('Relevance_Score', ascending=False)
        
        # Reorder columns to look professional
        df_summary = df_summary[["Name", "Email", "Phone", "Skills_Count", "Skills", "Education", 
                 "Experience_Years", "Relevance_Score", "Filename"]]
        
        # Create detailed dataframe with Field column
        df_detailed = pd.DataFrame(detailed_data_list)
        
        # Save to Excel with multiple sheets
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df_summary.to_excel(writer, sheet_name="Summary", index=False)
            df_detailed.to_excel(writer, sheet_name="Detailed_Fields", index=False)
        
        print("\n" + "="*60)
        print(f"✓ SUCCESS! Processed {len(data_list)} resume(s)")
        print(f"✓ Data saved to: {output_file}")
        print(f"✓ Created 2 sheets: Summary & Detailed_Fields")
        print("="*60)
        
        # Print summary statistics
        print("\n📊 SUMMARY STATISTICS:")
        print(f"   • Average Relevance Score: {df_summary['Relevance_Score'].mean():.1f}%")
        print(f"   • Top Candidate: {df_summary.iloc[0]['Name']} ({df_summary.iloc[0]['Relevance_Score']}%)")
        print(f"   • Total Skills Found: {df_summary['Skills_Count'].sum()}")
        print(f"   • Avg Experience: {df_summary['Experience_Years'].mean():.1f} years")
    else:
        print("\n⚠️  No resumes were successfully processed.")

if __name__ == "__main__":
    main()