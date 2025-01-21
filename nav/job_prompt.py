from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from typing import List

# template that instructs LLM on how to parse CV sections

SYS_TEMPLATE = """
You are an AI assistant. You are going to be given a Job listing and a candidate's CV.
From this you must deduce whether the candidate is a good fit for the job. For example they should
have certain skills, have the right education level, similar experience and more. It is important to note
that you can only use the information provided in the job listing and the CV to make your decision, and that
you should be lenient in your judgement. 

For example, a job listing in Software Engineering at entry level with understanding of Python but not necessarily required would match 
with a candidate who has a degree in Computer Science, has experience in Java.

However, a job listing in Software Engineering at entry level who want Bachelor graduates would not match
with a candidate who has  has experience in Python but with no degree in Computer Science.

Ideally, you wouuld want a good level match, due to variance you can match entry-level with associate jobs, but not graduate with internships for example.

For intern jobs the candidate should be a current student, for entry-level jobs the candidate should have less than 2 years of experience for senior jobs the candidate should have 5+ years of experience.

You will be given the candidate information in the following format, and then the job listing in a markdown format.

name: (STRING: candidate's full name, or empty if none found)
level: (STRING:  e.g. 'entry', 'junior', 'mid-level', 'senior', or empty, try to predict this off the greater information at hand, for example a recent graudate would be an entry level worker)
location: (STRING:  where are they based, city, region, country, or empty, e.g. London, be specific for which region in the UK)
discipline: (STRING:  their primary field of study/work, do not convolute this since it is used for searching for jobs e.g. 'Computer Science', 'Marketing', 'Finance' etc.)
secondary_discipline: (STRING:  This is based off the disclipline but should be related, for example Computer Science -> Software Engineer, Finance -> ?)
grade: (STRING:  if a student, e.g. '1st class', '2:1', '70%', or empty. Do not include the type of degree like BSc or MEng, include the highest level of qualification)
school: (STRING:  highest institution attended, e.g. 'University of Oxford', 'King's College London', 'Chertsey High School' or empty)
qual: (STRING:  highest level of qualification recieved such BSc, BEng, MEng, Msc, PhD etc.)
skills: (STRING:  skills, technical or not, frameworks used, tools used, languages known, demonstrable qualities they hold)
experience: (INT: years of experience from first rate jobs that are relevant)
s_info: (STRING: extra information, this should be long and considered vital information that may be needed when looking for jobs)

The output must be in valid JSON

"match": "True" or "False" depending on whether the candidate is a good fit for the job
"role" : "role name" e.g Software Engineer,
"company" : "company name" e.g Google,
"location" : "location of the job" e.g London,
"description" : "description of the job", e.g python software engineering role entry-level
"""

HUMAN_TEMPLATE = """
Below are the sections extracted from the candidate's CV

{sections}

And here is the job listing:

{job_listing}

Please return the JSON object with all required fields. No extra commentary.

"match": "True" or "False" depending on whether the candidate is a good fit for the job
"role" : "role name" e.g Software Engineer,
"company" : "company name" e.g Google,
"location" : "location of the job" e.g London,
"description" : "description of the job", e.g python software engineering role entry-level
"""

# TODO: Change this so everything other than match is scraped from the job listing, will save heavily on output tokens cost.
def check_job_with_cv(cvprofile, joblisting) -> ChatPromptTemplate:

    system_msg = SystemMessagePromptTemplate.from_template(SYS_TEMPLATE)

    # format CV data in structured way
    cv_format = f"""
    name: {cvprofile.name}
    level: {cvprofile.level}
    location: {cvprofile.location}
    discipline: {cvprofile.discipline}
    secondary_discipline: {cvprofile.secondary_discipline}
    grade: {cvprofile.grade}
    school: {cvprofile.school}
    qual: {cvprofile.qual}
    skills: {cvprofile.skills}
    experience: {cvprofile.experience}
    s_info: {cvprofile.s_info}
    """

    user_msg = HumanMessagePromptTemplate.from_template(
        HUMAN_TEMPLATE, input_variables=["sections", "job_listing"]
    )

    return ChatPromptTemplate.from_messages([system_msg, user_msg]).partial(
        sections=cv_format,
        job_listing=joblisting
    )
