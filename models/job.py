from dataclasses import dataclass

@dataclass
class Job:
    match: bool = False
    role: str = ""
    company: str = ""
    location: str = ""    
    description: str = ""
    link: str = ""


    def formatted_job_information(self) -> str:
        """
        formats the job information as markdown
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
