import logging
import json
from typing import List

from scripts.profile_prompt import build_cv_prompt
from models.cv_profile import CVProfile
import getpass
import os
import re
from openai import OpenAI
from dotenv import find_dotenv, load_dotenv


logger = logging.getLogger(__name__)


class CVProfileFiller:
    #uses a LangChain LLM to fill out CVProfile from sectioned CV text

    def __init__(self, api_key: str = "", temperature: float = 0.0):

        load_dotenv(find_dotenv())

        # Get the API key from the environment
        # Deepseek reasoner is 98x cheaper than OpenAi reasoner - omit base_url to use o1 OpenAi api
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if self.api_key is None:
            self.api_key = getpass.getpass("Enter your DEEPSEEK API key: ")
        self.temperature = temperature

        # create single client
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")

    def fill_cv_profile(self, sections: List[dict]) -> CVProfile:
        #build a prompt from the CV sections, get the llm response as json and parse into cvprofile class
        
        # Build the prompt from the sections
        prompt = build_cv_prompt(sections)
        messages = prompt.format_messages()

        res = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": m.content} for m in messages
            ],
            temperature=0.1,
        )

        raw_content = res.choices[0].message.content
        result_data = self.__clean_response__(raw_content)
        
        # Convert the JSON into a CVProfile
        # We assume the LLM used exactly the same keys we asked for
        
        return CVProfile(
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

    def __clean_response__(self, raw_content: str) -> dict:
        # clean content from response by removing ```json``` tags to allow for json parsing
        cleaned_content = re.sub(
            r"^```(?:json)?|```$", "", raw_content.strip(), flags=re.MULTILINE
        )

        try:
            return json.loads(cleaned_content)
        except json.JSONDecodeError:
            logger.error("Couldn't parse JSON from LLM output.")
            return CVProfile()  # or handle the error

