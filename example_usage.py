"""
Example usage of the Resume-Job Matcher system.
Demonstrates programmatic usage without the Streamlit UI.
"""

from src.matcher import ResumeJobMatcher
from src.parser import extract_text

# Example resume text
resume_text = """
John Doe
Software Engineer

EXPERIENCE:
- 5 years of experience in Python development
- Built web applications using Django and Flask
- Worked with PostgreSQL and MySQL databases
- Experience with AWS cloud services
- Proficient in Git and CI/CD pipelines

SKILLS:
Python, JavaScript, Django, Flask, PostgreSQL, MySQL, AWS, Git, Docker

EDUCATION:
Bachelor of Science in Computer Science
"""

# Example job description
job_text = """
Software Engineer Position

We are looking for a Software Engineer with:
- 3+ years of Python experience
- Experience with machine learning frameworks (TensorFlow, PyTorch)
- Knowledge of cloud platforms (AWS, Azure)
- Strong database skills (PostgreSQL, MongoDB)
- Experience with Docker and Kubernetes
- Bachelor's degree in Computer Science or related field

Required Skills:
Python, Machine Learning, TensorFlow, PyTorch, AWS, Azure, PostgreSQL, MongoDB, Docker, Kubernetes
"""


def main():
    """Example usage of the matcher."""
    print("=" * 60)
    print("Resume-Job Matching Example")
    print("=" * 60)
    
    # Initialize matcher
    print("\n1. Initializing matcher...")
    matcher = ResumeJobMatcher()
    print("   ✓ Matcher initialized")
    
    # Perform matching
    print("\n2. Computing match score...")
    results = matcher.match(resume_text, job_text)
    
    # Display results
    print("\n" + "=" * 60)
    print("MATCHING RESULTS")
    print("=" * 60)
    
    print(f"\n🎯 Match Score: {results['match_score']:.2f}%")
    print(f"🔗 Overall Similarity: {results['overall_similarity']:.2f}%")
    
    print("\n📈 Section Scores:")
    for section, score in results['section_scores'].items():
        print(f"   - {section.capitalize()}: {score:.2f}%")
    
    # Skill gap analysis
    gap = results['gap_analysis']
    print(f"\n✅ Skill Coverage: {gap['skill_coverage']:.2f}%")
    
    print(f"\n✅ Matching Skills ({len(gap['matching_skills'])}):")
    if gap['matching_skills']:
        print(f"   {', '.join(gap['matching_skills'])}")
    else:
        print("   None")
    
    print(f"\n❌ Missing Skills ({len(gap['missing_skills'])}):")
    if gap['missing_skills']:
        print(f"   {', '.join(gap['missing_skills'])}")
    else:
        print("   None - All required skills are present!")
    
    print(f"\n❌ Missing Tools ({len(gap['missing_tools'])}):")
    if gap['missing_tools']:
        print(f"   {', '.join(gap['missing_tools'])}")
    else:
        print("   None - All required tools are present!")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

