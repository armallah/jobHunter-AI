from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from typing import List

# Template that instructs LLM on how to parse CV sections

SYS_TEMPALTE = """

You are an AI assistant. The user has provided sections from a candidate's CV.
Please carefully analySe the text and extract the following fields:


name: (STRING: candidate's full name, or empty if none found)
level: (STRING:  e.g. 'entry', 'junior', 'mid-level', 'senior', or empty, try to predict this off the greater information at hand, for example a recent graudate would be an entry level worker)
location: (STRING:  where are they based, city, region, country, or empty, e.g. London, be specific for which region in the UK)
discipline: (STRING:  their primary field of study/work, e.g. 'Computer Science', 'Marketing', 'Finance' etc.)
secondary_discipline: (STRING:  any secondary area of expertise, if relevant)
grade: (STRING:  if a student, e.g. '1st class', '2:1', '70%', or empty. Do not include the type of degree like BSc or MEng, include the highest level of qualification)
school: (STRING:  highest institution attended, e.g. 'University of Oxford', 'King's College London', 'Chertsey High School' or empty)
qual: (STRING:  highest level of qualification recieved such BSc, BEng, MEng, Msc, PhD etc.)
skills: (STRING:  skills, technical or not, frameworks used, tools used, languages known, demonstrable qualities they hold)
experience: (INT: Include years of experience from first rate jobs that are relevant, for example you would include a graduate financial analysts but not a retail job for a finance major)
s_info: (STRING: This is quite critical to include, it's important extra information that will be relevant for job searching, such as certificates (e.g CompTIA A+) e.g. ''visa status', 'additional skills', or 'requires sponsorship' Ideally you would want this to be a few sentences long or more, something that could be used to match with job listings, so make it detailed)
If the CV does not contain some fields, output them as empty or default.

Output must be valid JSON with keys exactly as:
name, level, location, discipline, secondary_discipline, grade, school, experience, s_info
"""

HUMAN_TEMPLATE = """
Below are the sections extracted from the candidate's CV, Please note the heading may not be strictly relevant on the information proceeding it:

{sections}

Please return the JSON object with all required fields. No extra commentary.
"""


def build_cv_prompt(sections: List[dict]) -> ChatPromptTemplate:
    system_msg = SystemMessagePromptTemplate.from_template(SYS_TEMPALTE)

    formatted_sections = []

    for i, c in enumerate(sections, 1):
        heading = c.get("heading", "MISC")
        content = c.get("content", "")
        formatted_sections.append(f"Section {i} ({heading}):\n{content}\n")

    joined_sections = "\n".join(formatted_sections)

    user_msg = HumanMessagePromptTemplate.from_template(
        HUMAN_TEMPLATE, input_variables=["sections"]
    )

    return ChatPromptTemplate.from_messages([system_msg, user_msg]).partial(
        sections=joined_sections
    )
