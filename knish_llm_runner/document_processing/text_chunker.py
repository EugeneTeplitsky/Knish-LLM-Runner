from typing import List
from ..utils.logging import setup_logging

logger = setup_logging(__name__, 'document_processing')


def check_nltk_availability():
    try:
        import nltk
        nltk.download('punkt_tab')
        nltk.data.find('tokenizers/punkt')
        return True
    except (ImportError, LookupError):
        logger.warning("NLTK punkt tokenizer not available. Using fallback method.")
        return False


class TextChunker:
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.nltk_available = check_nltk_availability()

    def chunk_text(self, text: str) -> List[str]:
        if self.nltk_available:
            try:
                return self._chunk_text_nltk(text)
            except Exception as e:
                logger.warning(f"Error using NLTK tokenizer: {str(e)}. Falling back to basic method.")
                return self._chunk_text_fallback(text)
        else:
            return self._chunk_text_fallback(text)

    def _chunk_text_nltk(self, text: str) -> List[str]:
        import nltk
        sentences = nltk.sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_chunk_size = 0

        for sentence in sentences:
            sentence_size = len(sentence)
            if current_chunk_size + sentence_size > self.chunk_size:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = current_chunk[-self._calculate_overlap_sentences():]
                    current_chunk_size = sum(len(s) for s in current_chunk)
                else:
                    chunks.append(sentence[:self.chunk_size])
                    current_chunk = []
                    current_chunk_size = 0

            current_chunk.append(sentence)
            current_chunk_size += sentence_size

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        logger.info(f"Text split into {len(chunks)} chunks using NLTK")
        return chunks

    def _chunk_text_fallback(self, text: str) -> List[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            if end < len(text):
                # Try to find the last period or newline to end the chunk
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                end = start + max(last_period, last_newline) + 1 if max(last_period, last_newline) > 0 else end
            chunks.append(text[start:end])
            start = end - self.overlap

        logger.info(f"Text split into {len(chunks)} chunks using fallback method")
        return chunks

    def _calculate_overlap_sentences(self):
        return max(1, self.overlap // 100)  # Assuming average sentence length of 100 characters
