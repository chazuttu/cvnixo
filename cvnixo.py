import pdfplumber
import groq
import os
import json
import subprocess
import shutil

# ── Your Groq API key ─────────────────────────────────────────────────────
API_KEY = "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"

# ── Paths ─────────────────────────────────────────────────────────────────
JS_FILE = r"C:\Users\HP\Desktop\generate_resume.js"

client = groq.Groq(api_key=API_KEY)

def read_resume(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def analyze_and_tailor(resume_text, job_description):
    prompt = f"""
You are an expert ATS resume specialist and career coach.

Analyze the resume against the job description carefully.

Return ONLY a JSON object. No text before or after. No markdown. Just pure JSON.

{{
  "candidate_name": "full name from resume",
  "email": "email from resume or empty string",
  "phone": "phone from resume or empty string",
  "location": "city from resume or empty string",
  "linkedin": "linkedin url from resume or empty string",
  "match_score": "number between 5 and 100",
  "ats_keywords_found": "number of JD keywords found in resume",
  "ats_keywords_missing": "number of JD keywords missing from resume",
  "strong_points": [
    "matching point 1",
    "matching point 2",
    "matching point 3",
    "matching point 4",
    "matching point 5"
  ],
  "missing_skills": [
    "missing skill 1",
    "missing skill 2",
    "missing skill 3",
    "missing skill 4"
  ],
  "improvement_tips": [
    "specific actionable tip 1",
    "specific actionable tip 2",
    "specific actionable tip 3",
    "specific actionable tip 4"
  ],
  "summary": "2 to 3 sentence professional summary tailored to the job description",
  "work_experience": [
    {{
      "title": "job title exactly as in resume",
      "company": "company name exactly as in resume",
      "dates": "dates exactly as in resume",
      "location": "location exactly as in resume",
      "bullets": [
        "bullet rewritten with JD keywords",
        "bullet rewritten with JD keywords",
        "bullet rewritten with JD keywords"
      ]
    }}
  ],
  "projects": [
    {{
      "name": "project name",
      "bullets": [
        "project description bullet"
      ]
    }}
  ],
  "education": [
    {{
      "degree": "degree name exactly as in resume",
      "institution": "institution name exactly as in resume",
      "year": "year exactly as in resume",
      "cgpa": "cgpa or empty string"
    }}
  ],
  "skills_technical": ["skill1", "skill2", "skill3"],
  "skills_tools": ["tool1", "tool2", "tool3"],
  "achievements": [
    "achievement 1",
    "achievement 2",
    "achievement 3"
  ],
  "certifications": [
    "certification 1",
    "certification 2"
  ]
}}

STRICT RULES:
- Never fabricate any experience skills or education
- Only use information already present in the resume
- Rewrite bullet points using keywords from the job description
- Keep all dates company names and institutions exactly as original
- match_score minimum is 5 never return 0
- Return ONLY pure JSON nothing else

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=3500
    )
    return response.choices[0].message.content

def parse_json_response(text):
    text = text.strip()
    if "```" in text:
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        text = text[start:end]
    return json.loads(text)

def generate_documents(data, output_dir):
    temp_dir = os.environ.get("TEMP", "C:\\Temp")
    json_path = os.path.join(temp_dir, "cvnixo_data.json")
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    result = subprocess.run(
        ["node", JS_FILE, json_path, output_dir],
        capture_output=True,
        text=True
    )

    if "SUCCESS" in result.stdout:
        return True
    else:
        print("Error generating documents:")
        print(result.stderr)
        print(result.stdout)
        return False

def main():
    print("=" * 55)
    print("       Welcome to Cvnixo Resume Tailor")
    print("       AI Powered  |  ATS Optimized")
    print("=" * 55)

    resume_path = input("\nEnter full path of your resume PDF: ").strip()
    if not os.path.exists(resume_path):
        print("Resume file not found. Please check the path.")
        return

    print("\nPaste the Job Description below.")
    print("When done press Enter then type DONE and press Enter:\n")
    lines = []
    while True:
        line = input()
        if line.strip() == "DONE":
            break
        lines.append(line)

    job_description = "\n".join(lines)

    print("\nAnalyzing resume. Please wait...")

    resume_text = read_resume(resume_path)
    response = analyze_and_tailor(resume_text, job_description)

    print("Parsing results...")
    try:
        data = parse_json_response(response)
    except Exception as e:
        print(f"Parsing error: {e}")
        print("Raw response:", response[:300])
        return

    output_dir = os.path.dirname(resume_path)

    print("Creating your documents...")
    success = generate_documents(data, output_dir)

    if success:
        print("\n" + "=" * 55)
        print("SUCCESS! Your Cvnixo documents are ready.")
        print(f"ATS Match Score  : {data.get('match_score', '?')}%")
        print(f"Keywords Found   : {data.get('ats_keywords_found', '?')}")
        print(f"Keywords Missing : {data.get('ats_keywords_missing', '?')}")
        print(f"\nTwo files saved in: {output_dir}")
        print("  1. cvnixo_resume.docx   — Your tailored resume")
        print("  2. cvnixo_analysis.docx — Your ATS analysis report")
        print("=" * 55)
    else:
        print("\nSomething went wrong. Please check error above.")

if __name__ == "__main__":
    main()