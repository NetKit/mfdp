from pydantic import BaseModel
from typing import List, Optional

from app.services import gemini
from app.core import available_roles

class ContactInformation(BaseModel):
    email: Optional[str]
    phoneNumber: Optional[str] = ""
    linkedIn: Optional[str] = ""


class WorkExperience(BaseModel):
    jobTitle: str
    achievments: Optional[List[str]] = []
    company: str
    location: Optional[str] = ""
    startDate: str
    endDate: Optional[str]


class Resume(BaseModel):
    fullName: str
    summary: Optional[str]
    seniority: Optional[str]
    about: Optional[str] = ""
    role: Optional[str]
    title: Optional[str]
    experience_years: Optional[int]
    contactInformation: Optional[ContactInformation]
    workExperience: Optional[List[WorkExperience]]
    education: Optional[str]
    skills: Optional[List[str]]
    languages: Optional[List[str]]


class ResumeExtractor:
    def __init__(self):
        self.prompt = f"""
You are an exper HR.
You are given a resume. You need to extract contact information, education, work experience, skills, languages and add summary of resume. 
Detect spoken languages in which candidate is proficient like English, Russian etc. This field is not for programming languages.
If resume contains about section extract it without modifications
Add summary of the resume
Education is a highest level of education mentioned in the resume. Must be one from bachelors, masters, phd. If no university level education mentioned omit field
In each working experience write achievments if they are specified
Infere which role this person is seeking with this resume.
Example roles: Backend Engineer, Fronted Engineer, ML Engineer, Tech Support
Infere seniority level. Choose one from intern, junior, middle, senior, director
Calculate years of experience
Infere job title from resume
Try to select role from list {available_roles}
"""
        self.response_schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "role": {"type": "string"},
                "experience_years": {"type": "integer"},
                "seniority": {"type": "string"},
                "about": {"type": "string"},
                "summary": {"type": "string"},
                "fullName": {"type": "string"},
                "contactInformation": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                        },
                        "phoneNumber": {"type": "string"},
                        "linkedIn": {
                            "type": "string",
                        },
                    },
                },
                "workExperience": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "jobTitle": {"type": "string"},
                            "achievments": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                },
                            },
                            "company": {"type": "string"},
                            "location": {"type": "string"},
                            "startDate": {
                                "type": "string",
                            },
                            "endDate": {
                                "type": "string",
                            },
                            "technologiesUsed": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                    },
                },
                "education": {
                    "type": "string",
                },
                "skills": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
                "languages": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
            },
        }

    async def extract(self, path: str) -> Optional[Resume]:
        response = await gemini.file_request(
            self.prompt, path, temperature=0, json_schema=self.response_schema
        )

        return Resume.model_validate_json(response)


extractor = ResumeExtractor()
