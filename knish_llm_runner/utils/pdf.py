from pypdf import PdfReader

from knish_llm_runner.utils.logging import setup_logging

logger = setup_logging(__name__, 'pdf')


def process_pdf(file_path: str) -> str:
    """
    Process a PDF file and extract its text content.
    """
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            content = []
            for page in pdf_reader.pages:
                content.append(page.extract_text())

        full_content = "\n".join(content)
        logger.info(f"Successfully extracted text from PDF: {file_path}")
        return full_content
    except Exception as e:
        logger.error(f"Error processing PDF {file_path}: {str(e)}")
        raise
