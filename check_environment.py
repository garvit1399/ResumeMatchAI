"""
Environment Check Script
Checks if the system is ready to run the Resume-Job Matcher.
"""

import sys
import subprocess

def check_python_version():
    """Check Python version compatibility."""
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and 8 <= version.minor <= 13:
        print("✅ Python version is compatible")
        if version.minor in [11, 12]:
            print("   (Recommended version)")
        return True
    elif version.major == 3 and version.minor >= 14:
        print("❌ Python 3.14+ detected - may have compatibility issues with spaCy")
        print("   RECOMMENDATION: Use Python 3.11 or 3.12")
        return False
    else:
        print("❌ Python version too old. Requires Python 3.8+")
        return False

def check_package(package_name, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} is installed")
        return True
    except ImportError:
        print(f"❌ {package_name} is NOT installed")
        return False
    except Exception as e:
        print(f"⚠️  {package_name} has issues: {e}")
        return False

def check_spacy_model():
    """Check if spaCy model is installed."""
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy model 'en_core_web_sm' is installed")
            return True
        except OSError:
            print("❌ spaCy model 'en_core_web_sm' is NOT installed")
            print("   Run: python -m spacy download en_core_web_sm")
            return False
    except ImportError:
        print("⚠️  Cannot check spaCy model (spaCy not installed)")
        return False
    except Exception as e:
        print(f"⚠️  Error checking spaCy: {e}")
        if sys.version_info >= (3, 14):
            print("   This is likely a Python 3.14+ compatibility issue")
        return False

def main():
    """Run all checks."""
    print("=" * 60)
    print("Resume-Job Matcher - Environment Check")
    print("=" * 60)
    print()
    
    all_ok = True
    
    # Check Python version
    print("1. Checking Python version...")
    if not check_python_version():
        all_ok = False
    print()
    
    # Check required packages
    print("2. Checking required packages...")
    packages = [
        ("streamlit", "streamlit"),
        ("numpy", "numpy"),
        ("scikit-learn", "sklearn"),
        ("pandas", "pandas"),
        ("sentence-transformers", "sentence_transformers"),
        ("pdfplumber", "pdfplumber"),
    ]
    
    for pkg_name, import_name in packages:
        if not check_package(pkg_name, import_name):
            all_ok = False
    
    print()
    
    # Check spaCy (may fail on Python 3.14+)
    print("3. Checking spaCy...")
    spacy_ok = check_package("spacy", "spacy")
    if spacy_ok:
        check_spacy_model()
    else:
        all_ok = False
    print()
    
    # Summary
    print("=" * 60)
    if all_ok:
        print("✅ All checks passed! You're ready to run the application.")
        print("   Run: streamlit run app.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        if sys.version_info >= (3, 14):
            print()
            print("⚠️  IMPORTANT: Python 3.14+ compatibility issue detected.")
            print("   Solution: Use Python 3.11 or 3.12")
            print("   Install Python 3.12: https://www.python.org/downloads/")
    print("=" * 60)

if __name__ == "__main__":
    main()

