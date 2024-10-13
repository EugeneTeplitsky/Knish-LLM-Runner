from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from ..utils.logging import setup_logging
from ..config import CONFIG

logger = setup_logging(__name__, 'document_processing')

class EmbeddingGenerator:
    def __init__(self, model_name: str = CONFIG['document_processing'].get('embedding_model', 'all-MiniLM-L6-v2')):
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, chunks: List[str]) -> List[np.ndarray]:
        try:
            embeddings = self.model.encode(chunks)
            logger.info(f"Generated embeddings for {len(chunks)} text chunks")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise