"""Ask Claude to tailor the resume to one job, without inventing anything."""
import anthropic

from .models import Tailored

MODEL = "claude-opus-5-5"

SYSTEM = """You are an expert technical recruiter and resume writer.
You tailor a candidate's resume to one job description so it passes ATS
keyword filters and reads well to a hiring manager.

Hard rules (honesty):
- Never invent employers, job titles, dates, degrees, projects, metrics or skills.
- Only use a keyword from the job description if the resume already shows that
  skill or a clear equivalent (e.g. resume says "Apollo.io API", job says "data enrichment").
- Keep every job's title, company, location and dates exactly as given.
- Keep contact details and education exactly as given.

What you may do:
- Rewrite the headline and summary for this role.
- Reorder and rephrase bullets to lead with the most relevant work, using the
  job's vocabulary where it is truthful. Keep numbers exactly as given.
- Reorder skill groups and skills; drop skills irrelevant to this job.
- Reorder projects by relevance.

Also return:
- job_title and company from the job description ("" if not stated).
- gaps: requirements in the job the resume does not show. Be specific and honest.
- change_notes: short list of what you changed and why."""


def tailor(resume, job_text, effort="high"):
    client = anthropic.Anthropic()
    response = client.beta.messages.parse(
        model=MODEL,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        system=SYSTEM,
        output_config={"effort": effort},
        output_format=Tailored,
        messages=[{
            "role": "user",
            "content": f"<resume>\n{resume.model_dump_json(indent=2)}\n</resume>\n\n"
                       f"<job_description>\n{job_text}\n</job_description>",
        }],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("Claude declined this request; try a different job description.")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Response was cut off; try a shorter resume or job description.")
    return response.parsed_output


def integrity_check(original, tailored):
    """List anything Claude changed that it was told to keep. Empty list means all good."""
    problems = []
    key = lambda j: (j.title, j.company, j.dates)
    if sorted(map(key, original.experience)) != sorted(map(key, tailored.experience)):
        problems.append("job titles, companies or dates were changed")
    if original.contact != tailored.contact or original.name != tailored.name:
        problems.append("contact details were changed")
    if original.education != tailored.education:
        problems.append("education was changed")
    original_projects = {p.name for p in original.projects}
    if any(p.name not in original_projects for p in tailored.projects):
        problems.append("a project was added that isn't in your resume")
    return problems
