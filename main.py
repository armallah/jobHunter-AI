#!/usr/bin/env python3
import sys
import logging

from config import LOG_LEVEL
from services.pdf_extractor import PDFExtractor
from services.text_processor import SectionProcessor
from conversation_interface import CVProfileFiller
from nav.navigation import LinkedInJobScraper

def main() -> None:
    logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
    logger = logging.getLogger(__name__)

    if len(sys.argv) < 2:
        logger.error("Please provide a path to a PDF file.")
        sys.exit(1)

    pdf_path = sys.argv[1]
    logger.info(f"Starting PDF parse pipeline for: {pdf_path}")

    extractor = PDFExtractor(pdf_path)
    extractor.load_pdf()
    metadata = extractor.extract_metadata()
    logger.info(f"Extracted PDF metadata: {metadata}")

    text = extractor.extract_text()
    logger.info("Successfully extracted PDF text.")

    processor = SectionProcessor()
    sections = processor.tokenise(text)
    logger.info(f"Number of sections extracted: {len(sections)}")

    filler = CVProfileFiller()
    cv_profile = filler.fill_cv_profile(sections)
    print(cv_profile)

    scraper = LinkedInJobScraper(cv_profile, "armallah19782@gmail.com", "pass", headless=False)
    scraper.run()

if __name__ == "__main__":
    main()

"""
Possible next steps:
1. Add argument parsing for username/password or store them in a safe config.
2. Expand error handling for PDF extraction or scraping steps.
3. Integrate with a database or logging system for better reporting.

c
"""
