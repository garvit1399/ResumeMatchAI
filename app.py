"""
Streamlit Frontend Application
Interactive web interface for resume-job matching.
"""

import streamlit as st
import os
from pathlib import Path
import tempfile
import pandas as pd

from src.parser import extract_text
from src.matcher import ResumeJobMatcher
from src.multi_job_comparison import MultiJobComparator
from src.maris_controller import MARISController

# Page configuration
st.set_page_config(
    page_title="ResumeMatch AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "ResumeMatch AI - Intelligent resume-job matching powered by advanced NLP and multi-agent AI systems"
    }
)

# Enhanced CSS for modern, human-designed UI
st.markdown("""
    <style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .sub-header {
        text-align: center;
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2.5rem;
        font-weight: 400;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.5);
    }
    
    /* Skill badges */
    .skill-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        margin: 0.3rem;
        font-size: 0.9rem;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
        transition: transform 0.2s;
    }
    
    .skill-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
    }
    
    .missing-skill-badge {
        display: inline-block;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        margin: 0.3rem;
        font-size: 0.9rem;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(245, 87, 108, 0.3);
    }
    
    /* Section headers */
    h2 {
        color: #1f2937;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
        padding-left: 1rem;
    }
    
    h3 {
        color: #374151;
        font-weight: 600;
        margin-top: 1.5rem;
    }
    
    /* Input areas */
    .stTextArea textarea {
        border-radius: 8px;
        border: 2px solid #e5e7eb;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
        border: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #f9fafb;
    }
    
    /* Info boxes */
    .stInfo {
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
    }
    
    .stSuccess {
        border-radius: 8px;
        border-left: 4px solid #10b981;
    }
    
    .stWarning {
        border-radius: 8px;
        border-left: 4px solid #f59e0b;
    }
    
    .stError {
        border-radius: 8px;
        border-left: 4px solid #ef4444;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* File uploader */
    .uploadedFile {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'matcher' not in st.session_state:
    st.session_state.matcher = None
if 'results' not in st.session_state:
    st.session_state.results = None
if 'maris_controller' not in st.session_state:
    st.session_state.maris_controller = None
if 'maris_results' not in st.session_state:
    st.session_state.maris_results = None
if 'use_maris' not in st.session_state:
    st.session_state.use_maris = False


@st.cache_resource
def load_matcher():
    """Load and cache the matcher model."""
    with st.spinner("Loading AI models... This may take a moment on first run."):
        return ResumeJobMatcher()

@st.cache_resource
def load_maris():
    """Load and cache the MARIS controller."""
    with st.spinner("Initializing MARIS agents... This may take a moment."):
        return MARISController()


def main():
    """Main application function."""
    
    # Modern header with gradient
    st.markdown('<h1 class="main-header">ResumeMatch AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Match your resume with job opportunities using intelligent AI analysis</p>', unsafe_allow_html=True)
    
    # Sidebar with improved design
    with st.sidebar:
        st.markdown("### 🎯 Quick Start")
        st.markdown("""
        **Step 1:** Upload or paste your resume  
        **Step 2:** Add the job description  
        **Step 3:** Get instant match analysis
        """)
        
        st.markdown("---")
        
        st.markdown("### ⚙️ Settings")
        
        # MARIS Mode Toggle with better design
        st.markdown("**AI Analysis Mode**")
        use_maris = st.toggle(
            "🤖 Multi-Agent System (MARIS)",
            value=st.session_state.use_maris,
            help="Advanced mode with multiple AI agents that verify each other's analysis for higher accuracy"
        )
        st.session_state.use_maris = use_maris
        
        if use_maris:
            st.success("✓ **MARIS Active** - Enhanced accuracy with agent verification")
        else:
            st.info("**Standard Mode** - Fast single-model analysis")
        
        st.markdown("---")
        
        # Custom weights with better UI
        st.markdown("**Match Scoring Preferences**")
        st.caption("Adjust how much each factor influences your match score")
        
        skill_weight = st.slider("💼 Skills", 0.0, 1.0, 0.4, 0.05, help="Technical skills and competencies")
        exp_weight = st.slider("📈 Experience", 0.0, 1.0, 0.3, 0.05, help="Years and depth of experience")
        edu_weight = st.slider("🎓 Education", 0.0, 1.0, 0.15, 0.05, help="Educational qualifications")
        tool_weight = st.slider("🛠️ Tools", 0.0, 1.0, 0.15, 0.05, help="Tools and technologies")
        
        # Normalize weights
        total = skill_weight + exp_weight + edu_weight + tool_weight
        if total > 0:
            skill_weight /= total
            exp_weight /= total
            edu_weight /= total
            tool_weight /= total
        
        custom_weights = {
            'skills': skill_weight,
            'experience': exp_weight,
            'education': edu_weight,
            'tools': tool_weight
        }
        
        # Visual weight indicator
        if abs(sum(custom_weights.values()) - 1.0) < 0.01:
            st.success(f"✓ Weights balanced ({sum(custom_weights.values()):.0%})")
        else:
            st.warning(f"Weights: {sum(custom_weights.values()):.0%}")
        
        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.caption("• Upload PDF resumes for best results\n• Include full job descriptions for accurate matching\n• Review skill gaps to improve your resume")
    
    # Main content area with better layout
    st.markdown("### 📝 Input Your Information")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("#### 📄 Your Resume")
        resume_option = st.radio(
            "How would you like to add your resume?",
            ["📤 Upload File", "✍️ Paste Text"],
            key="resume_option",
            horizontal=True
        )
        
        resume_text = ""
        if resume_option == "Upload File":
            resume_file = st.file_uploader(
                "Upload Resume (PDF or TXT)",
                type=['pdf', 'txt'],
                key="resume_upload"
            )
            if resume_file:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(resume_file.name)[1]) as tmp_file:
                    tmp_file.write(resume_file.read())
                    tmp_path = tmp_file.name
                
                try:
                    resume_text = extract_text(tmp_path)
                    st.success(f"✓ Resume loaded successfully ({len(resume_text):,} characters)")
                    with st.expander("👁️ Preview resume"):
                        st.text(resume_text[:500] + "..." if len(resume_text) > 500 else resume_text)
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
                finally:
                    # Clean up temp file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
        else:
            resume_text = st.text_area(
                "Paste your resume content here:",
                height=300,
                key="resume_paste",
                placeholder="Copy and paste your resume text here, or upload a file above..."
            )
            if resume_text:
                st.caption(f"📝 {len(resume_text):,} characters entered")
    
    with col2:
        st.markdown("#### 💼 Job Description")
        job_option = st.radio(
            "How would you like to add the job description?",
            ["📤 Upload File", "✍️ Paste Text"],
            key="job_option",
            horizontal=True
        )
        
        job_text = ""
        if job_option == "Upload File":
            job_file = st.file_uploader(
                "Upload Job Description (TXT)",
                type=['txt'],
                key="job_upload"
            )
            if job_file:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
                    tmp_file.write(job_file.read())
                    tmp_path = tmp_file.name
                
                try:
                    job_text = extract_text(tmp_path)
                    st.success(f"✓ Job description loaded successfully ({len(job_text):,} characters)")
                    with st.expander("👁️ Preview job description"):
                        st.text(job_text[:500] + "..." if len(job_text) > 500 else job_text)
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
                finally:
                    # Clean up temp file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
        else:
            job_text = st.text_area(
                "Paste the job description here:",
                height=300,
                key="job_paste",
                placeholder="Copy and paste the job description here, or upload a file above..."
            )
            if job_text:
                st.caption(f"📝 {len(job_text):,} characters entered")
    
    st.markdown("---")
    
    # Enhanced match button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        match_button = st.button(
            "🎯 Analyze Match",
            type="primary",
            use_container_width=True,
            help="Click to analyze how well your resume matches the job description"
        )
    
    if match_button:
        if not resume_text or not job_text:
            st.warning("👋 Please provide both your resume and the job description to get started.")
        else:
            if st.session_state.use_maris:
                # Use MARIS system
                if st.session_state.maris_controller is None:
                    st.session_state.maris_controller = load_maris()
                
                with st.spinner("🤖 MARIS agents analyzing... This may take a few seconds."):
                    try:
                        maris_results = st.session_state.maris_controller.run_pipeline(
                            resume_text,
                            job_text
                        )
                        st.session_state.maris_results = maris_results
                        st.session_state.results = None  # Clear standard results
                    except Exception as e:
                        st.error(f"Error during MARIS analysis: {str(e)}")
                        st.exception(e)
            else:
                # Use standard matcher
                if st.session_state.matcher is None:
                    st.session_state.matcher = load_matcher()
                
                with st.spinner("🤖 Analyzing match... This may take a few seconds."):
                    try:
                        results = st.session_state.matcher.match(
                            resume_text,
                            job_text,
                            weights=custom_weights
                        )
                        st.session_state.results = results
                        st.session_state.maris_results = None  # Clear MARIS results
                    except Exception as e:
                        st.error(f"Error during matching: {str(e)}")
                        st.exception(e)
    
    # Display results with tabs
    if st.session_state.maris_results:
        # MARIS Results
        _display_maris_results(st.session_state.maris_results)
    elif st.session_state.results:
        # Standard Results
        results = st.session_state.results
        
        # Create tabs with better labels
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📊 Overview",
            "🔍 Why This Score?",
            "💪 Your Skills",
            "📝 ATS Check",
            "✍️ Improve Resume",
            "📈 Compare Jobs",
            "🤖 AI Analysis"
        ])
        
        with tab1:
            _display_main_results(results)
        
        with tab2:
            _display_explainable_ai(results)
        
        with tab3:
            _display_skill_confidence(results)
        
        with tab4:
            _display_ats_optimization(results)
        
        with tab5:
            _display_resume_rewrites(results)
        
        with tab6:
            _display_multi_job_comparison(resume_text, st.session_state.matcher)
        
        with tab7:
            _display_multi_agent_system(results)


def _display_main_results(results):
    """Display main matching results."""
    # Hero section with main score
    score = results['match_score']
    
    # Color coding based on score
    if score >= 80:
        score_color = "#10b981"  # Green
        score_label = "Excellent Match"
    elif score >= 60:
        score_color = "#3b82f6"  # Blue
        score_label = "Good Match"
    elif score >= 40:
        score_color = "#f59e0b"  # Orange
        score_label = "Moderate Match"
    else:
        score_color = "#ef4444"  # Red
        score_label = "Needs Improvement"
    
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 16px; margin-bottom: 2rem;">
        <h2 style="color: {score_color}; font-size: 4rem; margin: 0; font-weight: 700;">{score:.1f}%</h2>
        <p style="color: #6b7280; font-size: 1.2rem; margin-top: 0.5rem; font-weight: 500;">{score_label}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics in a row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Overall Similarity",
            f"{results['overall_similarity']:.1f}%",
            help="How similar your resume is to the job description overall"
        )
    
    with col2:
        gap_analysis = results['gap_analysis']
        st.metric(
            "Skill Coverage",
            f"{gap_analysis['skill_coverage']:.1f}%",
            help="Percentage of required skills you have"
        )
    
    with col3:
        section_scores = results['section_scores']
        st.metric(
            "Skills Match",
            f"{section_scores['skills']:.1f}%",
            help="How well your skills match the job requirements"
        )
    
    with col4:
        st.metric(
            "Experience Match",
            f"{section_scores['experience']:.1f}%",
            help="How well your experience aligns with the job"
        )
    
    st.markdown("---")
    
    # Section breakdown with visual bars
    st.markdown("### 📊 Detailed Breakdown")
    section_scores = results['section_scores']
    
    sections_data = [
        ('skills', '💼 Skills', section_scores['skills']),
        ('experience', '📈 Experience', section_scores['experience']),
        ('education', '🎓 Education', section_scores['education']),
        ('tools', '🛠️ Tools', section_scores['tools'])
    ]
    
    for section_key, section_name, score in sections_data:
        col_label, col_bar, col_score = st.columns([2, 5, 1])
        with col_label:
            st.write(f"**{section_name}**")
        with col_bar:
            # Visual progress bar
            bar_color = "#10b981" if score >= 70 else "#3b82f6" if score >= 50 else "#f59e0b" if score >= 30 else "#ef4444"
            st.markdown(f"""
            <div style="background: #e5e7eb; border-radius: 10px; height: 24px; overflow: hidden;">
                <div style="background: {bar_color}; width: {score}%; height: 100%; border-radius: 10px; transition: width 0.3s;"></div>
            </div>
            """, unsafe_allow_html=True)
        with col_score:
            st.write(f"**{score:.0f}%**")
    
    st.markdown("---")
    
    # Skill gap analysis with better visual design
    st.markdown("### 🎯 Skills Analysis")
    gap_analysis = results['gap_analysis']
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("#### ✅ Skills You Have")
        matching_skills = gap_analysis['matching_skills']
        if matching_skills:
            st.caption(f"Great! You have {len(matching_skills)} matching skills")
            skill_text = " ".join([f'<span class="skill-badge">{skill}</span>' for skill in matching_skills])
            st.markdown(skill_text, unsafe_allow_html=True)
        else:
            st.info("No matching skills detected. Try adding more technical skills to your resume.")
        
        st.markdown("---")
        st.markdown("#### 🛠️ Tools You Know")
        matching_tools = gap_analysis['matching_tools']
        if matching_tools:
            st.caption(f"You're familiar with {len(matching_tools)} required tools")
            tool_text = " ".join([f'<span class="skill-badge">{tool}</span>' for tool in matching_tools])
            st.markdown(tool_text, unsafe_allow_html=True)
        else:
            st.info("No matching tools found.")
    
    with col2:
        st.markdown("#### ⚠️ Skills to Learn")
        missing_skills = gap_analysis['missing_skills']
        if missing_skills:
            st.caption(f"Focus on learning {len(missing_skills)} missing skills to improve your match")
            skill_text = " ".join([f'<span class="missing-skill-badge">{skill}</span>' for skill in missing_skills])
            st.markdown(skill_text, unsafe_allow_html=True)
        else:
            st.success("🎉 Excellent! You have all the required skills.")
        
        st.markdown("---")
        st.markdown("#### 🔧 Tools to Consider")
        missing_tools = gap_analysis['missing_tools']
        if missing_tools:
            st.caption(f"Consider learning {len(missing_tools)} additional tools")
            tool_text = " ".join([f'<span class="missing-skill-badge">{tool}</span>' for tool in missing_tools])
            st.markdown(tool_text, unsafe_allow_html=True)
        else:
            st.success("✓ You know all the required tools!")
    
    # Detailed breakdown
    with st.expander("📋 Detailed Breakdown"):
        st.subheader("Resume Skills")
        st.write(", ".join(gap_analysis['resume_skills']) if gap_analysis['resume_skills'] else "None found")
        
        st.subheader("Job Required Skills")
        st.write(", ".join(gap_analysis['job_skills']) if gap_analysis['job_skills'] else "None found")
        
        st.subheader("Education Keywords")
        st.write(f"Resume: {', '.join(gap_analysis['resume_education']) if gap_analysis['resume_education'] else 'None'}")
        st.write(f"Job: {', '.join(gap_analysis['job_education']) if gap_analysis['job_education'] else 'None'}")
    
    st.markdown("---")
    
    # Actionable recommendations
    st.markdown("### 💡 How to Improve Your Match")
    
    if missing_skills:
        st.info(f"""
        **🎯 Action Items:**
        
        1. **Learn or highlight**: {', '.join(missing_skills[:3])}
        2. **Add to resume**: If you have experience with any missing skills, make sure they're clearly mentioned
        3. **Cover letter**: Emphasize your willingness to learn and any related experience
        
        **💪 Quick Win**: Focus on the top 2-3 missing skills first - they'll have the biggest impact on your score.
        """)
    else:
        st.success("""
        **🎉 Great News!**
        
        Your resume already covers all the required skills. To further improve:
        - Highlight specific achievements and projects
        - Quantify your experience with metrics
        - Emphasize leadership and collaboration examples
        """)
    
    # Export results (optional)
    if st.button("📥 Download Results Summary"):
        summary = f"""
RESUME-JOB MATCHING RESULTS
===========================

Match Score: {results['match_score']:.2f}%
Overall Similarity: {results['overall_similarity']:.2f}%
Skill Coverage: {gap_analysis['skill_coverage']:.2f}%

SECTION SCORES:
- Skills: {results['section_scores']['skills']:.2f}%
- Experience: {results['section_scores']['experience']:.2f}%
- Education: {results['section_scores']['education']:.2f}%
- Tools: {results['section_scores']['tools']:.2f}%

MATCHING SKILLS ({len(matching_skills)}):
{', '.join(matching_skills) if matching_skills else 'None'}

MISSING SKILLS ({len(missing_skills)}):
{', '.join(missing_skills) if missing_skills else 'None'}

MISSING TOOLS ({len(missing_tools)}):
{', '.join(missing_tools) if missing_tools else 'None'}
"""
        st.download_button(
            label="Download as TXT",
            data=summary,
            file_name="match_results.txt",
            mime="text/plain"
        )


def _display_explainable_ai(results):
    """Display explainable AI analysis."""
    st.markdown("### 🔍 Understanding Your Score")
    st.caption("See exactly why you got this score and what influenced it")
    
    if 'explanations' not in results:
        st.info("💡 Run the analysis first to see detailed insights about your match score.")
        return
    
    explanations = results['explanations']
    top_reasons = results.get('top_reasons_low_score', [])
    resume_highlights = results.get('resume_highlights', {})
    
    # Top reasons for low score
    if top_reasons:
        st.markdown("#### ⚠️ What's Holding You Back")
        st.caption("These factors are reducing your match score:")
        for i, reason in enumerate(top_reasons, 1):
            st.markdown(f"**{i}.** {reason}")
    else:
        st.success("✅ No major issues detected! Your score looks good.")
    
    st.markdown("---")
    
    # Section impact breakdown with visual design
    st.markdown("#### 📊 How Each Section Affects Your Score")
    section_impact = explanations.get('section_impact', {})
    
    section_names = {
        'skills': '💼 Skills',
        'experience': '📈 Experience',
        'education': '🎓 Education',
        'tools': '🛠️ Tools'
    }
    
    for section, data in section_impact.items():
        section_name = section_names.get(section, section.capitalize())
        
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{section_name}**")
                # Visual indicator
                status_color = "#10b981" if data['status'] == 'strong' else "#f59e0b" if data['status'] == 'moderate' else "#ef4444"
                status_text = "Strong" if data['status'] == 'strong' else "Moderate" if data['status'] == 'moderate' else "Weak"
                st.caption(f"Status: <span style='color: {status_color}; font-weight: 600;'>{status_text}</span>", unsafe_allow_html=True)
            with col2:
                st.metric("Score", f"{data['score']:.0f}%")
            with col3:
                st.metric("Impact", f"{data['contribution']:.1f}%")
            
            st.markdown("---")
    
    # Top strengths and weaknesses in columns
    col_strength, col_weakness = st.columns(2, gap="large")
    
    with col_strength:
        st.markdown("#### ✅ Your Strengths")
        strengths = explanations.get('top_strengths', [])
        if strengths:
            for strength in strengths:
                st.success(f"✓ {strength['message']}")
        else:
            st.info("Analyzing your strengths...")
    
    with col_weakness:
        st.markdown("#### ⚠️ Areas to Improve")
        weaknesses = explanations.get('top_weaknesses', [])
        if weaknesses:
            for weakness in weaknesses:
                st.warning(f"⚠️ {weakness['message']}")
        else:
            st.success("🎉 No major weaknesses! You're doing great.")
    
    # Resume highlights
    if resume_highlights:
        st.subheader("💡 Resume Sections That Helped")
        helpful = resume_highlights.get('helpful', [])
        if helpful:
            for item in helpful[:3]:
                with st.expander(f"✓ {item['reason']}"):
                    st.write(item['text'])
        
        st.subheader("⚠️ Resume Sections That Hurt")
        hurtful = resume_highlights.get('hurtful', [])
        if hurtful:
            for item in hurtful[:2]:
                with st.expander(f"⚠️ {item['reason']}"):
                    st.write(item['text'])


def _display_skill_confidence(results):
    """Display skill confidence analysis."""
    st.markdown("### 💪 Your Skills Breakdown")
    st.caption("See how strong your skills are based on how you've presented them")
    
    if 'skill_confidence' not in results:
        st.info("💡 Run the analysis first to see detailed skill confidence levels.")
        return
    
    skill_confidence = results['skill_confidence']
    skill_summary = results.get('skill_strength_summary', {})
    
    # Summary by strength
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Strong Skills", len(skill_summary.get('strong', [])))
    with col2:
        st.metric("Moderate Skills", len(skill_summary.get('moderate', [])))
    with col3:
        st.metric("Weak Skills", len(skill_summary.get('weak', [])))
    
    # Display skills by confidence level
    st.subheader("Strong Skills")
    strong_skills = skill_summary.get('strong', [])
    if strong_skills:
        for skill in strong_skills[:10]:
            data = skill_confidence.get(skill, {})
            st.success(f"✅ **{skill}** - {data.get('mentions', 0)} mentions, {data.get('confidence', 'N/A')} confidence")
    else:
        st.info("No strong skills identified.")
    
    st.subheader("Moderate Skills")
    moderate_skills = skill_summary.get('moderate', [])
    if moderate_skills:
        for skill in moderate_skills[:10]:
            data = skill_confidence.get(skill, {})
            st.info(f"⚡ **{skill}** - {data.get('mentions', 0)} mentions")
    else:
        st.info("No moderate skills identified.")
    
    st.subheader("Weak Skills (Mentioned Once)")
    weak_skills = skill_summary.get('weak', [])
    if weak_skills:
        for skill in weak_skills[:10]:
            data = skill_confidence.get(skill, {})
            st.warning(f"⚠️ **{skill}** - {data.get('mentions', 0)} mention(s)")


def _display_ats_optimization(results):
    """Display ATS optimization analysis."""
    st.markdown("### 📝 ATS Compatibility Check")
    st.caption("See how well your resume will work with Applicant Tracking Systems")
    
    if 'ats_analysis' not in results:
        st.info("💡 Run the analysis first to check your resume's ATS compatibility.")
        return
    
    ats_analysis = results['ats_analysis']
    ats_recommendations = results.get('ats_recommendations', [])
    
    # ATS Score
    ats_score = ats_analysis.get('ats_score', 0)
    st.metric("ATS Compatibility Score", f"{ats_score:.1f}%", 
              delta=f"{ats_score - 70:.1f}%" if ats_score >= 70 else f"{ats_score - 70:.1f}%",
              delta_color="normal" if ats_score >= 70 else "inverse")
    
    # Issues
    st.subheader("⚠️ Issues Found")
    issues = ats_analysis.get('issues', [])
    if issues:
        for issue in issues:
            st.error(f"❌ {issue}")
    else:
        st.success("✅ No major ATS issues found!")
    
    # Recommendations
    st.subheader("💡 Recommendations")
    if ats_recommendations:
        for i, rec in enumerate(ats_recommendations, 1):
            st.write(f"{i}. {rec}")
    else:
        st.success("✅ Your resume is ATS-optimized!")
    
    # Missing sections
    missing_sections = ats_analysis.get('missing_sections', [])
    if missing_sections:
        st.warning(f"⚠️ Missing sections: {', '.join(missing_sections)}")
    
    # Keyword placement
    keyword_placement = ats_analysis.get('keyword_placement', {})
    if keyword_placement:
        st.subheader("🔑 Keyword Placement Analysis")
        with st.expander("View keyword details"):
            for keyword, data in list(keyword_placement.items())[:10]:
                status = "✅" if data['present'] else "❌"
                st.write(f"{status} **{keyword}**: {data['mentions']} mentions - {data['recommendation']}")


def _display_resume_rewrites(results):
    """Display resume rewrite suggestions."""
    st.markdown("### ✍️ Improve Your Resume")
    st.caption("Get AI-powered suggestions to make your resume bullet points more impactful")
    
    if 'rewrite_suggestions' not in results:
        st.info("💡 Run the analysis first to get personalized resume improvement suggestions.")
        return
    
    rewrite_suggestions = results.get('rewrite_suggestions', [])
    
    if not rewrite_suggestions:
        st.success("✅ No rewrite suggestions at this time.")
        return
    
    st.info(f"💡 Found {len(rewrite_suggestions)} suggestions to improve your resume")
    
    for i, suggestion in enumerate(rewrite_suggestions, 1):
        with st.expander(f"Suggestion {i}: {suggestion.get('reason', 'Improve this bullet point')}"):
            st.write("**Original:**")
            st.write(suggestion.get('original', ''))
            st.write("**Suggested:**")
            st.success(suggestion.get('suggested', ''))
            st.caption(f"Reason: {suggestion.get('reason', '')}")


def _display_multi_job_comparison(resume_text, matcher):
    """Display multi-job comparison interface."""
    st.markdown("### 📈 Compare Multiple Jobs")
    st.caption("See how your resume stacks up against multiple opportunities at once")
    
    if not resume_text:
        st.warning("👋 Please upload or paste your resume first to compare it with multiple jobs.")
        return
    
    if not resume_text:
        st.warning("Please upload or paste your resume first.")
        return
    
    st.markdown("---")
    
    # Job descriptions input with better UX
    st.markdown("#### Add Jobs to Compare")
    num_jobs = st.number_input(
        "How many jobs would you like to compare?",
        min_value=1,
        max_value=10,
        value=2,
        help="Compare your resume against multiple job postings simultaneously"
    )
    
    job_descriptions = {}
    for i in range(num_jobs):
        job_title = st.text_input(f"Job {i+1} Title", key=f"job_title_{i}", placeholder="e.g., Software Engineer at Google")
        job_text = st.text_area(f"Job {i+1} Description", key=f"job_text_{i}", height=150)
        if job_title and job_text:
            job_descriptions[job_title] = job_text
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        compare_button = st.button("🔄 Compare All Jobs", type="primary", use_container_width=True)
    
    if compare_button:
        if not job_descriptions:
            st.warning("👋 Please add at least one job description to compare.")
        else:
            with st.spinner(f"🤖 Analyzing your resume against {len(job_descriptions)} job{'s' if len(job_descriptions) > 1 else ''}..."):
                comparator = MultiJobComparator(matcher)
                comparison_results = comparator.compare_multiple_jobs(resume_text, job_descriptions)
                st.session_state.comparison_results = comparison_results
                st.success(f"✓ Analysis complete! Compared against {len(job_descriptions)} job{'s' if len(job_descriptions) > 1 else ''}.")
    
    # Display comparison results
    if 'comparison_results' in st.session_state:
        results = st.session_state.comparison_results
        
        st.markdown("---")
        st.markdown("#### 📊 Your Job Rankings")
        st.caption("Jobs ranked by how well your resume matches")
        
        # Ranking table
        ranking_data = []
        for i, result in enumerate(results, 1):
            ranking_data.append({
                'Rank': i,
                'Job Title': result['job_id'],
                'Match Score': f"{result['match_score']:.1f}%",
                'Skill Coverage': f"{result['gap_analysis']['skill_coverage']:.1f}%"
            })
        
        df = pd.DataFrame(ranking_data)
        st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        
        # Best fit jobs with better design
        st.markdown("#### 🏆 Top Matches")
        top_jobs = results[:3]
        for i, job in enumerate(top_jobs, 1):
            score = job['match_score']
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            
            with st.expander(f"{medal} **#{i} {job['job_id']}** - {score:.1f}% match", expanded=(i==1)):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Match Score", f"{score:.1f}%")
                with col2:
                    st.metric("Skill Coverage", f"{job['gap_analysis']['skill_coverage']:.1f}%")
                
                missing = job['gap_analysis']['missing_skills'][:5]
                if missing:
                    st.caption("**Skills to focus on:**")
                    st.write(", ".join(missing))
        
        # Summary statistics
        if len(results) > 1:
            st.subheader("📈 Comparison Summary")
            avg_score = sum(r['match_score'] for r in results) / len(results)
            st.metric("Average Match Score", f"{avg_score:.1f}%")
            st.metric("Best Match", f"{results[0]['match_score']:.1f}%")
            st.metric("Worst Match", f"{results[-1]['match_score']:.1f}%")


def _display_maris_results(maris_results):
    """Display MARIS multi-agent system results."""
    st.header("🤖 MARIS - Multi-Agent Resume Intelligence System")
    st.info("🧠 **Advanced AI System**: Multiple specialized agents collaborate, verify, and explain their analysis")
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🎯 Final Score",
            f"{maris_results['final_score']:.1f}%",
            delta=f"{maris_results['final_score'] - 50:.1f}%"
        )
    
    with col2:
        confidence_emoji = "🟢" if maris_results['confidence'] == 'High' else "🟡" if maris_results['confidence'] == 'Medium' else "🔴"
        st.metric("Confidence", f"{confidence_emoji} {maris_results['confidence']}")
    
    with col3:
        st.metric("Stability Index", f"{maris_results['stability_index']:.2f}")
    
    with col4:
        verified_emoji = "✅" if maris_results['verified'] else "⚠️"
        st.metric("Verified", f"{verified_emoji} {'Yes' if maris_results['verified'] else 'No'}")
    
    # Agent Overview
    st.markdown("---")
    st.subheader("🤖 Agent Overview")
    
    agent_metrics = maris_results['agent_metrics']
    agent_cols = st.columns(5)
    
    agent_names = [
        ('Resume Parser', 'resume_parser_confidence'),
        ('Job Analyzer', 'job_analyzer_confidence'),
        ('Match Scorer', 'match_scorer_confidence'),
        ('Skill Gap', 'skill_gap_analyzer_confidence'),
        ('Verification', 'verification_agent_confidence')
    ]
    
    for i, (name, key) in enumerate(agent_names):
        with agent_cols[i]:
            confidence = agent_metrics.get(key, 0)
            st.metric(name, f"{confidence:.2f}")
    
    st.metric("Agent Agreement", f"{agent_metrics['agent_agreement']:.1f}%")
    
    # Agent Details Tabs
    st.markdown("---")
    agent_tabs = st.tabs([
        "📊 Results Summary",
        "🧠 Agent Reasoning",
        "🔍 Agent Details",
        "⚠️ Warnings & Issues"
    ])
    
    with agent_tabs[0]:
        st.subheader("📊 Analysis Summary")
        
        # Match Score Details
        match_score = maris_results['match_score']
        st.write("**Match Score Breakdown:**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Skills", f"{match_score.get('section_scores', {}).get('skills', 0):.1f}%")
        with col2:
            st.metric("Experience", f"{match_score.get('section_scores', {}).get('experience', 0):.1f}%")
        with col3:
            st.metric("Education", f"{match_score.get('section_scores', {}).get('education', 0):.1f}%")
        with col4:
            st.metric("Tools", f"{match_score.get('section_scores', {}).get('tools', 0):.1f}%")
        
        # Skill Gap Summary
        gap_analysis = maris_results['gap_analysis']
        st.write("**Skill Gap Analysis:**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Required Coverage", f"{gap_analysis.get('required_coverage', 0):.1f}%")
            missing_req = gap_analysis.get('missing_required_skills', [])
            if missing_req:
                st.write(f"**Missing Required Skills ({len(missing_req)}):**")
                for skill in missing_req[:5]:
                    st.write(f"- {skill}")
        with col2:
            st.metric("Overall Coverage", f"{gap_analysis.get('overall_coverage', 0):.1f}%")
            matching = gap_analysis.get('matching_all_skills', [])
            if matching:
                st.write(f"**Matching Skills ({len(matching)}):**")
                for skill in matching[:5]:
                    st.write(f"- {skill}")
    
    with agent_tabs[1]:
        st.subheader("🧠 Agent Reasoning & Evidence")
        
        explainability = maris_results['explainability']
        reasoning = explainability['agent_reasoning']
        evidence = explainability['agent_evidence']
        
        for agent_name, agent_reasoning in reasoning.items():
            with st.expander(f"🤖 {agent_name.replace('_', ' ').title()}"):
                st.write("**Reasoning:**")
                st.info(agent_reasoning or "No reasoning provided")
                
                agent_evidence = evidence.get(agent_name, [])
                if agent_evidence:
                    st.write("**Evidence:**")
                    for ev in agent_evidence:
                        st.write(f"- {ev}")
    
    with agent_tabs[2]:
        st.subheader("🔍 Detailed Agent Outputs")
        
        # Resume Parser Output
        with st.expander("📄 Resume Parser Agent"):
            resume_data = maris_results['resume_data']
            st.write(f"**Skills Found:** {len(resume_data.get('skills', []))}")
            st.write(f"**Experience Years:** {resume_data.get('experience_years', 0)}")
            st.write(f"**Education Level:** {resume_data.get('education_level', 'N/A')}")
            st.write(f"**Job Titles:** {', '.join(resume_data.get('job_titles', [])[:3])}")
        
        # Job Analyzer Output
        with st.expander("💼 Job Analyzer Agent"):
            job_data = maris_results['job_data']
            st.write(f"**Required Skills:** {len(job_data.get('required_skills', []))}")
            st.write(f"**Preferred Skills:** {len(job_data.get('preferred_skills', []))}")
            st.write(f"**Role Level:** {job_data.get('role_level', 'N/A')}")
            st.write(f"**Experience Requirement:** {job_data.get('experience_requirement', 0)} years")
        
        # Verification Output
        with st.expander("✅ Verification Agent"):
            verification = maris_results['verification']
            st.write(f"**Stability Index:** {verification.get('stability_index', 0):.3f}")
            st.write(f"**Consistency Score:** {verification.get('consistency_score', 0):.3f}")
            st.write(f"**Agent Agreement:** {verification.get('agent_agreement', 0):.1f}%")
    
    with agent_tabs[3]:
        st.subheader("⚠️ Warnings & Issues")
        
        warnings = maris_results.get('warnings', [])
        if warnings:
            for warning in warnings:
                st.warning(f"⚠️ {warning}")
        else:
            st.success("✅ No warnings - all agents report clean outputs")
        
        # Agent-specific warnings
        agent_messages = maris_results['agent_messages']
        st.write("**Agent-Specific Warnings:**")
        for agent_name, message in agent_messages.items():
            agent_warnings = message.get('warnings', [])
            if agent_warnings:
                with st.expander(f"🤖 {agent_name.replace('_', ' ').title()}"):
                    for warn in agent_warnings:
                        st.warning(f"⚠️ {warn}")
    
    # Stability & Verification Details
    st.markdown("---")
    with st.expander("🔬 Stability & Verification Details"):
        verification = maris_results['verification']
        st.write(f"**Stability Index:** {verification.get('stability_index', 0):.3f}")
        st.caption("Measures score consistency across input perturbations (higher = more stable)")
        
        st.write(f"**Consistency Score:** {verification.get('consistency_score', 0):.3f}")
        st.caption("Measures agreement between different agents (higher = more consistent)")
        
        st.write(f"**Agent Agreement:** {verification.get('agent_agreement', 0):.1f}%")
        st.caption("Average confidence across all agents")
        
        if maris_results['verified']:
            st.success("✅ **Verified**: All checks passed - output is stable and consistent")
        else:
            st.warning("⚠️ **Not Verified**: Some checks failed - review warnings above")


def _display_multi_agent_system(results):
    """Display multi-agent system (MARIS) outputs and explainability."""
    st.markdown("### 🤖 AI Analysis Details")
    st.caption("See how our AI agents analyzed your resume and job match")
    
    # Check if multi-agent data exists
    if 'multi_agent' not in results or not results['multi_agent'].get('enabled', False):
        st.warning("⚠️ Multi-agent system not enabled. Enable it in the sidebar to see agent outputs.")
        return
    
    multi_agent = results['multi_agent']
    verification = multi_agent.get('verification', {})
    agent_messages = multi_agent.get('agent_messages', [])
    agent_reasoning = multi_agent.get('agent_reasoning', {})
    agent_evidence = multi_agent.get('agent_evidence', {})
    pipeline_metadata = multi_agent.get('pipeline_metadata', {})
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        final_score = verification.get('final_score', results.get('match_score', 0))
        st.metric(
            "🎯 Final Score",
            f"{final_score:.1f}%",
            delta=f"{final_score - 50:.1f}%"
        )
    
    with col2:
        confidence_level = verification.get('confidence_level', 'Medium')
        confidence_emoji = "🟢" if confidence_level == 'High' else "🟡" if confidence_level == 'Medium' else "🔴"
        st.metric("Confidence", f"{confidence_emoji} {confidence_level}")
    
    with col3:
        stability = verification.get('stability_index', 0.0)
        st.metric("Stability Index", f"{stability:.3f}")
    
    with col4:
        is_stable = verification.get('is_stable', True)
        verified_emoji = "✅" if is_stable else "⚠️"
        st.metric("Stable", f"{verified_emoji} {'Yes' if is_stable else 'No'}")
    
    # Agent Overview
    st.markdown("---")
    st.subheader("🤖 Agent Overview")
    
    agent_names = [
        'ResumeParser',
        'JobAnalyzer',
        'MatchScoring',
        'SkillGap',
        'Verification'
    ]
    
    agent_cols = st.columns(5)
    
    for i, agent_name in enumerate(agent_names):
        with agent_cols[i]:
            # Find agent message
            agent_msg = next((msg for msg in agent_messages if msg.get('agent') == agent_name), None)
            if agent_msg:
                confidence = agent_msg.get('confidence', 0.0)
                st.metric(agent_name.replace('Parser', ' Parser').replace('Analyzer', ' Analyzer').replace('Scoring', ' Scorer'), f"{confidence:.2f}")
            else:
                st.metric(agent_name, "N/A")
    
    # Agent Reasoning
    st.markdown("---")
    st.subheader("💭 Agent Reasoning")
    
    for agent_name in agent_names:
        if agent_name in agent_reasoning:
            with st.expander(f"🧠 {agent_name} - {agent_reasoning[agent_name][:50]}..."):
                st.write(f"**Reasoning:** {agent_reasoning[agent_name]}")
                
                # Show evidence if available
                if agent_name in agent_evidence:
                    st.write("**Evidence:**")
                    for evidence_item in agent_evidence[agent_name]:
                        st.write(f"  • {evidence_item}")
    
    # Verification Details
    st.markdown("---")
    st.subheader("🧪 Verification & Stability")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Stability Analysis**")
        st.metric("Stability Index", f"{stability:.3f}", 
                 help="Score consistency across perturbations (0-1, higher is better)")
        st.metric("Score Variance", f"{verification.get('score_variance', 0):.3f}",
                 help="Variance in scores across perturbations")
        
        if verification.get('is_stable', True):
            st.success("✅ Score is stable")
        else:
            st.warning("⚠️ Score may be unstable")
    
    with col2:
        st.write("**Consistency Checks**")
        consistency = verification.get('consistency_score', 0.0)
        st.metric("Consistency Score", f"{consistency:.3f}",
                 help="Self-consistency of results (0-1, higher is better)")
        
        if verification.get('is_consistent', True):
            st.success("✅ Results are consistent")
        else:
            st.warning("⚠️ Results may be inconsistent")
    
    # Warnings
    warnings = verification.get('warnings', [])
    if warnings:
        st.markdown("---")
        st.subheader("⚠️ Warnings")
        for warning in warnings:
            st.warning(warning)
    else:
        st.success("✅ No warnings - all checks passed")
    
    # Agent Contributions
    st.markdown("---")
    st.subheader("📊 Agent Contributions to Final Score")
    
    contributions = multi_agent.get('agent_contributions', {})
    if contributions:
        for section, contribution in contributions.items():
            st.write(f"**{section.capitalize()}**: {contribution:.2f}% contribution")
    
    # Pipeline Metadata
    st.markdown("---")
    st.subheader("⚙️ Pipeline Metadata")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Execution Time", f"{pipeline_metadata.get('elapsed_time', 0):.2f}s")
    with col2:
        st.metric("Agents Used", pipeline_metadata.get('agent_count', 0))
    with col3:
        avg_confidence = pipeline_metadata.get('average_confidence', 0.0)
        st.metric("Avg Confidence", f"{avg_confidence:.3f}")
    
    # Raw Agent Messages (Collapsible)
    with st.expander("🔍 View Raw Agent Messages (JSON)"):
        import json
        st.json(agent_messages)


if __name__ == "__main__":
    main()

