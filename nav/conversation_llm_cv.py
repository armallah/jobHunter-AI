import json
from .job_prompt import check_job_with_cv
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

import getpass
import os
import re

class JobChecker:
    def __init__(self, temperature: float = 0.0):
        """
        Initialize the JobChecker with an API key and optional temperature, api_key is loaded from env variables. 
        export DEEPSEEK_API_KEY=your_api_key on linux, set DEEPSEEK_API_KEY=your_api_key on windows
        or enter maurually when prompted
        """
        # Load environment variables from a .env file one directory up
        load_dotenv(find_dotenv())

        # Get the API key from the environment
        # Deepseek reasoner is 98x cheaper than OpenAi reasoner - omit base_url to use o1 OpenAi api
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if self.api_key is None:
            self.api_key = getpass.getpass("Enter your DEEPSEEK API key: ")
        self.temperature = temperature

        # create single client
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")


    def check_job(self, cv_profile, joblisting):
        
        propmt = check_job_with_cv(cv_profile, joblisting)

        messages = propmt.format_messages()
        systemcontent, usercontent = messages[0].content, messages[1].content        
        
        response = self.client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "user", "content": systemcontent + usercontent},
            ]
        )
        
        raw_content = response.choices[0].message.content
        result_data = self.__clean_response__(raw_content)
    
        # print(result_data)
        return result_data

    def __clean_response__(self, raw_content):
        # clean content from response by removing ```json``` tags to allow for json parsing
        cleaned_content = re.sub(
            r"^```(?:json)?|```$", "", raw_content.strip(), flags=re.MULTILINE
        )

        try:
            return json.loads(cleaned_content)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None

