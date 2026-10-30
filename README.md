# Resume Tailor

Tailors your resume to a specific job description with Claude, scores it
against the job's keywords the way an ATS would, and exports a clean,
ATS-friendly Word file. It rewrites and reorders what you've already done
and **never invents experience**: an integrity check blocks the output if it
does.

```
$ python main.py jobs/sample_job.txt
Job mentions 42 tracked keywords: python, sql, apollo, hubspot, clay, ...

Your resume now: 43% of the job's keywords

Tailoring with Claude...
Tailored resume: 71% of the job's keywords

What changed:
  - Led with the Apollo -> scoring -> sequence pipeline, the closest match to the role
  - Renamed "cold email copy" bullet to emphasise A/B testing and reply-rate metrics
  ...
Gaps (the job wants these, your resume doesn't show them):
  - No hands-on Clay or n8n experience
  - No Salesforce experience
  ...
Saved output/Alex_Morgan_Northwind_Labs.docx
```
*(Illustrative output: the exact numbers and notes depend on your resume and the job.)*

## How it works

1. **Master resume.** You keep everything you've done in `resume.yaml`
   once. Each tailored version is picked from it.
2. **Keyword analysis.** The job description is scanned for ~150 tracked
   skills and tools across engineering, data, AI and GTM. Coverage is measured
   before and after tailoring.
3. **Tailoring (Claude Opus 5.5).** Claude rewrites the headline and summary,
   reorders and rephrases bullets in the job's vocabulary, and reorders skills
   and projects by relevance. Structured output guarantees a valid resume
   object back.
4. **Integrity check.** Job titles, companies, dates, education, contact
   details and project names are compared with your original. Any change, or
   any added project, blocks the save.
5. **Gap report.** Requirements you don't meet are listed, so you know what
   to learn or address in a cover letter rather than keyword-stuff.
6. **Export.** Single-column `.docx` with standard headings and no tables or
   text boxes, which parse reliably in ATS systems.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env        # add your ANTHROPIC_API_KEY
```

Edit `resume.yaml` with your own details (the included one is a sample).

## Usage

```bash
python main.py jobs/sample_job.txt              # tailor and save a .docx to output/
python main.py jobs/sample_job.txt --offline    # keyword report only, no API key needed
python main.py path/to/job.txt --resume me.yaml --effort medium
python -m unittest discover -s tests -t .
```

Save each job description you're applying to as a text file in `jobs/`.

## Project layout

| File | Purpose |
|---|---|
| `main.py` | Command-line entry point |
| `tailor/models.py` | Pydantic schema for the resume and Claude's response |
| `tailor/claude.py` | Prompt, Claude call and integrity check |
| `tailor/keywords.py` | Keyword extraction and coverage scoring |
| `tailor/render.py` | ATS-friendly Word export |
| `resume.yaml` | Sample master resume |
| `jobs/sample_job.txt` | Sample job description |
