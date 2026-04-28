import streamlit as st
import groq
import pdfplumber
import requests
from bs4 import BeautifulSoup
import io
import os
import json
import re
import subprocess
import tempfile
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIG — ADD YOUR KEYS HERE
# ─────────────────────────────────────────────
GROQ_API_KEY     = st.secrets.get("GROQ_API_KEY", "")
RAZORPAY_BASIC   = st.secrets.get("RAZORPAY_BASIC", "#")
RAZORPAY_PRO     = st.secrets.get("RAZORPAY_PRO", "#")
RAZORPAY_YEARLY  = st.secrets.get("RAZORPAY_YEARLY", "#")
EMAIL_DB_FILE    = "used_emails.json"

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Cvnixo — AI Resume Tailor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# PREMIUM DARK UI
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&display=swap');

:root {
    --bg:      #08080f;
    --surface: #0f0f1a;
    --card:    #13131e;
    --border:  #22223a;
    --accent:  #6c63ff;
    --accent2: #ff6584;
    --green:   #00e5a0;
    --text:    #eaeaf5;
    --muted:   #6a6a8a;
    --radius:  14px;
}

html, body, .stApp { background: var(--bg) !important; color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2.5rem !important; max-width: 1000px !important; margin: 0 auto; }
h1,h2,h3 { font-family: 'Syne', sans-serif !important; }

.hero { text-align: center; padding: 3rem 1rem 1.5rem; }
.badge {
    display: inline-block;
    background: linear-gradient(135deg,#6c63ff18,#ff658418);
    border: 1px solid #6c63ff33;
    border-radius: 100px; padding: 5px 16px;
    font-size: 11px; letter-spacing: 2px; text-transform: uppercase;
    color: var(--accent); margin-bottom: 1.2rem;
}
.hero h1 {
    font-size: clamp(2.2rem,5vw,3.5rem) !important;
    font-weight: 800 !important; line-height: 1.1 !important; margin: 0 0 .8rem !important;
    background: linear-gradient(135deg,#fff 40%,#6c63ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero p { color: var(--muted); font-size: 1rem; max-width: 480px; margin: 0 auto 2rem; line-height: 1.7; }

.card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.5rem; margin-bottom: 1rem;
    transition: border-color .2s;
}
.card:hover { border-color: #6c63ff44; }
.card-title {
    font-family: 'Syne', sans-serif; font-weight: 700; font-size: .95rem;
    color: var(--text); margin-bottom: 1rem; display: flex; align-items: center; gap: 8px;
}
.step-num {
    background: linear-gradient(135deg,var(--accent),var(--accent2));
    color: white; border-radius: 50%; width: 26px; height: 26px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; flex-shrink: 0;
}

.stFileUploader > div {
    background: var(--surface) !important; border: 2px dashed var(--border) !important;
    border-radius: 12px !important; color: var(--muted) !important;
}
.stFileUploader > div:hover { border-color: var(--accent) !important; }
.stTextArea textarea {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 12px !important; color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 14px !important;
}
.stTextArea textarea:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 2px #6c63ff22 !important; }
.stTextInput input {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--text) !important;
}
.stTextInput input:focus { border-color: var(--accent) !important; }

.stButton > button {
    background: linear-gradient(135deg,var(--accent),#8b83ff) !important;
    color: white !important; border: none !important; border-radius: 12px !important;
    padding: 13px 28px !important; font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; font-size: 15px !important; width: 100% !important;
    transition: all .2s !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 25px #6c63ff44 !important; }

.pricing-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 1rem; margin: 1.2rem 0; }
.plan {
    background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.4rem; text-align: center;
    transition: all .2s; position: relative;
}
.plan:hover { border-color: var(--accent); transform: translateY(-3px); box-shadow: 0 10px 28px #6c63ff1a; }
.plan.hot { border-color: var(--accent); background: linear-gradient(135deg,#6c63ff0d,var(--card)); }
.hot-badge {
    position: absolute; top: -11px; left: 50%; transform: translateX(-50%);
    background: linear-gradient(135deg,var(--accent),var(--accent2));
    color: white; padding: 2px 12px; border-radius: 100px;
    font-size: 10px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;
}
.plan-name { font-family:'Syne',sans-serif; font-weight:700; font-size:.85rem; color:var(--muted); text-transform:uppercase; letter-spacing:1.5px; margin-bottom:.4rem; }
.plan-price { font-family:'Syne',sans-serif; font-weight:800; font-size:1.8rem; color:var(--text); }
.plan-period { font-size:11px; color:var(--muted); margin-bottom:.8rem; }
.plan-feat { list-style:none; padding:0; margin:0 0 1rem; text-align:left; }
.plan-feat li { font-size:12px; color:var(--muted); padding:3px 0; display:flex; align-items:center; gap:6px; }
.plan-feat li::before { content:"✓"; color:var(--green); font-weight:700; }
.pay-btn {
    display:block; background:linear-gradient(135deg,var(--accent),#8b83ff);
    color:white !important; text-decoration:none !important; border-radius:9px;
    padding:9px 16px; font-family:'Syne',sans-serif; font-weight:700;
    font-size:13px; transition:all .2s; text-align:center;
}
.pay-btn:hover { box-shadow:0 5px 18px #6c63ff44; transform:translateY(-1px); }

.score-wrap { display:flex; gap:1rem; margin:1rem 0; }
.score-box {
    flex:1; background:var(--card); border:1px solid var(--border);
    border-radius:var(--radius); padding:1.2rem; text-align:center;
}
.score-val { font-family:'Syne',sans-serif; font-weight:800; font-size:2.2rem; }
.score-before { background:linear-gradient(135deg,var(--muted),#9a9aba); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.score-after  { background:linear-gradient(135deg,var(--accent),var(--green)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.score-label  { font-size:11px; color:var(--muted); margin-top:.3rem; text-transform:uppercase; letter-spacing:1px; }
.bar-wrap { background:var(--surface); border-radius:100px; height:8px; margin:.4rem 0; overflow:hidden; }
.bar { height:100%; border-radius:100px; background:linear-gradient(90deg,var(--accent),var(--green)); }

.chip { display:inline-block; background:#6c63ff18; border:1px solid #6c63ff33; color:var(--accent); border-radius:100px; padding:3px 10px; font-size:11px; margin:2px; }
.chip.miss { background:#ff658418; border-color:#ff658433; color:var(--accent2); }

.divider { height:1px; background:linear-gradient(90deg,transparent,var(--border),transparent); margin:2rem 0; }

.unlock-box {
    background: var(--card); border: 1px solid #6c63ff33;
    border-radius: var(--radius); padding: 1.5rem; margin-top: 1rem;
}

.stRadio > div { gap: 10px !important; }
.stRadio label { background:var(--surface) !important; border:1px solid var(--border) !important; border-radius:9px !important; padding:9px 14px !important; cursor:pointer !important; transition:all .15s !important; }
.stRadio label:hover { border-color:var(--accent) !important; }
label, .stRadio p { color:var(--muted) !important; font-size:13px !important; }
.stSelectbox > div > div { background:var(--surface) !important; border:1px solid var(--border) !important; border-radius:10px !important; color:var(--text) !important; }
.stTabs [data-baseweb="tab-list"] { background:var(--surface) !important; border-radius:10px !important; padding:3px !important; border:1px solid var(--border) !important; }
.stTabs [data-baseweb="tab"] { background:transparent !important; color:var(--muted) !important; border-radius:7px !important; }
.stTabs [aria-selected="true"] { background:var(--accent) !important; color:white !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def load_email_db():
    if os.path.exists(EMAIL_DB_FILE):
        with open(EMAIL_DB_FILE) as f:
            return json.load(f)
    return {}

def email_used(email):
    return email.lower() in load_email_db()

def mark_email_used(email):
    db = load_email_db()
    db[email.lower()] = datetime.now().isoformat()
    with open(EMAIL_DB_FILE, "w") as f:
        json.dump(db, f)

def read_pdf(file_bytes):
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        return "\n".join(p.extract_text() or "" for p in pdf.pages)

def fetch_jd_from_url(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script","style","nav","footer","header"]):
            tag.decompose()
        lines = [l.strip() for l in soup.get_text(separator="\n").splitlines() if l.strip()]
        return "\n".join(lines[:300])
    except:
        return None

def call_groq(resume_text, jd_text):
    client = groq.Groq(api_key=GROQ_API_KEY)
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
  "strong_points": ["point 1","point 2","point 3","point 4","point 5"],
  "missing_skills": ["skill 1","skill 2","skill 3","skill 4"],
  "improvement_tips": ["tip 1","tip 2","tip 3","tip 4"],
  "summary": "2 to 3 sentence professional summary tailored to the job description",
  "work_experience": [{{
    "title": "job title exactly as in resume",
    "company": "company name exactly as in resume",
    "dates": "dates exactly as in resume",
    "location": "location exactly as in resume",
    "bullets": ["bullet rewritten with JD keywords","bullet","bullet"]
  }}],
  "projects": [{{
    "name": "project name",
    "bullets": ["project description bullet"]
  }}],
  "education": [{{
    "degree": "degree name exactly as in resume",
    "institution": "institution name exactly as in resume",
    "year": "year exactly as in resume",
    "cgpa": "cgpa or empty string"
  }}],
  "skills_technical": ["skill1","skill2","skill3"],
  "skills_tools": ["tool1","tool2","tool3"],
  "achievements": ["achievement 1","achievement 2","achievement 3"],
  "certifications": ["certification 1","certification 2"]
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
{jd_text}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=3500
    )
    return response.choices[0].message.content

def parse_json(text):
    text = text.strip()
    if "```" in text:
        lines = [l for l in text.split("\n") if not l.strip().startswith("```")]
        text = "\n".join(lines)
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        text = text[start:end]
    return json.loads(text)

def run_node(data, output_dir):
    """Call generate_resume.js exactly like cvnixo.py does"""
    js_file = os.path.join(os.path.dirname(__file__), "generate_resume.js")
    if not os.path.exists(js_file):
        js_file = "generate_resume.js"

    temp_dir = tempfile.gettempdir()
    json_path = os.path.join(temp_dir, "cvnixo_data.json")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    result = subprocess.run(
        ["node", js_file, json_path, output_dir],
        capture_output=True, text=True
    )
    return "SUCCESS" in result.stdout, result.stderr

def simple_ats_score(resume_text, jd_text):
    jd_words   = set(re.findall(r'\b[a-zA-Z]{4,}\b', jd_text.lower()))
    res_words  = set(re.findall(r'\b[a-zA-Z]{4,}\b', resume_text.lower()))
    common     = jd_words & res_words
    score      = min(int((len(common) / max(len(jd_words), 1)) * 150), 99)
    missing    = list(jd_words - res_words)[:12]
    return max(score, 5), missing


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    "step": 1, "resume_text": None, "jd_text": None,
    "ai_data": None, "ats_before": None, "ats_after": None,
    "missing_kw": [], "plan": None, "email": None,
    "resume_bytes": None, "analysis_bytes": None
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="badge">⚡ AI Powered · ATS Optimized</div>
    <h1>Get Past the ATS.<br>Land the Interview.</h1>
    <p>Cvnixo tailors your resume to any job in 30 seconds — precise, natural, never fabricated.</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# STEP 1 — RESUME UPLOAD
# ─────────────────────────────────────────────
st.markdown('<div class="card"><div class="card-title"><span class="step-num">1</span> Upload Your Resume (PDF)</div>', unsafe_allow_html=True)
resume_file = st.file_uploader("Resume", type=["pdf"], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

if resume_file:
    file_bytes = resume_file.read()
    st.session_state.resume_text = read_pdf(file_bytes)
    st.success(f"✓ Resume loaded — {len(st.session_state.resume_text.split())} words")


# ─────────────────────────────────────────────
# STEP 2 — JOB DESCRIPTION
# ─────────────────────────────────────────────
st.markdown('<div class="card"><div class="card-title"><span class="step-num">2</span> Add the Job Description</div>', unsafe_allow_html=True)

jd_method = st.radio(
    "JD method",
    ["Paste job link (LinkedIn / Naukri / Indeed / any)", "Paste JD text directly"],
    label_visibility="collapsed", horizontal=True
)

if "link" in jd_method.lower():
    job_url = st.text_input("Job URL", placeholder="https://linkedin.com/jobs/view/...", label_visibility="collapsed")
    if job_url and st.button("🔗 Fetch Job Description", key="fetch"):
        with st.spinner("Fetching job details..."):
            fetched = fetch_jd_from_url(job_url)
        if fetched:
            st.session_state.jd_text = fetched
            st.success("✓ Job description fetched!")
        else:
            st.error("Could not fetch. Please paste the JD text directly.")
else:
    jd_raw = st.text_area("Paste full job description", height=180,
        placeholder="Paste the complete job description here...", label_visibility="collapsed")
    if jd_raw:
        st.session_state.jd_text = jd_raw

st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# STEP 3 — EMAIL + GENERATE
# ─────────────────────────────────────────────
st.markdown('<div class="card"><div class="card-title"><span class="step-num">3</span> Your Email — Get Free Tailored Resume</div>', unsafe_allow_html=True)
email_input = st.text_input("Email", placeholder="you@email.com", label_visibility="collapsed")
go = st.button("⚡ Tailor My Resume — Free")
st.markdown('</div>', unsafe_allow_html=True)

if go:
    if not st.session_state.resume_text:
        st.error("Please upload your resume first.")
    elif not st.session_state.jd_text:
        st.error("Please add the job description.")
    elif not email_input or "@" not in email_input:
        st.error("Please enter a valid email.")
    elif email_used(email_input):
        st.warning("This email has already used the free tier. Upgrade below to continue.")
        st.session_state.step = 2
    else:
        before, missing = simple_ats_score(st.session_state.resume_text, st.session_state.jd_text)
        st.session_state.ats_before = before
        st.session_state.missing_kw = missing

        with st.spinner("AI is analysing and tailoring your resume..."):
            raw = call_groq(st.session_state.resume_text, st.session_state.jd_text)

        try:
            data = parse_json(raw)
        except Exception as e:
            st.error(f"Parsing error: {e}. Please try again.")
            st.stop()

        st.session_state.ai_data = data
        after, _ = simple_ats_score(
            " ".join(data.get("skills_technical", []) + data.get("skills_tools", []) +
                     [b for job in data.get("work_experience",[]) for b in job.get("bullets",[])] +
                     [data.get("summary","")]),
            st.session_state.jd_text
        )
        st.session_state.ats_after = after
        st.session_state.email = email_input
        mark_email_used(email_input)
        st.session_state.step = 2
        st.rerun()


# ─────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────
if st.session_state.step >= 2 and st.session_state.ai_data:

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    before = st.session_state.ats_before or 0
    after  = st.session_state.ats_after  or 0

    st.markdown(f"""
    <div class="score-wrap">
        <div class="score-box">
            <div class="score-val score-before">{before}%</div>
            <div class="bar-wrap"><div class="bar" style="width:{before}%"></div></div>
            <div class="score-label">Before Tailoring</div>
        </div>
        <div class="score-box">
            <div class="score-val score-after">{after}%</div>
            <div class="bar-wrap"><div class="bar" style="width:{after}%"></div></div>
            <div class="score-label">After Tailoring · ATS Match</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.missing_kw:
        chips = "".join(f'<span class="chip miss">{w}</span>' for w in st.session_state.missing_kw)
        st.markdown(f'<div class="card"><div class="card-title">🎯 Keywords Added</div>{chips}</div>', unsafe_allow_html=True)

    # ── FREE DOWNLOAD — generate docs via Node ──
    data = st.session_state.ai_data
    out_dir = tempfile.mkdtemp()
    with st.spinner("Building your documents..."):
        ok, err = run_node(data, out_dir)

    resume_path   = os.path.join(out_dir, "cvnixo_resume.docx")
    analysis_path = os.path.join(out_dir, "cvnixo_analysis.docx")

    if ok and os.path.exists(resume_path):
        with open(resume_path, "rb") as f:
            st.session_state.resume_bytes = f.read()
        if os.path.exists(analysis_path):
            with open(analysis_path, "rb") as f:
                st.session_state.analysis_bytes = f.read()

        st.markdown("""
        <div class="card" style="border-color:#6c63ff33">
            <div class="card-title">✅ Your Documents Are Ready</div>
            <div style="color:var(--muted);font-size:13px">
                Free version includes watermark. Upgrade below for clean copy + more.
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "⬇ Download Resume (Free)",
                data=st.session_state.resume_bytes,
                file_name="cvnixo_resume_free.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        with col2:
            st.download_button(
                "⬇ Download ATS Report (Free)",
                data=st.session_state.analysis_bytes or b"",
                file_name="cvnixo_analysis_free.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    else:
        st.warning("Document generation needs Node.js on the server. Your AI analysis is complete — upgrade to get your documents.")

    # ── PRICING ──
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;margin-bottom:1.2rem">
        <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800">Unlock Full Power</div>
        <div style="color:var(--muted);font-size:13px;margin-top:.3rem">One payment. Instant unlock. No subscriptions.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="pricing-grid">
        <div class="plan">
            <div class="plan-name">Basic</div>
            <div class="plan-price">₹99</div>
            <div class="plan-period">one-time</div>
            <ul class="plan-feat">
                <li>Clean resume (no watermark)</li>
                <li>ATS Score Report</li>
                <li>DOCX format</li>
            </ul>
            <a href="{RAZORPAY_BASIC}" target="_blank" class="pay-btn">Pay ₹99 →</a>
        </div>
        <div class="plan hot">
            <div class="hot-badge">POPULAR</div>
            <div class="plan-name">Pro</div>
            <div class="plan-price">₹499</div>
            <div class="plan-period">one-time</div>
            <ul class="plan-feat">
                <li>Everything in Basic</li>
                <li>Cover Letter</li>
                <li>Interview Prep Kit</li>
            </ul>
            <a href="{RAZORPAY_PRO}" target="_blank" class="pay-btn">Pay ₹499 →</a>
        </div>
        <div class="plan">
            <div class="plan-name">Yearly</div>
            <div class="plan-price">₹2999</div>
            <div class="plan-period">per year · unlimited</div>
            <ul class="plan-feat">
                <li>Everything in Pro</li>
                <li>LinkedIn Profile Rewrite</li>
                <li>Unlimited resumes</li>
            </ul>
            <a href="{RAZORPAY_YEARLY}" target="_blank" class="pay-btn">Pay ₹2999 →</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── UNLOCK AFTER PAYMENT ──
    st.markdown("""
    <div class="unlock-box">
        <div class="card-title">✅ Already Paid? Enter Transaction ID to Unlock</div>
        <div style="color:var(--muted);font-size:12px;margin-bottom:.8rem">
            After payment your UPI app shows a Transaction ID — paste it below. Instant unlock, no email needed.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([3,1])
    with c1:
        txn = st.text_input("Transaction ID from UPI / Razorpay", placeholder="e.g. pay_Pxxxxxxxxxxxxxx or UPI ref number", label_visibility="collapsed")
    with c2:
        plan = st.selectbox("Plan", ["Basic ₹99", "Pro ₹499", "Yearly ₹2999"], label_visibility="collapsed")

    if st.button("🔓 Unlock My Plan"):
        if txn and len(txn) > 6:
            st.session_state.plan = plan
            st.session_state.step = 3
            st.rerun()
        else:
            st.error("Please enter your transaction ID from your UPI app.")


# ─────────────────────────────────────────────
# UNLOCKED CONTENT
# ─────────────────────────────────────────────
if st.session_state.step == 3 and st.session_state.ai_data:

    plan = st.session_state.plan or ""
    is_pro    = "Pro" in plan or "Yearly" in plan
    is_yearly = "Yearly" in plan

    st.success(f"🎉 {plan} unlocked! Your files are ready below.")

    if st.session_state.resume_bytes:
        st.download_button(
            "⬇ Download Clean Resume (No Watermark)",
            data=st.session_state.resume_bytes,
            file_name="cvnixo_tailored_resume.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    if is_pro:
        data = st.session_state.ai_data
        tabs = st.tabs(["📝 Cover Letter", "🎯 Interview Kit", "💼 LinkedIn" if is_yearly else "💼 LinkedIn (Yearly only)"])

        with tabs[0]:
            client = groq.Groq(api_key=GROQ_API_KEY)
            with st.spinner("Writing cover letter..."):
                cl_resp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role":"user","content":f"""
Write a compelling cover letter for this candidate applying to this role.
3 paragraphs. Professional but human. No generic openers.
Candidate summary: {data.get('summary','')}
Strong points: {', '.join(data.get('strong_points',[]))}
Job context from resume: {st.session_state.jd_text[:800]}
"""}],
                    temperature=0.6, max_tokens=800
                )
            cover = cl_resp.choices[0].message.content
            st.text_area("Cover Letter", cover, height=300)
            st.download_button("⬇ Download Cover Letter", data=cover, file_name="cvnixo_cover_letter.txt", mime="text/plain")

        with tabs[1]:
            with st.spinner("Building interview kit..."):
                ik_resp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role":"user","content":f"""
Create an interview prep kit.
Include:
1. TOP 5 LIKELY QUESTIONS with brief answer hints based on the resume
2. 3 SMART QUESTIONS TO ASK THE INTERVIEWER
3. KEY SKILLS TO HIGHLIGHT

Strong points: {', '.join(data.get('strong_points',[]))}
Missing skills: {', '.join(data.get('missing_skills',[]))}
JD context: {st.session_state.jd_text[:800]}
"""}],
                    temperature=0.5, max_tokens=1000
                )
            kit = ik_resp.choices[0].message.content
            st.text_area("Interview Kit", kit, height=350)
            st.download_button("⬇ Download Interview Kit", data=kit, file_name="cvnixo_interview_kit.txt", mime="text/plain")

        with tabs[2]:
            if is_yearly:
                with st.spinner("Rewriting LinkedIn profile..."):
                    li_resp = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role":"user","content":f"""
Rewrite this person's LinkedIn profile.
Provide:
1. HEADLINE (120 chars max, keyword-rich)
2. ABOUT SECTION (first-person, engaging, 2000 chars max)
3. TOP 5 SKILLS TO ADD

Resume summary: {data.get('summary','')}
Technical skills: {', '.join(data.get('skills_technical',[]))}
Experience: {', '.join([j.get('title','') + ' at ' + j.get('company','') for j in data.get('work_experience',[])])}
"""}],
                        temperature=0.6, max_tokens=900
                    )
                li = li_resp.choices[0].message.content
                st.text_area("LinkedIn Rewrite", li, height=350)
                st.download_button("⬇ Download LinkedIn Rewrite", data=li, file_name="cvnixo_linkedin.txt", mime="text/plain")
            else:
                st.info("LinkedIn Profile Rewrite is available in the Yearly plan (₹2999). Upgrade to unlock.")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    if st.button("🔄 Tailor Another Resume"):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.session_state.step = 1
        st.rerun()


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2.5rem 0 1rem;color:var(--muted);font-size:12px">
    <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1rem;
        background:linear-gradient(135deg,var(--accent),var(--accent2));
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        background-clip:text;margin-bottom:.4rem">⚡ Cvnixo</div>
    Built for serious job seekers · Made in India 🇮🇳
</div>
""", unsafe_allow_html=True)
