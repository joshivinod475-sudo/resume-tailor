"""Resume structure shared by the YAML input, Claude's output and the renderers."""
from pydantic import BaseModel


class Contact(BaseModel):
    email: str
    phone: str
    location: str
    linkedin: str
    github: str


class SkillGroup(BaseModel):
    category: str
    items: list[str]


class Job(BaseModel):
    title: str
    company: str
    location: str
    dates: str
    bullets: list[str]


class Project(BaseModel):
    name: str
    description: str
    link: str


class Education(BaseModel):
    degree: str
    school: str
    dates: str


class Resume(BaseModel):
    name: str
    headline: str
    contact: Contact
    summary: str
    skills: list[SkillGroup]
    experience: list[Job]
    projects: list[Project]
    education: list[Education]


class Tailored(BaseModel):
    """What Claude returns: the rewritten resume plus an honest report."""
    job_title: str
    company: str
    resume: Resume
    gaps: list[str]
    change_notes: list[str]
