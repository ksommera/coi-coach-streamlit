import os
import sys
import streamlit as st
from openai import OpenAI
import openai

# =========================================
# STREAMLIT CONFIG
# =========================================

st.set_page_config(
    page_title="Centers of Influence Coach",
    page_icon="🧭",
    layout="wide"
)

# --- Environment debug ---
st.sidebar.write("📦 Environment info")
st.sidebar.write(f"Python: {sys.version.split()[0]}")
st.sidebar.write(f"OpenAI: {openai.__version__}")

# =========================================
# CUSTOM CSS THEME
# =========================================

CUSTOM_CSS = """
<style>
.stApp { background-color: #f5f7fb; }

/* Cards */
.card {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    border: 1px solid #e5e7eb;
    margin-bottom: 0.8rem;
}
.card-soft {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 1rem;
    border: 1px solid #e5e7eb;
    margin-bottom: 0.8rem;
}

/* Titles */
.main-title { font-size: 1.55rem; font-weight: 700; color: #111827; }
.sub-title { font-size: 0.95rem; color: #4b5563; }
.small-label { font-size: 0.78rem; letter-spacing: 0.05em; color: #6b7280; }

/* Inputs */
textarea, input, select { border-radius: 6px !important; }

/* Buttons */
.stButton > button {
    border-radius: 999px !important;
    padding: 0.45rem 1.2rem !important;
    border: 1px solid #0050b3 !important;
    background-color: #0050b3 !important;
    color: white !important;
    font-weight: 600 !important;
}
.stButton > button:hover {
    background-color: #003a82 !important;
    border-color: #003a82 !important;
}

/* Results */
.result-card {
    background-color: white;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
    padding: 1rem;
}

/* Questions */
.qblock {
    padding: 16px;
    background-color: #f1f5f9;
    border: 1px solid #d3d8df;
    border-radius: 8px;
}
.qblock-title { font-weight: 700; font-size: 1.05rem; }
.qblock-help { font-size: 0.86rem; color: #475569; }

.qsep {
    border-bottom: 2px solid #d1d9e0;
    margin: 26px 0;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =========================================
# SYSTEM PROMPT (FULL — AS PROVIDED BY YOU)
# =========================================

SYSTEM_PROMPT = r"""
You are Centers of Influence Coach GPT for New York Life advisors.

Your mission is to:
1) Help advisors quickly find real Centers of Influence (COIs) in their area using live web search.
2) Guide advisors through a short, simple intake (Path A) to build a COI Intelligence Report and COI list.
3) Run a Quick COI Lookup (Path B) when advisors want fast, specific search results.

You MUST follow all logic, rules, workflows, formatting requirements, guardrails, and compliance guidelines
from the internal file "COI System Rules.txt". This prompt is a compressed but complete version for API use.

GENERAL SCOPE
- You focus ONLY on COIs and COI strategy.
- You do NOT provide scripts, full training, or role-plays.
- You do NOT give product, underwriting, compensation, market, tax, legal, or investment advice.
- Redirect such questions to internal NYL resources or the Practice Development Team and re-offer Path 1 or 2.

TONE AND STYLE
- Sound like a helpful, succinct colleague.
- Short sentences, simple language.
- Clean tables and clear headings.
- Assume many advisors are new to COIs.

MODES
You support:
- Path A — Personalized COI Strategy with COI List
- Path B — Quick COI Lookup

IMPORTANT FOR STREAMLIT APP
- UI already handled path selection.
- UI already collected Q1–Q6 for Path A.
- UI already collected ZIP + COI type + context for Path B.
- DO NOT re-ask anything; use provided inputs.

WELCOME BLOCK (reference only)
"👋 Welcome! I can help you find Centers of Influence (COIs) in your area and build a tailored strategy…"

PATH A QUESTIONS (already collected externally)
Q1 – Main ZIP code  
Q2 – Target segments  
Q3 – Common life events  
Q4 – Communities / affinity groups  
Q5 – Advisor background  
Q6 – Warm networks  

SEGMENT GUIDANCE
Use this when interpreting segments:

| Segment                      | Age Range | Typical triggers and needs                                      |
|-----------------------------|-----------|------------------------------------------------------------------|
| Young Childfree             | 24–44     | Jobs, relationships, cash-flow changes                          |
| Young Families              | 25–44     | New baby, home purchase, childcare, education planning          |
| Mid-Career Families         | 35–54     | Job changes, eldercare, education decisions                     |
| Affluent Mid-Career Families| 35–54     | Stock comp, higher homes, complex taxes                         |
| Affluent Pre-Retirees       | 55+       | Retirement readiness, downsizing                                |
| Affluent Retirees           | 65+       | Income stability, healthcare, estate planning                   |

COMMUNITIES / AFFINITIES
Examples: NYL cultural markets, LGBTQ+, immigrant groups, parent groups, alumni, civic groups.

COI INTELLIGENCE REPORT (PATH A REQUIRED)
MUST INCLUDE:

1) CLIENT FOCUS OVERVIEW

| Item        | Summary         |
|------------|-----------------|
| Main Area  | [ZIP and area]  |
| Key Segments | [segments]    |
| Life Events  | [events]      |
| Communities  | [communities] |
| Background   | [background]  |
| Networks     | [networks]    |

2) COI OPPORTUNITY THEMES (3–5 themes)
3) PRIORITY COI CATEGORIES TABLE
4) COI OPPORTUNITY CHANNELS (2–3 sentences)

REAL COI SEARCH ENGINE RULES
- Use GPT-5.1’s built-in live browsing.
- Center search on ZIP → broaden if needed.
- Combine adjacent towns, ZIPs, counties.

FIRST BATCH RULES
- Always aim for 20–25 COIs.
- If <15 → broaden.
- <10 only allowed after two broadenings + scarcity.

COI TABLE FORMAT

| Name | Role/Specialty | Organization + Link | Public Contact | Why They Fit |

Public Contact may include:
- Business phone
- Public business email
- LinkedIn URL
- Contact page

NEVER include:
- Personal phone numbers
- Private emails

WHY THEY FIT should map to:
- Segments
- Life events
- Communities
- Background
- Warm networks

ASK FOR MORE (REQUIRED LINE)
"**Would you like more COIs?  
I can add more (up to 125 total), or we can finish with your summary.**"

PATH B — QUICK LOOKUP
- Skip Intelligence Report.
- Use ZIP + COI type + context.
- Return ONLY first batch of 20–25.
- End with the required line.

FINAL SUMMARY
- Recap user details & segments.
- Recap COI categories.
- Offer PDF summary.

COMPLIANCE
- Only share public business info.
- No product/tax/legal/market/underwriting advice.
- Encourage proper verification.

END SYSTEM PROMPT
"""

# =========================================
# OPENAI CLIENT
# =========================================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================================
# GPT-5.1 CALL WRAPPERS (CHAT COMPLETIONS)
# =========================================

def _run_chat_completion(user_input: str, max_tokens: int) -> str:
    """
    Wrapper for GPT-5.1 with automatic web browsing.
    No 'tools' parameter is needed — your model performs web search implicitly.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"⚠️ Error while calling OpenAI: {e}"


# =========================================
# PATH A MODEL — Intelligence Report + First COI Batch
# =========================================

def run_path_a_model(q1, q2, q3, q4, q5, q6):
    user_input = (
        "You are running PATH A — Personalized COI Strategy with COI List.\n\n"
        f"Q1 – Main ZIP code: {q1}\n"
        f"Q2 – Target segments: {q2}\n"
        f"Q3 – Common life events: {q3}\n"
        f"Q4 – Communities / affinity groups: {q4}\n"
        f"Q5 – Advisor background: {q5}\n"
        f"Q6 – Warm networks: {q6}\n\n"
        "Follow the COI System Rules strictly:\n"
        "1) Build the COI Intelligence Report.\n"
        "2) Then perform live browsing and return the first batch of 20–25 real COIs.\n"
        "3) Use required COI table format.\n"
        "4) End with: 'Would you like more COIs? I can add more (up to 125 total)…'"
    )
    return _run_chat_completion(user_input, max_tokens=2000)


# =========================================
# PATH B MODEL — Quick Lookup
# =========================================

def run_path_b_model(zip_code, coi_type, ctx):
    user_input = (
        "You are running PATH B — Quick COI Lookup.\n\n"
        f"ZIP: {zip_code}\n"
        f"COI type(s): {coi_type}\n"
        f"Extra context: {ctx}\n\n"
        "Skip the Intelligence Report.\n"
        "Immediately perform live browsing and return ONLY the first COI batch (20–25 results)\n"
        "in the required table format.\n"
        "End with the required line about more COIs."
    )
    return _run_chat_completion(user_input, max_tokens=1500)


# =========================================
# SESSION STATE
# =========================================

if "selected_path" not in st.session_state:
    st.session_state.selected_path = None
if "path_a_result" not in st.session_state:
    st.session_state.path_a_result = None
if "path_b_result" not in st.session_state:
    st.session_state.path_b_result = None


# =========================================
# HEADER UI
# =========================================

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("""
    <div class="card">
        <div class="small-label">New York Life • COI Coach</div>
        <div class="main-title">Centers of Influence Coach</div>
        <div class="sub-title">Find real COIs and build a clear COI strategy.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card-soft">
        <b>How this works</b><br>
        • Choose a path<br>
        • Answer a few questions<br>
        • GPT-5.1 will automatically search the web<br><br>
        <span style="font-size:0.8rem;color:#6b7280;">Verify all COIs and follow NYL compliance.</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)


# =========================================
# PATH SELECTION UI
# =========================================

st.markdown("""
<div class="card">
  <b>Select your path</b><br>
  Choose the workflow you want to run.
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    if st.button("1️⃣ Personalized COI Strategy with COI List"):
        st.session_state.selected_path = "A"
    st.markdown("""
    <div class="card-soft">
        <b>You get:</b>
        <ul>
            <li>COI Intelligence Report</li>
            <li>20–25 real COIs</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with c2:
    if st.button("2️⃣ Quick COI Lookup"):
        st.session_state.selected_path = "B"
    st.markdown("""
    <div class="card-soft">
        <b>You get:</b>
        <ul>
            <li>20–25 real COIs (immediate)</li>
            <li>No intake needed</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)


# =========================================
# PATH A UI
# =========================================

if st.session_state.selected_path == "A":

    st.markdown("### 1️⃣ Path A — Personalized COI Strategy & First COI Batch")

    with st.form("path_a_form"):

        # Q1
        st.markdown('<div class="qblock"><div class="qblock-title">Q1/6 — What is your main ZIP code?</div></div>', unsafe_allow_html=True)
        q1 = st.text_input("", placeholder="e.g., 07302")
        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)

        # Q2
        st.markdown('<div class="qblock"><div class="qblock-title">Q2/6 — Which target segments fit your clients’ market?</div></div>', unsafe_allow_html=True)
        q2 = st.text_area("", height=60)
        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)

        # Q3
        st.markdown('<div class="qblock"><div class="qblock-title">Q3/6 — Which life events are most common?</div></div>', unsafe_allow_html=True)
        q3 = st.text_area("", height=60)
        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)

        # Q4
        st.markdown('<div class="qblock"><div class="qblock-title">Q4/6 — Which communities or affinity groups do you work closely with?</div></div>', unsafe_allow_html=True)
        q4 = st.text_area("", height=60)
        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)

        # Q5
        st.markdown('<div class="qblock"><div class="qblock-title">Q5/6 — What is your past professional background?</div></div>', unsafe_allow_html=True)
        q5 = st.text_area("", height=70)
        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)

        # Q6
        st.markdown('<div class="qblock"><div class="qblock-title">Q6/6 — What warm networks do you already have?</div></div>', unsafe_allow_html=True)
        q6 = st.text_area("", height=70)

        submit_A = st.form_submit_button("Generate Intelligence Report & First COI Batch")

    if submit_A:
        if not q1:
            st.warning("Please enter your main ZIP code.")
        else:
            with st.spinner("Generating Intelligence Report & searching for real COIs…"):
                st.session_state.path_a_result = run_path_a_model(q1, q2, q3, q4, q5, q6)

    if st.session_state.path_a_result:
        st.markdown("### 🧠 Intelligence Report & First COI Batch")
        st.markdown(f"<div class='result-card'>{st.session_state.path_a_result}</div>", unsafe_allow_html=True)


# =========================================
# PATH B UI
# =========================================

elif st.session_state.selected_path == "B":

    st.markdown("### 2️⃣ Path B — Quick COI Lookup")

    with st.form("path_b_form"):

        st.markdown('<div class="qblock"><div class="qblock-title">ZIP code</div></div>', unsafe_allow_html=True)
        zip_b = st.text_input("", placeholder="e.g., 07302")
        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)

        st.markdown('<div class="qblock"><div class="qblock-title">COI Type</div></div>', unsafe_allow_html=True)
        coi_type = st.selectbox("", [
            "CPA / Tax Advisor",
            "Estate Planning Attorney",
            "Immigration Attorney",
            "Family Law / Divorce Attorney",
            "Realtor",
            "Mortgage Lender / Broker",
            "Pediatrician / OB-GYN",
            "School / Education Professional",
            "Business Banker / RM",
            "Business Consultant / Career Coach",
            "Community / Cultural Organization",
            "Other / Mixed COIs",
        ])
        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)

        st.markdown('<div class="qblock"><div class="qblock-title">Optional context</div></div>', unsafe_allow_html=True)
        ctx = st.text_area("", height=70)

        submit_B = st.form_submit_button("Find COIs Now")

    if submit_B:
        if not zip_b:
            st.warning("Please enter a ZIP code.")
        else:
            with st.spinner("Searching for real COIs…"):
                st.session_state.path_b_result = run_path_b_model(zip_b, coi_type, ctx)

    if st.session_state.path_b_result:
        st.markdown("### 📋 COI List — First Batch")
        st.markdown(f"<div class='result-card'>{st.session_state.path_b_result}</div>", unsafe_allow_html=True)


# =========================================
# DEFAULT VIEW
# =========================================

else:
    st.write("Choose **Path 1** or **Path 2** above to begin.")
