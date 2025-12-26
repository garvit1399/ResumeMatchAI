# 📌 AI-Powered Resume & Job Matching System

## 🔍 Overview

This project is an AI-driven system that evaluates how well a resume matches a given job description using Natural Language Processing and semantic similarity, rather than traditional keyword matching.

It generates:
- **A match score** (0-100%) with explainable breakdowns
- **Skill gap analysis** (missing vs. present skills)
- **Skill confidence levels** (Strong/Moderate/Weak)
- **ATS optimization recommendations**
- **Resume rewrite suggestions** with before/after comparisons
- **Multi-job comparison** rankings
- **Actionable feedback** to improve resume alignment

### Example Output

```
🎯 Match Score: 75.3%
✅ Skill Coverage: 68.5%

Top Strengths:
✓ Strong skills match (82.1%)
✓ Good experience alignment (71.2%)

Top Weaknesses:
⚠️ Experience section reduces score by 12.3%
⚠️ Missing critical skills: SQL, REST APIs

Skill Confidence:
✅ Strong: Python, JavaScript, React
⚡ Moderate: Docker, AWS
⚠️ Weak: Kubernetes (mentioned once)

ATS Score: 85% - Good compatibility
Recommendations:
1. Add missing section: Certifications
2. Increase keyword frequency for: Machine Learning
```

## 🚀 Features

### Core Features
- ✅ **Semantic resume–job matching** using sentence embeddings
- ✅ **Skill extraction** using NLP techniques
- ✅ **Weighted scoring** across skills, experience, education, and tools
- ✅ **Clear identification** of missing or weak skills
- ✅ **Interactive web interface** built with Streamlit

### Advanced Features (NEW! 🎉)
- 🔍 **Explainable AI (XAI)** - Transparent scoring with detailed breakdowns showing why the score is what it is
- 💪 **Skill Confidence Scoring** - Analyzes skill strength (Strong/Moderate/Weak) based on context, verbs, and frequency
- 📈 **Multi-Job Comparison** - Compare one resume against multiple job descriptions simultaneously with ranked recommendations
- ✍️ **Resume Rewrite Suggestions** - AI-powered improvements to bullet points with stronger action verbs and keyword integration
- 📝 **ATS Optimization Mode** - Detects ATS-unfriendly formatting and provides actionable recommendations
- 📊 **Section Impact Analysis** - Shows how each section (skills, experience, education, tools) contributes to the final score
- 💡 **Resume Highlights** - Identifies which resume sections helped or hurt the match score

## 🧠 Technologies Used

- **Language**: Python 3.8+
- **NLP**: spaCy, Sentence Transformers
- **ML**: Cosine similarity, embeddings
- **Frontend**: Streamlit
- **Libraries**: scikit-learn, pandas, numpy

## 🏗️ System Architecture

```
Resume & Job Description
        ↓
Text Preprocessing (NLP)
        ↓
Skill & Entity Extraction
        ↓
Semantic Embedding Generation
        ↓
Similarity Scoring Engine
        ↓
┌─────────────────────────────────────┐
│   Advanced Analysis Modules         │
├─────────────────────────────────────┤
│ • Explainable AI Analysis          │
│ • Skill Confidence Scoring          │
│ • ATS Optimization                  │
│ • Resume Rewrite Engine             │
│ • Multi-Job Comparison              │
└─────────────────────────────────────┘
        ↓
Comprehensive Match Results + Insights
```

## 📊 Matching Methodology

1. **Semantic Embeddings**: Uses Sentence-BERT embeddings (`all-MiniLM-L6-v2`) to capture contextual meaning
2. **Cosine Similarity**: Computes semantic similarity between resume and job description vectors
3. **Weighted Scoring**: Applies weighted scoring across resume sections:
   - Skills: 40%
   - Experience: 30%
   - Education: 15%
   - Tools: 15%
4. **Skill Gap Analysis**: Identifies missing skills by comparing extracted entities

## ⚖️ Ethical Considerations

- ✅ No use of demographic or personal attributes
- ✅ Bias-aware normalization across resume formats
- ✅ Transparent and explainable scoring logic

## 🧪 Evaluation

- Compared semantic matching against keyword-based baseline
- Manual relevance validation
- Skill extraction precision testing

## 🛠️ Installation

### Prerequisites

- **Python 3.8+** (Recommended: Python 3.11 or 3.12)
  - ⚠️ **Note**: Python 3.14+ has compatibility issues with spaCy, but the app includes a fallback preprocessing mode that works without spaCy
- pip package manager

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd ResumeMatchAI
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Download spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

**Note**: The sentence-transformers model (`all-MiniLM-L6-v2`) will be automatically downloaded on first use.

## 🚀 How to Run

### Start the Application

```bash
python -m streamlit run app.py
```

**Note**: On Windows, use `python -m streamlit` instead of just `streamlit`.

The application will open in your default web browser at `http://localhost:8501`

### Application Interface

The app features a **tabbed interface** with 6 comprehensive views:

1. **📊 Main Results Tab**
   - Overall match score and similarity metrics
   - Section-wise score breakdown
   - Skill gap analysis (matching vs. missing skills)
   - Detailed breakdown and recommendations

2. **🔍 Explainable AI Tab**
   - Top 5 reasons for low score (if applicable)
   - Section impact analysis (how each section contributes)
   - Top strengths and weaknesses
   - Resume highlights (helpful vs. hurtful sections)

3. **💪 Skill Confidence Tab**
   - Skill strength summary (Strong/Moderate/Weak counts)
   - Detailed confidence analysis for each skill
   - Based on mentions, action verbs, and experience indicators

4. **📝 ATS Optimization Tab**
   - ATS compatibility score (0-100%)
   - Issues found (missing sections, formatting problems)
   - Prioritized recommendations
   - Keyword placement analysis

5. **✍️ Resume Rewrites Tab**
   - AI-powered bullet point improvement suggestions
   - Before/after comparisons
   - Action verb replacements
   - Keyword integration suggestions

6. **📈 Multi-Job Compare Tab**
   - Compare one resume against multiple jobs
   - Ranked job list with scores
   - Best-fit job recommendations
   - Comparison statistics

### Usage

1. **Upload your resume** (PDF or TXT format)
   - Or paste the resume text directly
2. **Upload or paste the job description** (TXT format or paste text)
3. Click **"Match Resume"** to analyze
4. **Explore results** using the 6 tabs:
   - **📊 Main Results** - Core matching results and skill gaps
   - **🔍 Explainable AI** - Why the score is what it is (section breakdowns, top reasons)
   - **💪 Skill Confidence** - Strength analysis of your skills (Strong/Moderate/Weak)
   - **📝 ATS Optimization** - ATS compatibility score and recommendations
   - **✍️ Resume Rewrites** - AI-powered improvement suggestions
   - **📈 Multi-Job Compare** - Compare against multiple jobs at once
5. Use the sidebar to adjust scoring weights if needed

## 📁 Project Structure

```
ResumeMatchAI/
│
├── data/
│   ├── resumes/          # Sample resumes (optional)
│   └── job_descriptions/ # Sample job descriptions (optional)
│
├── src/
│   ├── parser.py              # Text extraction from PDF/TXT
│   ├── preprocess.py          # NLP preprocessing (tokenization, lemmatization)
│   ├── skill_gap.py           # Skill extraction and gap analysis
│   ├── embeddings.py          # Semantic embedding generation
│   ├── matcher.py             # Main matching engine
│   ├── explainable.py         # Explainable AI analysis
│   ├── skill_confidence.py    # Skill confidence scoring
│   ├── ats_optimizer.py        # ATS optimization analysis
│   ├── resume_rewriter.py     # Resume rewrite suggestions
│   └── multi_job_comparison.py # Multi-job comparison engine
│
├── app.py                # Streamlit frontend application
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔧 Module Details

### `parser.py`
- Extracts text from PDF files using `pdfplumber` or `PyMuPDF`
- Handles text files (.txt)
- Returns clean raw text

### `preprocess.py`
- Tokenization and lemmatization using spaCy (with fallback for Python 3.14+)
- Stopword removal
- Text normalization
- **Fallback mode**: Basic preprocessing when spaCy is unavailable (Python 3.14+ compatibility)

### `skill_gap.py`
- Extracts technical skills, tools, education keywords
- Compares resume vs. job description entities
- Identifies missing skills and tools

### `embeddings.py`
- Generates semantic embeddings using Sentence Transformers
- Converts text to high-dimensional vectors
- Supports batch processing

### `matcher.py`
- Main matching engine combining all components
- Computes cosine similarity scores
- Applies weighted scoring across sections
- Returns comprehensive matching results with all advanced features

### `explainable.py` ⭐ NEW
- Provides explainable AI analysis
- Breaks down section-wise contributions to final score
- Identifies top strengths and weaknesses
- Highlights resume sections that helped or hurt the score
- Generates "Top 5 reasons for low score" insights

### `skill_confidence.py` ⭐ NEW
- Analyzes skill strength (Strong/Moderate/Weak)
- Based on mentions, action verbs, and experience indicators
- Provides detailed confidence analysis for each skill
- Categorizes skills beyond binary presence detection

### `ats_optimizer.py` ⭐ NEW
- Analyzes ATS (Applicant Tracking System) compatibility
- Detects missing standard section headers
- Evaluates keyword placement and frequency
- Provides prioritized recommendations for ATS optimization
- Calculates ATS compatibility score (0-100%)

### `resume_rewriter.py` ⭐ NEW
- Suggests improvements to resume bullet points
- Replaces weak action verbs with stronger alternatives
- Incorporates missing job-relevant keywords
- Provides before/after comparisons with explanations

### `multi_job_comparison.py` ⭐ NEW
- Compares one resume against multiple job descriptions
- Ranks jobs by match score
- Provides best-fit job recommendations
- Generates comparison statistics and summaries

## 📈 Future Enhancements

- [x] ✅ ATS-friendly resume suggestions (Implemented!)
- [x] ✅ Multi-job comparison dashboard (Implemented!)
- [x] ✅ Resume optimization suggestions (Implemented!)
- [x] ✅ Explainable AI scoring (Implemented!)
- [ ] Career path recommendations
- [ ] Integration with job boards (LinkedIn, Indeed)
- [ ] Role-specific scoring models
- [ ] Historical matching trends
- [ ] Bias & Fairness Analyzer
- [ ] Recruiter View Mode
- [ ] Resume Version Testing (A/B Testing)

## 🐛 Troubleshooting

### Issue: Python 3.14+ Compatibility Warning
If you see warnings about Python 3.14+ and spaCy:

**Problem**: You're using Python 3.14+ which has compatibility issues with spaCy/Pydantic v1.

**Solution**: 
1. **The app will automatically use fallback preprocessing** - it will still work, but with basic tokenization instead of advanced NLP
2. **For best results**: Use Python 3.11 or 3.12 (recommended)
   ```bash
   # Using pyenv (if installed)
   pyenv install 3.12.0
   pyenv local 3.12.0
   
   # Or using conda
   conda create -n resumematcher python=3.12
   conda activate resumematcher
   ```
3. The fallback mode uses basic tokenization and stopword removal, which is sufficient for most use cases

### Issue: spaCy model not found
```bash
python -m spacy download en_core_web_sm
```

### Issue: PDF reading errors
Install one of the PDF libraries:
```bash
pip install pdfplumber
# OR
pip install pymupdf
```

### Issue: Sentence transformers download slow
The model downloads automatically on first use. Ensure you have a stable internet connection.

## 📝 License

This project is open source and available for educational and personal use.

## 👤 Author

**Your Name**  
AI / ML | NLP | Data Analytics

## 🔥 Resume Lines

### Short Version:
> Built an AI-powered resume–job matching system using NLP and semantic embeddings to evaluate candidate-job fit and identify skill gaps with explainable scoring.

### Detailed Version (for technical interviews):
> Developed an advanced AI-powered resume–job matching system featuring explainable AI (XAI) for transparent scoring, skill confidence analysis, multi-job comparison capabilities, ATS optimization, and AI-powered resume rewrite suggestions. The system uses sentence transformers for semantic matching, NLP for skill extraction, and provides actionable insights to improve resume alignment with job requirements.

### Feature Highlights for Resume:
- **Explainable AI**: Implemented transparent, interpretable match scores with detailed section breakdowns
- **Skill Confidence Scoring**: Analyzed skill strength based on context, verb usage, and frequency
- **Multi-Job Comparison**: Built dashboard to compare resume fit across multiple positions simultaneously
- **ATS Optimization**: Developed analyzer for applicant tracking system compatibility
- **Resume Rewrite Engine**: Created AI-powered suggestions for improving bullet points and keyword integration

---

**Made with ❤️ using Python, spaCy, Sentence Transformers, and Advanced NLP Techniques**

---

## 📚 Additional Documentation

- See [FEATURES.md](FEATURES.md) for detailed documentation of all advanced features
- See [QUICKSTART.md](QUICKSTART.md) for quick setup instructions

