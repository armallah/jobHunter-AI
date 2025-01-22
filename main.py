#!/usr/bin/env python3
import sys
import logging
from config import LOG_LEVEL
from services.pdf_extractor import PDFExtractor
from services.text_processor import SentenceProcessor, Processor, SectionProcessor
from conversation_interface import CVProfileFiller
from models.cv_profile import CVProfile


def main():
    # Configure logging
    logging.basicConfig(
        level=LOG_LEVEL, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    # Quick arg check
    if len(sys.argv) < 2:
        logger.error("Please provide a path to a PDF file.")
        sys.exit(1)

    pdf_path = sys.argv[1]
    logger.info(f"Starting PDF parse pipeline for: {pdf_path}")

    # 1. Extract PDF
    extractor = PDFExtractor(pdf_path)
    extractor.load_pdf()

    metadata = extractor.extract_metadata()
    logger.info(f"Extracted PDF metadata: {metadata}")

    text = extractor.extract_text()
    logger.info("Successfully extracted PDF text.")

    # 2. Process text
    # processor = SentenceProcessor()
    processor = SectionProcessor()
    sections = processor.tokenise(text)
    logger.info(f"Number of sections extracted: {len(sections)}")

    # 2) Pass sections to LLM to fill CVProfile
    filler = CVProfileFiller()
    cv_profile: CVProfile = filler.fill_cv_profile(sections)

    print("CV PROFILE FIELDS:")
    print(cv_profile)

    scraper = LinkedInJobScraper(cv_profile, "armallah19782@gmail.com", "", headless=False)
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
