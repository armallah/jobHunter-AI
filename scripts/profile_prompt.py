from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from typing import List

# template that instructs LLM on how to parse CV sections

SYS_TEMPALTE = """

You are an AI assistant. The user has provided sections from a candidate's CV.
Please very carefully analyse the text and extract the following fields:

name: (STRING: candidate's full name, or empty if none found)
level: (STRING:  e.g. 'entry', 'junior', 'mid-level', 'senior', or empty, try to predict this off the greater information at hand, for example a recent graudate would be an entry level worker)
location: (STRING:  where are they based, city, region, country, or empty, e.g. London, be specific for which region in the UK)
discipline: (STRING:  their primary field of study/work, do not convolute this since it is used for searching for jobs e.g. 'Software Engineer', 'Marketing', 'Finance' etc.)
secondary_discipline: (STRING:  This is based off the disclipline but should be related, for example Computer Science -> Software Engineer, Finance -> ?)
grade: (STRING:  if a student, e.g. '1st class', '2:1', '70%', or empty. Do not include the type of degree like BSc or MEng, include the highest level of qualification)
school: (STRING:  highest institution attended, e.g. 'University of Oxford', 'King's College London', 'Chertsey High School' or empty)
qual: (STRING:  highest level of qualification recieved such BSc, BEng, MEng, Msc, PhD etc.)
skills: (STRING:  skills, technical or not, frameworks used, tools used, languages known, demonstrable qualities they hold)
experience: (INT: years of experience from first rate jobs that are relevant)
s_info: (STRING: Include as much as you can as this should be long with extra information; considered vital information that may be needed when looking for jobs)

The output must be in valid JSON

For example, this would be a good one:
CVProfile(name='REHMAN MALLAH', level='entry', location='Surrey, England', discipline='Computer Science', 
secondary_discipline='Artificial Intelligence', grade='', school="King's College London", qual='BSc', experience=1, 
skills='AWS Certified Cloud Practitioner, CompTIA A+ Certified, Python (Django, Flask, FastAPI), C, C++, Java, Scala,
Git, Docker, MS Azure, Kubernetes, Linux, HTML+ CSS, Pytorch, LangChain, SQL', s_info='British Citizen, 
requires no sponsorship. AWS Certified Cloud Practitioner and CompTIA A+ Certified. Experience with cloud
platforms, automation, and security testing. Developed CI/CD pipelines and managed VMs. Proficient in Python,
C, and various frameworks and tools. Completed projects in AI, web applications, and trading bots.')
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

    user_msg = HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE, input_variables=["sections"])

    return ChatPromptTemplate.from_messages([system_msg, user_msg]).partial(sections=joined_sections)
