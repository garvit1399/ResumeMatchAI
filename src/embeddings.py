"""
Semantic Embeddings Module
Converts text into vector embeddings using sentence transformers.
"""

from typing import List, Union
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class EmbeddingGenerator:
    """Generates semantic embeddings for text using sentence transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding generator.
        
        Args:
            model_name: Sentence transformer model name
                        Default: 'all-MiniLM-L6-v2' (fast, good quality)
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is required. Install with: pip install sentence-transformers"
            )
        
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def encode(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for text.
        
        Args:
            text: Single text string or list of texts
            
        Returns:
            Numpy array of embeddings
            - Single text: 1D array of shape (embedding_dim,)
            - Multiple texts: 2D array of shape (num_texts, embedding_dim)
        """
        if isinstance(text, str):
            if not text.strip():
                # Return zero vector for empty text
                return np.zeros(self.embedding_dim)
            embeddings = self.model.encode(text, convert_to_numpy=True)
            return embeddings
        else:
            # List of texts
            if not text:
                return np.zeros((0, self.embedding_dim))
            # Filter out empty strings
            non_empty = [t for t in text if t.strip()]
            if not non_empty:
                return np.zeros((0, self.embedding_dim))
            embeddings = self.model.encode(non_empty, convert_to_numpy=True)
            return embeddings
    
    def encode_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of text strings
            batch_size: Batch size for processing
            
        Returns:
            2D numpy array of embeddings
        """
        if not texts:
            return np.zeros((0, self.embedding_dim))
        
        non_empty = [t for t in texts if t.strip()]
        if not non_empty:
            return np.zeros((0, self.embedding_dim))
        
        embeddings = self.model.encode(
            non_empty,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        return embeddings

