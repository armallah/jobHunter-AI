import logging
import json
import openai

# from langchain.chat_models import ChatOpenAI
from dataclasses import asdict
from typing import List
from langchain_openai import ChatOpenAI

from scripts.profile_prompt import build_cv_prompt
from models.cv_profile import CVProfile

import getpass
import os
# from dotenv import find_dotenv, load_dotenv


logger = logging.getLogger(__name__)


class CVProfileFiller:
    """
    Uses a LangChain LLM to fill out CVProfile from sectioned CV text.
    """

    def __init__(self, api_key: str = "", temperature: float = 0.0):
        """
        Example usage with an OpenAI-based LLM.
        """

        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        elif not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = getpass.getpass(
                "Enter your OpenAI API key: "
            )

        self.llm = ChatOpenAI(
            temperature=temperature,
            model="gpt-4o",
            max_retries=2,
            timeout=None,
            model_kwargs={"response_format": {"type": "json_object"}},
        )

    def fill_cv_profile(self, sections: List[dict]) -> CVProfile:
        """
        1) Build a prompt from the CV sections
        2) Get LLM response as JSON
        3) Parse into CVProfile
        """
        # Build the prompt from the sections
        prompt = build_cv_prompt(sections)

        # Convert the ChatPromptTemplate to a list of messages
        messages = prompt.format_messages()

        # Call the LLM
        response = self.llm.invoke(messages)

        # We'll try to parse JSON from the response
        # print("\n\n\n", response)

        import re

        raw_content = response.content
        cleaned_content = re.sub(
            r"^```(?:json)?|```$", "", raw_content.strip(), flags=re.MULTILINE
        )

        try:
            result_data = json.loads(cleaned_content)
        except json.JSONDecodeError:
            logger.error("Couldn't parse JSON from LLM output.")
            return CVProfile()  # or handle the error

        # Convert the JSON into a CVProfile
        # We assume the LLM used exactly the same keys we asked for
        cv_profile = CVProfile(
            name=result_data.get("name", ""),
            level=result_data.get("level", ""),
            location=result_data.get("location", ""),
            discipline=result_data.get("discipline", ""),
            secondary_discipline=result_data.get("secondary_discipline", ""),
            grade=result_data.get("grade", ""),
            school=result_data.get("school", ""),
            qual=result_data.get("qual", ""),
            experience=result_data.get("experience", ""),
            skills=result_data.get("skills", ""),
            s_info=result_data.get("s_info", ""),
            min_salary=float(result_data.get("min_salary", float("-inf"))),
            max_salary=float(result_data.get("max_salary", float("inf"))),
        )

        return cv_profile
