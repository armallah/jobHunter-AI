import logging
from pypdf import PdfReader
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PDFExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self._pdf_reader: Optional[PdfReader] = None

    def load_pdf(self) -> None:
        try:
            # with open(self.pdf_path, "rb") as f:
            self._pdf_reader = PdfReader(self.pdf_path)
            logger.info(f"Successfully loaded PDF: {self.pdf_path}")
        except FileNotFoundError:
            logger.error(f"File not found: {self.pdf_path}")
            raise
        except Exception as e:
            logger.error(f"Error while loading PDF: {e}")
            raise

    def extract_metadata(self) -> Dict[str, Any]:
        if not self._pdf_reader:
            raise ValueError("PDF must be loaded before extracting metadata.")

        pdf_meta = self._pdf_reader.metadata
        logger.debug(f"Extracted PDF metadata: {pdf_meta}")

        return {
            "author": pdf_meta.author,
            "subject": pdf_meta.subject,
            "title": pdf_meta.title,
            "number_of_pages": len(self._pdf_reader.pages)
            if self._pdf_reader.pages
            else 0,
        }

    def extract_text(self) -> str:
        if not self._pdf_reader:
            raise ValueError("PDF must be loaded before extracting text.")

        text_pages = []
        for page in self._pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_pages.append(page_text)

        full_text = "\n".join(text_pages)
        logger.debug("Successfully extracted text from PDF.")
        return full_text
