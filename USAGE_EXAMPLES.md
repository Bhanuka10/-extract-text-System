# 📖 Usage Examples & Commands

## 🚀 Quick Commands

### Run the System
```bash
python main.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

## 📋 Common Use Cases

### Use Case 1: Process New Batch of Resumes
```bash
# 1. Clear old resumes (optional)
Remove-Item resumes\* -Force

# 2. Add new resume files to resumes folder
# (Manually copy PDF, DOCX, or TXT files)

# 3. Run the parser
python main.py

# 4. Open the output
start HR_Candidate_Database.xlsx
```

### Use Case 2: Test with Sample Data
```bash
# Copy sample resumes
Copy-Item data\*.txt resumes\

# Run parser
python main.py

# View results
start HR_Candidate_Database.xlsx
```

### Use Case 3: Process Only PDF Files
```bash
# Copy only PDF files from a source folder
Copy-Item "C:\Downloads\Resumes\*.pdf" resumes\

# Run parser
python main.py
```

---

## ⚙️ Customization Examples

### Example 1: Add Custom Skills for Tech Roles
Edit `main.py` and modify the `TARGET_SKILLS` list:

```python
TARGET_SKILLS = [
    # Your custom tech skills
    "Python", "Java", "JavaScript", "TypeScript",
    "React", "Angular", "Vue.js", "Node.js",
    "AWS", "Azure", "Docker", "Kubernetes",
    "Machine Learning", "AI", "Data Science",
    "SQL", "MongoDB", "PostgreSQL",
    # ... add more
]
```

### Example 2: Add Custom Skills for Marketing Roles
```python
TARGET_SKILLS = [
    "Digital Marketing", "SEO", "SEM", "Content Marketing",
    "Social Media Marketing", "Email Marketing", "PPC",
    "Google Analytics", "Google Ads", "Facebook Ads",
    "HubSpot", "Mailchimp", "WordPress",
    "Brand Management", "Campaign Management",
    # ... add more
]
```

### Example 3: Change Output Filename
Edit `main.py`, find the `main()` function:

```python
def main():
    input_folder = "resumes"
    output_file = "Candidates_2026_Q1.xlsx"  # Custom name
    # ... rest of code
```

---

## 🔍 Interpreting Results

### Output Excel Columns Explained

| Column | Description | Example |
|--------|-------------|---------|
| **Name** | Extracted candidate name | "John Michael Smith" |
| **Email** | Primary email address | "john.smith@email.com" |
| **Phone** | Contact number | "+1-555-123-4567" |
| **Skills_Count** | Number of matching skills | 15 |
| **Skills** | Comma-separated skill list | "Python, Java, React..." |
| **Education** | Degrees found | "Bachelor, Master" |
| **Experience_Years** | Years of experience | 5 |
| **Relevance_Score** | Candidate score (0-100) | 95 |
| **Filename** | Original resume file | "candidate1.pdf" |

### Score Interpretation

- **90-100**: Excellent match - High priority candidate
- **75-89**: Good match - Strong candidate
- **60-74**: Moderate match - Review carefully
- **Below 60**: Weak match - May not meet requirements

---

## 🛠️ Troubleshooting Commands

### Check Python Version
```bash
python --version
# Should be 3.8 or higher
```

### Check Installed Packages
```bash
pip list
# Look for: pandas, spacy, PyPDF2, python-docx, openpyxl
```

### Verify spaCy Model
```bash
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('Model loaded successfully')"
```

### Test File Reading
```bash
# Test PDF reading
python -c "import PyPDF2; print('PyPDF2 working')"

# Test Word reading
python -c "from docx import Document; print('python-docx working')"

# Test Excel writing
python -c "import openpyxl; print('openpyxl working')"
```

### Reinstall Dependencies
```bash
pip uninstall pandas openpyxl PyPDF2 python-docx spacy -y
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

## 📊 Batch Processing Examples

### Process 100+ Resumes
```bash
# 1. Organize resumes in folders by role
resumes/
  ├── developers/
  ├── marketers/
  └── hr_professionals/

# 2. Process each category separately
# Copy developers to resumes folder
Copy-Item "resumes\developers\*" resumes\
python main.py
Move-Item HR_Candidate_Database.xlsx Developers_Database.xlsx

# Repeat for other categories
```

### Archive Processed Resumes
```bash
# After processing, move resumes to archive
$date = Get-Date -Format "yyyy-MM-dd"
New-Item -ItemType Directory -Path "archive\$date" -Force
Move-Item resumes\* "archive\$date\"
```

---

## 🔧 Advanced Usage

### Modify Scoring Algorithm
Edit the `calculate_candidate_score()` function in `main.py`:

```python
def calculate_candidate_score(details):
    score = 0
    
    # Customize weights:
    # Skills: 50 points instead of 40
    skills_count = len([s for s in details.get('Skills', '').split(', ') if s])
    score += min(50, skills_count * 5)  # Changed from 4 to 5
    
    # Experience: 25 points instead of 30
    experience = details.get('Experience_Years', 0)
    score += min(25, experience * 2.5)  # Changed
    
    # ... modify as needed
    
    return min(100, score)
```

### Add Custom Data Fields
Modify `extract_details()` to add more fields:

```python
def extract_details(text):
    # ... existing code ...
    
    # Add LinkedIn URL extraction
    linkedin_pattern = r'linkedin\.com/in/[\w\-]+'
    linkedin = re.findall(linkedin_pattern, text, re.IGNORECASE)
    
    details = {
        # ... existing fields ...
        "LinkedIn": linkedin[0] if linkedin else "Not Found",
        # Add more custom fields
    }
    
    return details
```

---

## 📝 Integration Examples

### Export to CSV Instead of Excel
Add this to `main.py`:

```python
# In main() function, after creating DataFrame:
df.to_csv("candidates.csv", index=False)
```

### Export to JSON
```python
# In main() function:
df.to_json("candidates.json", orient="records", indent=2)
```

### Email Results Automatically
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def send_email_with_attachment():
    # Configure your email settings
    sender = "your-email@gmail.com"
    receiver = "hr-team@company.com"
    subject = "Candidate Database Updated"
    
    # Create email (simplified example)
    # ... add email sending code ...
```

---

## 🎯 Performance Tips

### Speed Up Processing
1. Use SSD for resume storage
2. Process in batches of 50-100
3. Use text files when possible (faster than PDF)

### Improve Accuracy
1. Request standardized resume formats
2. Update TARGET_SKILLS regularly
3. Review and refine extraction patterns
4. Add domain-specific keywords

---

## 📈 Analytics Examples

### Generate Statistics Report
```python
# Add to main() function after creating DataFrame:
print("\n📊 DETAILED ANALYTICS:")
print(f"   Skills Distribution:")
for skill in TARGET_SKILLS[:10]:  # Top 10 skills
    count = df['Skills'].str.contains(skill, case=False).sum()
    if count > 0:
        print(f"      {skill}: {count} candidates")
```

---

## 💡 Pro Tips

1. **Regularly Update Skills List**: Review job postings monthly
2. **Maintain Resume Archive**: Keep processed resumes organized
3. **Backup Excel Files**: Save dated versions
4. **Customize for Each Role**: Use different skill sets per position
5. **Quality Control**: Randomly review 5-10 extractions
6. **Train HR Team**: Ensure team understands scoring system

---

For more information, see [README.md](README.md)

**Last Updated**: January 2026
