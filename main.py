import os
import re
import pandas as pd
import spacy
import PyPDF2
from docx import Document # Library for Word Docs

# Load the "Brain" (Pre-trained NLP model)
nlp = spacy.load("en_core_web_sm")

# --- CONFIGURATION: SKILLS TO LOOK FOR ---
# Based on your Job Descriptions
TARGET_SKILLS = [
    "Recruitment", "Labor Laws", "Employee Relations", # HR
    "Digital Marketing", "SEO", "Google Analytics", "Campaigns", # Marketing
    "Invoicing", "Taxation", "Audit", "Financial Reporting", "Excel" # Accounts
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

def extract_details(text):
    """
    Finds Email, Phone, and Skills.
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
            
    # 4. Name Extraction (Using Spacy NLP)
    doc = nlp(text)
    name = "Unknown"
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text
            break # Assume the first person mentioned is the candidate
            
    return {
        "Name": name,
        "Email": email[0] if email else None,
        "Phone": phone[0] if phone else None,
        "Skills": ", ".join(found_skills),
        "Raw_Text": text[:100] + "..." # Preview of text
    }

def main():
    # FOLDER SETUP
    input_folder = "resumes" # Put all PDFs, DOCXs, TXTs here
    output_file = "HR_Candidate_Database.xlsx"
    
    data_list = []
    
    print("--- Starting Resume Parser ---")
    
    for filename in os.listdir(input_folder):
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
            print(f"Processed: {filename}")
            
    # C. SAVE TO EXCEL
    if data_list:
        df = pd.DataFrame(data_list)
        # Reorder columns to look professional
        df = df[["Name", "Email", "Phone", "Skills", "Filename"]]
        df.to_excel(output_file, index=False)
        print(f"\nSuccess! Data saved to '{output_file}'")
    else:
        print("No resumes found or processed.")

if __name__ == "__main__":
    main()