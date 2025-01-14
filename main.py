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
    # # Print sections with their content
    # for idx, sentence in enumerate(sentences, 1):
    #     print(f"Section {idx}:")
    #     for key, value in sentence.items():
    #         print(f"{key}: {value}")
    #     print("-" * 50)

    # 3. Example usage of system-user approach
    # conversation = ConversationInterface(
    #     system_prompt="You are an AI specialized in analyzing resumes."
    # )
    # summary = conversation.ask_for_cv_details(text)
    # print("\n--- System Response (Mock) ---")
    # print(summary)

    # 4. Example: Create CVProfile (this might be populated from user input, or from the PDF)
    # cv_profile = CVProfile(
    #     name="John Doe",
    #     level="Graduate",
    #     location="San Francisco",
    #     discipline="Computer Science",
    # )
    # logger.info(
    #     f"Created CVProfile for {cv_profile.name}, location={cv_profile.location}, discipline={cv_profile.discipline}"
    # )

    # 5. (Optional) You can persist or pass cv_profile to other services, e.g. job matching, etc.


if __name__ == "__main__":
    main()
