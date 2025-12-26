# 🚀 Quick Start Guide

## ⚠️ Important: Python Version Requirement

**This project requires Python 3.8-3.13** (Python 3.11 or 3.12 recommended)

If you're using Python 3.14+, you may encounter compatibility issues. Please use Python 3.11 or 3.12.

Check your Python version:
```bash
python --version
```

## Installation (5 minutes)

### 0. Check Environment (Optional but Recommended)

```bash
python check_environment.py
```

This will verify your Python version and installed packages.

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

**Note**: This is a one-time setup. The model is ~50MB.

### 3. Run the Application

```bash
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## First Use

1. **Upload a Resume**: 
   - Click "Upload File" and select a PDF or TXT resume
   - OR paste your resume text directly

2. **Add Job Description**:
   - Paste the job description text
   - OR upload a TXT file with the job description

3. **Click "Match Resume"**:
   - Wait a few seconds for processing
   - Review your match score and skill gaps

## Example Workflow

```
1. Resume: "Software Engineer with 5 years Python experience..."
2. Job: "Looking for Python developer with ML experience..."
3. Result: 
   - Match Score: 75%
   - Missing Skills: machine learning, tensorflow
   - Matching Skills: python, software engineering
```

## Troubleshooting

### "spaCy model not found"
```bash
python -m spacy download en_core_web_sm
```

### "PDF reading failed"
Install PDF library:
```bash
pip install pdfplumber
```

### "Sentence transformers slow"
The model downloads on first use (~80MB). Be patient on first run.

## Next Steps

- Try different resumes and job descriptions
- Adjust scoring weights in the sidebar
- Review skill gap analysis to improve your resume
- Check the detailed breakdown for insights

---

**Happy Matching! 🎯**

