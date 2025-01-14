from dataclasses import dataclass


@dataclass
class Job:
    role: str = ""
    company: str = ""
    location: str = ""
    link: str = ""
    apply_method: str = ""
    description: str = ""
    summarize_job_description: str = ""
    recruiter_link: str = ""
    resume_path: str = ""
    cover_letter_path: str = ""

    def formatted_job_information(self) -> str:
        """
        Formats the job information as markdown
        """

        return f"""
        Job Description
        Job Information 
        - Position: {self.role}
        - At: {self.company}
        - Location: {self.location}
        - Recruiter Profile: {self.recruiter_link or "Not available"}
        
        Description
        {self.description or "No description provided."}
        """.strip()
