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

# Page configuration
st.set_page_config(
    page_title="AI Resume-Job Matcher",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .skill-badge {
        display: inline-block;
        background-color: #4CAF50;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        margin: 0.25rem;
        font-size: 0.85rem;
    }
    .missing-skill-badge {
        display: inline-block;
        background-color: #f44336;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        margin: 0.25rem;
        font-size: 0.85rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'matcher' not in st.session_state:
    st.session_state.matcher = None
if 'results' not in st.session_state:
    st.session_state.results = None


@st.cache_resource
def load_matcher():
    """Load and cache the matcher model."""
    with st.spinner("Loading AI models... This may take a moment on first run."):
        return ResumeJobMatcher()


def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">🔍 AI-Powered Resume & Job Matching System</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Instructions")
        st.markdown("""
        1. **Upload your resume** (PDF or TXT)
        2. **Paste or upload job description** (TXT or paste text)
        3. Click **"Match Resume"** to analyze
        4. Review your **match score** and **skill gaps**
        """)
        
        st.markdown("---")
        st.header("⚙️ Advanced Options")
        
        # Custom weights
        st.subheader("Scoring Weights")
        skill_weight = st.slider("Skills", 0.0, 1.0, 0.4, 0.05)
        exp_weight = st.slider("Experience", 0.0, 1.0, 0.3, 0.05)
        edu_weight = st.slider("Education", 0.0, 1.0, 0.15, 0.05)
        tool_weight = st.slider("Tools", 0.0, 1.0, 0.15, 0.05)
        
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
        
        st.info(f"Total: {sum(custom_weights.values()):.2f}")
    
    # Main content area
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("📄 Resume")
        resume_option = st.radio(
            "Choose input method:",
            ["Upload File", "Paste Text"],
            key="resume_option"
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
                    st.success(f"✅ Resume loaded: {len(resume_text)} characters")
                    st.text_area("Preview (first 500 chars):", resume_text[:500], height=100, disabled=True)
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
                finally:
                    # Clean up temp file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
        else:
            resume_text = st.text_area(
                "Paste Resume Text:",
                height=300,
                key="resume_paste"
            )
            if resume_text:
                st.info(f"📝 {len(resume_text)} characters")
    
    with col2:
        st.header("💼 Job Description")
        job_option = st.radio(
            "Choose input method:",
            ["Upload File", "Paste Text"],
            key="job_option"
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
                    st.success(f"✅ Job description loaded: {len(job_text)} characters")
                    st.text_area("Preview (first 500 chars):", job_text[:500], height=100, disabled=True)
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
                finally:
                    # Clean up temp file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
        else:
            job_text = st.text_area(
                "Paste Job Description:",
                height=300,
                key="job_paste"
            )
            if job_text:
                st.info(f"📝 {len(job_text)} characters")
    
    st.markdown("---")
    
    # Match button
    if st.button("🚀 Match Resume", type="primary", use_container_width=True):
        if not resume_text or not job_text:
            st.warning("⚠️ Please provide both resume and job description.")
        else:
            # Load matcher
            if st.session_state.matcher is None:
                st.session_state.matcher = load_matcher()
            
            # Perform matching
            with st.spinner("🤖 Analyzing match... This may take a few seconds."):
                try:
                    results = st.session_state.matcher.match(
                        resume_text,
                        job_text,
                        weights=custom_weights
                    )
                    st.session_state.results = results
                except Exception as e:
                    st.error(f"Error during matching: {str(e)}")
                    st.exception(e)
    
    # Display results with tabs
    if st.session_state.results:
        results = st.session_state.results
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Main Results",
            "🔍 Explainable AI",
            "💪 Skill Confidence",
            "📝 ATS Optimization",
            "✍️ Resume Rewrites",
            "📈 Multi-Job Compare"
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


def _display_main_results(results):
    """Display main matching results."""
    st.markdown("---")
    st.header("📊 Matching Results")
    
    # Main metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "🎯 Match Score",
            f"{results['match_score']:.1f}%",
            delta=f"{results['match_score'] - 50:.1f}%",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            "🔗 Overall Similarity",
            f"{results['overall_similarity']:.1f}%"
        )
    
    with col3:
        gap_analysis = results['gap_analysis']
        st.metric(
            "✅ Skill Coverage",
            f"{gap_analysis['skill_coverage']:.1f}%"
        )
    
    # Section breakdown
    st.subheader("📈 Section Breakdown")
    section_cols = st.columns(4)
    
    sections = ['skills', 'experience', 'education', 'tools']
    section_names = ['Skills', 'Experience', 'Education', 'Tools']
    
    for i, (section, name) in enumerate(zip(sections, section_names)):
        with section_cols[i]:
            score = results['section_scores'][section]
            st.metric(name, f"{score:.1f}%")
    
    # Skill gap analysis
    st.markdown("---")
    st.header("🔍 Skill Gap Analysis")
    
    gap_analysis = results['gap_analysis']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Matching Skills")
        matching_skills = gap_analysis['matching_skills']
        if matching_skills:
            for skill in matching_skills:
                st.markdown(f'<span class="skill-badge">{skill}</span>', unsafe_allow_html=True)
        else:
            st.info("No matching skills found.")
        
        st.subheader("🛠️ Matching Tools")
        matching_tools = gap_analysis['matching_tools']
        if matching_tools:
            for tool in matching_tools:
                st.markdown(f'<span class="skill-badge">{tool}</span>', unsafe_allow_html=True)
        else:
            st.info("No matching tools found.")
    
    with col2:
        st.subheader("❌ Missing Skills")
        missing_skills = gap_analysis['missing_skills']
        if missing_skills:
            st.warning(f"⚠️ {len(missing_skills)} missing skills identified:")
            for skill in missing_skills:
                st.markdown(f'<span class="missing-skill-badge">{skill}</span>', unsafe_allow_html=True)
        else:
            st.success("✅ All required skills are present!")
        
        st.subheader("🔧 Missing Tools")
        missing_tools = gap_analysis['missing_tools']
        if missing_tools:
            st.warning(f"⚠️ {len(missing_tools)} missing tools identified:")
            for tool in missing_tools:
                st.markdown(f'<span class="missing-skill-badge">{tool}</span>', unsafe_allow_html=True)
        else:
            st.success("✅ All required tools are present!")
    
    # Detailed breakdown
    with st.expander("📋 Detailed Breakdown"):
        st.subheader("Resume Skills")
        st.write(", ".join(gap_analysis['resume_skills']) if gap_analysis['resume_skills'] else "None found")
        
        st.subheader("Job Required Skills")
        st.write(", ".join(gap_analysis['job_skills']) if gap_analysis['job_skills'] else "None found")
        
        st.subheader("Education Keywords")
        st.write(f"Resume: {', '.join(gap_analysis['resume_education']) if gap_analysis['resume_education'] else 'None'}")
        st.write(f"Job: {', '.join(gap_analysis['job_education']) if gap_analysis['job_education'] else 'None'}")
    
    # Recommendations
    st.markdown("---")
    st.header("💡 Recommendations")
    
    if missing_skills:
        st.info(f"""
        **To improve your match score:**
        - Consider highlighting experience with: {', '.join(missing_skills[:5])}
        - Add these skills to your resume if you have experience with them
        - Focus on the top missing skills in your cover letter
        """)
    else:
        st.success("🎉 Great! Your resume covers all required skills. Focus on highlighting your experience and achievements.")
    
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
    st.header("🔍 Explainable AI - Why This Score?")
    
    if 'explanations' not in results:
        st.info("Run the analysis first to see explainable insights.")
        return
    
    explanations = results['explanations']
    top_reasons = results.get('top_reasons_low_score', [])
    resume_highlights = results.get('resume_highlights', {})
    
    # Top reasons for low score
    if top_reasons:
        st.subheader("📉 Top 5 Reasons Your Score is Low")
        for i, reason in enumerate(top_reasons, 1):
            st.write(f"{i}. {reason}")
    
    # Section impact breakdown
    st.subheader("📊 Section Impact on Final Score")
    section_impact = explanations.get('section_impact', {})
    
    for section, data in section_impact.items():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"{section.capitalize()} Score", f"{data['score']:.1f}%")
        with col2:
            st.metric("Weight", f"{data['weight']:.1f}%")
        with col3:
            status_emoji = "✅" if data['status'] == 'strong' else "⚠️" if data['status'] == 'moderate' else "❌"
            st.metric("Contribution", f"{data['contribution']:.1f}%", help=f"Status: {data['status']}")
    
    # Top strengths
    st.subheader("✅ Top Strengths")
    strengths = explanations.get('top_strengths', [])
    if strengths:
        for strength in strengths:
            st.success(f"✓ {strength['message']}")
    else:
        st.info("No strong sections identified.")
    
    # Top weaknesses
    st.subheader("❌ Top Weaknesses")
    weaknesses = explanations.get('top_weaknesses', [])
    if weaknesses:
        for weakness in weaknesses:
            st.warning(f"⚠️ {weakness['message']}")
    else:
        st.success("No major weaknesses identified!")
    
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
    st.header("💪 Skill Confidence Analysis")
    
    if 'skill_confidence' not in results:
        st.info("Run the analysis first to see skill confidence levels.")
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
    st.header("📝 ATS Optimization Analysis")
    
    if 'ats_analysis' not in results:
        st.info("Run the analysis first to see ATS optimization insights.")
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
    st.header("✍️ Resume Rewrite Suggestions")
    
    if 'rewrite_suggestions' not in results:
        st.info("Run the analysis first to see rewrite suggestions.")
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
    st.header("📈 Multi-Job Comparison")
    st.info("Compare your resume against multiple job descriptions at once!")
    
    if not resume_text:
        st.warning("Please upload or paste your resume first.")
        return
    
    # Job descriptions input
    st.subheader("Add Job Descriptions")
    num_jobs = st.number_input("Number of jobs to compare", min_value=1, max_value=10, value=2)
    
    job_descriptions = {}
    for i in range(num_jobs):
        job_title = st.text_input(f"Job {i+1} Title", key=f"job_title_{i}", placeholder="e.g., Software Engineer at Google")
        job_text = st.text_area(f"Job {i+1} Description", key=f"job_text_{i}", height=150)
        if job_title and job_text:
            job_descriptions[job_title] = job_text
    
    if st.button("🔄 Compare All Jobs", type="primary"):
        if not job_descriptions:
            st.warning("Please add at least one job description.")
        else:
            with st.spinner("Comparing against all jobs..."):
                comparator = MultiJobComparator(matcher)
                comparison_results = comparator.compare_multiple_jobs(resume_text, job_descriptions)
                st.session_state.comparison_results = comparison_results
    
    # Display comparison results
    if 'comparison_results' in st.session_state:
        results = st.session_state.comparison_results
        
        st.subheader("📊 Job Rankings")
        
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
        
        # Best fit jobs
        st.subheader("🏆 Best Fit Jobs")
        top_jobs = results[:3]
        for i, job in enumerate(top_jobs, 1):
            with st.expander(f"#{i} {job['job_id']} - {job['match_score']:.1f}% match"):
                st.metric("Match Score", f"{job['match_score']:.1f}%")
                st.metric("Skill Coverage", f"{job['gap_analysis']['skill_coverage']:.1f}%")
                
                missing = job['gap_analysis']['missing_skills'][:5]
                if missing:
                    st.write("**Top Missing Skills:**", ", ".join(missing))
        
        # Summary statistics
        if len(results) > 1:
            st.subheader("📈 Comparison Summary")
            avg_score = sum(r['match_score'] for r in results) / len(results)
            st.metric("Average Match Score", f"{avg_score:.1f}%")
            st.metric("Best Match", f"{results[0]['match_score']:.1f}%")
            st.metric("Worst Match", f"{results[-1]['match_score']:.1f}%")


if __name__ == "__main__":
    main()

