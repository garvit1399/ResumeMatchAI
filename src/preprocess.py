"""
Text Preprocessing Module
Performs NLP preprocessing: tokenization, lemmatization, stopword removal.
"""

import re
import string
import sys
from typing import List

# Basic stopwords list (fallback when spaCy is not available)
BASIC_STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
    'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
    'had', 'what', 'said', 'each', 'which', 'their', 'time', 'if', 'up',
    'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her', 'would',
    'make', 'like', 'into', 'him', 'has', 'two', 'more', 'very', 'after',
    'words', 'long', 'than', 'first', 'been', 'call', 'who', 'oil', 'sit',
    'now', 'find', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part'
}

# Lazy import spaCy to handle compatibility issues
SPACY_AVAILABLE = False
SPACY_ERROR = None

def _try_import_spacy():
    """Try to import spaCy and return status."""
    global SPACY_AVAILABLE, SPACY_ERROR
    if SPACY_AVAILABLE:
        return True
    
    try:
        import spacy
        SPACY_AVAILABLE = True
        return True
    except Exception as e:
        SPACY_ERROR = str(e)
        # Check if it's a Python version compatibility issue
        if sys.version_info >= (3, 14):
            SPACY_ERROR = (
                f"spaCy compatibility issue with Python {sys.version_info.major}.{sys.version_info.minor}. "
                f"spaCy requires Python 3.8-3.13. Using fallback preprocessing. "
                f"Original error: {e}"
            )
        return False


class TextPreprocessor:
    """Handles text preprocessing using spaCy with fallback to basic preprocessing."""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize preprocessor.
        
        Args:
            model_name: spaCy model name (default: en_core_web_sm)
        """
        self.model_name = model_name
        self.nlp = None
        self.use_spacy = False
        self._load_spacy()
    
    def _load_spacy(self):
        """Lazy load spaCy to handle import errors gracefully."""
        if _try_import_spacy():
            import spacy
            try:
                self.nlp = spacy.load(self.model_name)
                self.use_spacy = True
                return
            except (OSError, Exception) as e:
                # If model loading fails, fall back to basic preprocessing
                if sys.version_info >= (3, 14):
                    print(f"Warning: spaCy model loading failed (Python 3.14 compatibility issue). "
                          f"Using fallback preprocessing. Error: {e}")
                else:
                    print(f"Warning: spaCy model '{self.model_name}' not found. "
                          f"Using fallback preprocessing. Download with: python -m spacy download {self.model_name}")
                self.use_spacy = False
        else:
            # spaCy not available, use fallback
            if sys.version_info >= (3, 14):
                print(f"Warning: {SPACY_ERROR}\nUsing fallback preprocessing (basic tokenization).")
            else:
                print(f"Warning: spaCy not available. Using fallback preprocessing.\n"
                      f"Install with: pip install spacy && python -m spacy download en_core_web_sm")
            self.use_spacy = False
    
    def _basic_preprocess(self, text: str, remove_stopwords: bool = True) -> str:
        """
        Basic preprocessing fallback when spaCy is not available.
        
        Args:
            text: Raw input text
            remove_stopwords: Whether to remove stopwords
            
        Returns:
            Preprocessed text as single string
        """
        if not text:
            return ""
        
        # Clean text: remove extra whitespace, normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip().lower()
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Tokenize (split on whitespace)
        tokens = text.split()
        
        # Remove stopwords if requested
        if remove_stopwords:
            tokens = [token for token in tokens if token not in BASIC_STOPWORDS]
        
        return " ".join(tokens)
    
    def preprocess(self, text: str, remove_stopwords: bool = True) -> str:
        """
        Preprocess text: lowercase, tokenize, lemmatize, remove stopwords.
        
        Args:
            text: Raw input text
            remove_stopwords: Whether to remove stopwords
            
        Returns:
            Preprocessed text as single string
        """
        if not text:
            return ""
        
        # Use fallback if spaCy is not available
        if not self.use_spacy:
            return self._basic_preprocess(text, remove_stopwords)
        
        # Clean text: remove extra whitespace, normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Process with spaCy
        doc = self.nlp(text)
        
        # Extract tokens: lemmatize, filter stopwords and punctuation
        tokens = []
        for token in doc:
            # Skip punctuation, whitespace, and optionally stopwords
            if token.is_punct or token.is_space:
                continue
            if remove_stopwords and token.is_stop:
                continue
            
            # Use lemma (root form) in lowercase
            lemma = token.lemma_.lower().strip()
            if lemma:
                tokens.append(lemma)
        
        return " ".join(tokens)
    
    def preprocess_list(self, text: str, remove_stopwords: bool = True) -> List[str]:
        """
        Preprocess text and return as list of tokens.
        
        Args:
            text: Raw input text
            remove_stopwords: Whether to remove stopwords
            
        Returns:
            List of preprocessed tokens
        """
        preprocessed = self.preprocess(text, remove_stopwords)
        return preprocessed.split() if preprocessed else []
    
    def extract_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text.
        
        Args:
            text: Raw input text
            
        Returns:
            List of sentences
        """
        if not text:
            return []
        
        # Use fallback if spaCy is not available
        if not self.use_spacy:
            # Basic sentence splitting on punctuation
            sentences = re.split(r'[.!?]+\s+', text)
            return [s.strip() for s in sentences if s.strip()]
        
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        return sentences

