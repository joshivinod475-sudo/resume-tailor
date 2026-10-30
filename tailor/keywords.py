"""Measure how well a resume covers a job description's keywords (what ATS filters look for)."""
import re

SKILLS = [
    # languages and data
    "python", "sql", "javascript", "typescript", "java", "golang", "bash", "excel", "google sheets",
    "pandas", "numpy", "etl", "data analysis", "data modeling", "dashboards", "looker", "tableau",
    "power bi", "bigquery", "snowflake", "postgresql", "mysql", "mongodb", "dbt", "airflow",
    # engineering
    "api", "rest", "graphql", "webhooks", "git", "github", "github actions", "ci/cd", "docker",
    "kubernetes", "aws", "gcp", "azure", "linux", "testing", "unit tests", "fastapi", "flask",
    "django", "react", "node.js", "selenium", "web scraping", "automation", "scripting",
    # ai
    "llm", "llms", "ai", "machine learning", "nlp", "prompt engineering", "openai", "claude",
    "anthropic", "langchain", "rag", "agents", "ai agents", "voice ai", "chatbots", "fine-tuning",
    # gtm / revops
    "gtm", "go-to-market", "revops", "revenue operations", "sales operations", "marketing operations",
    "lead generation", "lead scoring", "outbound", "cold email", "email sequences", "prospecting",
    "enrichment", "data enrichment", "icp", "segmentation", "personalization", "a/b testing",
    "crm", "salesforce", "hubspot", "apollo", "apollo.io", "saleshandy", "outreach", "salesloft",
    "clay", "zapier", "make.com", "n8n", "workflow automation", "pipeline", "attribution", "funnel",
    "conversion", "deliverability", "b2b", "saas", "kpis", "metrics", "analytics",
    # soft / process
    "stakeholder management", "cross-functional", "project management", "agile", "documentation",
    "communication", "experimentation", "problem solving",
]


def _find(terms, text):
    text = text.lower()
    return [t for t in terms if re.search(rf"(?<![\w-]){re.escape(t)}(?![\w-])", text)]


def job_keywords(job_text):
    """Skills from our list that the job description mentions."""
    return _find(SKILLS, job_text)


def resume_text(resume):
    """Flatten a Resume into plain text for matching."""
    parts = [resume.headline, resume.summary]
    parts += [item for group in resume.skills for item in group.items]
    for job in resume.experience:
        parts += [job.title, *job.bullets]
    parts += [f"{p.name} {p.description}" for p in resume.projects]
    return "\n".join(parts)


def coverage(resume, keywords):
    """Return (percent covered, matched keywords, missing keywords)."""
    if not keywords:
        return 100, [], []
    matched = _find(keywords, resume_text(resume))
    missing = [k for k in keywords if k not in matched]
    return round(100 * len(matched) / len(keywords)), matched, missing
