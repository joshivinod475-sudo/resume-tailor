"""Tailor your resume to a job description with Claude, honestly.

  python main.py jobs/sample_job.txt                 tailor + save a .docx
  python main.py jobs/sample_job.txt --offline       keyword match report only, no API key
  python main.py jobs/sample_job.txt --resume me.yaml
"""
import argparse
import re
from pathlib import Path

import yaml
from dotenv import load_dotenv

from tailor import keywords
from tailor.models import Resume
from tailor.render import to_docx


def report(label, resume, job_kw):
    pct, _, missing = keywords.coverage(resume, job_kw)
    print(f"{label}: {pct}% of the job's keywords")
    return missing


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("job", help="text file containing the job description")
    parser.add_argument("--resume", default="resume.yaml", help="your master resume (YAML)")
    parser.add_argument("--offline", action="store_true", help="keyword report only, no Claude call")
    parser.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh"])
    args = parser.parse_args()

    resume = Resume.model_validate(yaml.safe_load(Path(args.resume).read_text(encoding="utf-8")))
    job_text = Path(args.job).read_text(encoding="utf-8")
    job_kw = keywords.job_keywords(job_text)
    print(f"Job mentions {len(job_kw)} tracked keywords: {', '.join(job_kw)}\n")

    missing = report("Your resume now", resume, job_kw)
    if args.offline:
        print(f"Missing: {', '.join(missing) or 'nothing'}")
        print("\nOnly add a missing keyword if you genuinely have that skill.")
        return

    from tailor.claude import integrity_check, tailor  # only needs anthropic when used

    print("\nTailoring with Claude...")
    result = tailor(resume, job_text, effort=args.effort)
    tailored = result.resume

    problems = integrity_check(resume, tailored)
    if problems:
        print("\n! Integrity check failed, not saving: " + "; ".join(problems))
        return

    missing = report("Tailored resume", tailored, job_kw)

    print("\nWhat changed:")
    for note in result.change_notes:
        print(f"  - {note}")
    print("\nGaps (the job wants these, your resume doesn't show them):")
    for gap in result.gaps or ["none"]:
        print(f"  - {gap}")

    Path("output").mkdir(exist_ok=True)
    slug = re.sub(r"\W+", "_", f"{resume.name} {result.company or Path(args.job).stem}").strip("_")
    path = to_docx(tailored, Path("output") / f"{slug}.docx")
    print(f"\nSaved {path}")


if __name__ == "__main__":
    main()
