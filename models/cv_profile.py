from dataclasses import dataclass
from typing import Optional


@dataclass
class CVProfile:
    """
    dataclass representing metadata about a CV candidate.
    You can expand this as needed.
    """

    name: str = ""  # Full name
    level: str = ""  # "entry", "immediate", "mid-level", etc.
    location: str = ""  # e.g. "London" "Surrey"
    discipline: str = ""  # e.g. "Computer science" "Mehanical engineering" "PPE"
    secondary_discipline: str = ""  # e.g. "Retail", "Support Engineer"
    grade: str = ""  # e.g What grade at University (i.e 2:1, 1st class, 70% etc.) Do not include the tpye of degree
    school: str = ""  # e.g. Which university did they attend, choose highest qualification university if there are more than one, if none put highest level of education
    s_info: str = (
        ""  # e.g. Important information that may be needed when looking for jobs
    )
    min_salary: float = float("-inf")
    max_salary: float = float("inf")

    def __post_init__(self):
        # You can add post-initialization validation or processing here
        pass
