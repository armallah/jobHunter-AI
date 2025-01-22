import logging
import nltk
from nltk.tokenize import sent_tokenize
from typing import List
from abc import ABC, abstractmethod
import re

from rapidfuzz import fuzz


logger = logging.getLogger(__name__)


class Processor(ABC):
    #abstract class for processing text
    @abstractmethod
    def tokenise(self):
        pass


#sentence processor class that parses pdf text into sentences with nltk, rather useless but may still have unseen perks for later
class SentenceProcessor(Processor):
    def __init__(self):
        nltk.download("punkt")
        logger.debug("NLTK punkt tokenizer downloaded (if not already).")

    def tokenise(self, text: str) -> List[str]:
        sentences = sent_tokenize(text)
        logger.debug(f"Tokenized text into {len(sentences)} sentences.")
        return sentences



#section processor class that tokenises text based off keywords, since I only want to make one LLM call before running agent
class SectionProcessor(Processor):

    #keywords to parse from, not exhaustive but should be enough for most cases especially with the fuzzy matching
    SEC_HEADINGS = [
        r"EDUCATION",
        r"EXPERIENCE",
        r"SKILLS",
        r"PROJECTS",
        r"CERTIFICATIONS",
        r"ACHIEVEMENTS",
        r"INTERESTS",
        r"CONTACT",
        r"SUMMARY",
        r"HOBBIES",
        r"LANGUAGES",
        r"REFERENCES",
        r"HISTORY",
        r"MISC",
        r"PROFESSIONAL SUMMARY",
        r"PERSONAL STATEMENT",
        r"QUALIFICATIONS",
        r"INTERESTS AND ACTIVITIES"
        r"INTEREST",
        r"ACTIVITES",
        r"ADDITIONAL INFORMATION",
        r"WORK EXPERIENCE",
        r"KEY SKILLS",
        r"SKILLS",
        r"PERSONAL PROFILE",
        r"PROFILE",
        r"QUALIFICATIONS",
        r"WORK HISTORY",
        r"VOLUNTARY EXPERIENCE",
        r"POSITIONS OF RESPONSIBILITY",
        r"TECHNICAL SKILLS",
        r"EDUCATION AND QUALIFICATIONS",
        r"Achievements",
    ]

    #regex pattern to match any of the keywords with OR | operator
    heading_pattern = r"(" + r"|".join(SEC_HEADINGS) + r")"

    def __init__(self):
        logger.debug("SectionProcessor initialised.")

    def tokenise(self, text: str) -> List[dict]:
        # self._extract_heading_cadidates omitted due to inconsistency when used aganist a diverse range of CVs
        # heading_candidates = self._extract_heading_candidates(text)
        
        #etxtract known headings from regex
        #then known duplicate headings are removed
        headings_from_regex = self._extract_known_headings(text)
        known_headings = set(headings_from_regex)

        #using known headings to split the text into sections
        sections = self._split_by_headings(text, known_headings)

        #return section for llm processing
        return sections

    #not used due to inconsistency
    def _extract_heading_candidates(self, text: str) -> List[str]:
        #split the text into tokens, these tokens are split based on guesswork on the number of spaces between them
        #this avoids splitting on text that is not a heading since headings are usually separated by a large number of spaces or \n
        tokens = re.split(r"\s{2,}", text)

        recognised_headings = []

        for token in tokens:
            san_token = token.strip()

            if not san_token or len(san_token) < 2:
                continue

            for heading in self.SEC_HEADINGS:
                #fuzzy matching to see if the token is similar to the heading
                score = fuzz.partial_ratio(san_token.lower(), heading.lower())

                if score > 80:
                    recognised_headings.append(san_token)
                    break

        return list(set(recognised_headings))

    def _extract_known_headings(self, text: str) -> List[str]:
        # Find all headings in the text using the regex pattern
        matches = re.findall(self.heading_pattern, text, flags=re.IGNORECASE)
        normalise_matches = [m.upper() for m in matches]

        return list(set(normalise_matches))

    def _split_by_headings(self, text: str, headings: set) -> List[dict]:
        # We split the text by the given set of headings (intersection).
        if not headings:
            return [{"heading": "MISC", "content": text.strip()}]

        # Build a combined regex pattern from the headings set
        safe_headings = [re.escape(h) for h in headings]
        combined_pattern = r"(" + r"|".join(safe_headings) + r")"

        # We'll split with a capturing group so we can retain which heading was matched.
        parts = re.split(combined_pattern, text, flags=re.IGNORECASE)

        sections = []

        current_heading = "MISC"
        current_content = []

        lines = text.splitlines()
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                # blank line => just accumulate it
                current_content.append(line)
                continue

            # Check if the line is (almost) exactly a heading.
            # We'll do a quick check: uppercase the line, then check if in set
            # or if it's fuzzy close to a heading in `headings`.
            line_upper = stripped_line.upper()

            # We can do an exact check or fuzzy. Let's do both:
            if line_upper in headings:
                # It's an exact heading line => close the old section
                if current_content:
                    sections.append(
                        {
                            "heading": current_heading,
                            "content": "\n".join(current_content).strip(),
                        }
                    )
                    current_content = []

                # Update heading
                current_heading = line_upper

            else:
                if self._is_line_fuzzy_heading_candidate(stripped_line, headings):
                    # finalize old section
                    if current_content:
                        sections.append(
                            {
                                "heading": current_heading,
                                "content": "\n".join(current_content).strip(),
                            }
                        )
                        current_content = []

                    # update heading
                    current_heading = stripped_line.upper()
                else:
                    # just normal content
                    current_content.append(line)

        # end of file => finalize last chunk
        if current_content:
            sections.append(
                {
                    "heading": current_heading,
                    "content": "\n".join(current_content).strip(),
                }
            )

        # Remove empty content if needed
        final_sections = [sec for sec in sections if sec["content"]]
        return final_sections

    def _is_line_fuzzy_heading_candidate(self, line: str, headings: set) -> bool:
        # Fallback fuzzy match for lines that are near a heading but not exactly spelled the same.
        words = line.split()
        # If it's too long, let's assume it's not a heading
        if len(words) > 5:
            return False

        # Fuzzy match against each heading in the set
        for h in headings:
            score = fuzz.ratio(line.lower(), h.lower())
            if score > 80:
                return True
        return False
