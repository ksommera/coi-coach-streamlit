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

# --- Environment debug (safe to keep or remove later)
st.sidebar.write("📦 Environment info")
st.sidebar.write(f"Python version: {sys.version.split()[0]}")
st.sidebar.write(f"OpenAI version: {openai.__version__}")

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
# SYSTEM PROMPT (FULL, CLEANED, FLUSH-LEFT)
# =========================================

SYSTEM_PROMPT = r"""
You are Centers of Influence Coach GPT for New York Life advisors.
Your mission is to:
1) Help advisors quickly find real Centers of Influence (COIs) in their area using live web search.
2) Guide advisors through a short, simple intake (Path A) to build a COI Intelligence Report and COI list.
3) Run a Quick COI Lookup (Path B) when advisors want fast, specific search results.

You must follow all logic, rules, workflows, formatting requirements, guardrails, and compliance guidelines
from the internal file "COI System Rules.txt". This prompt is a compressed but complete version for API use.

GENERAL SCOPE
- You focus ONLY on COIs and COI strategy.
- You do NOT provide scripts, full training, or role-plays.
- You do NOT give product, underwriting, compensation, market, tax, legal, or investment advice.
- Redirect questions about those topics to NYL internal resources or the Practice Development Team.

TONE AND STYLE
- Sound like a helpful, succinct colleague.
- Use short sentences and simple language.
- Avoid jargon, long paragraphs, and unnecessary detail.
- Assume many advisors are new to COIs.
- Use clean tables and clear section headings.

MODES
You operate in one overarching mode: "Find COIs in my area."
Within that:
- Path A — Personalized COI Strategy with COI List
- Path B — Quick COI Lookup

STREAMLIT CONTEXT
- The UI already collected answers.
- DO NOT re-ask questions.
- Use provided values exactly as if gathered in conversation.

WELCOME BLOCK (REFERENCE ONLY)
"👋 Welcome. I can help you find Centers of Influence (COIs) in your area and build a tailored COI strategy…"

PATH A — QUESTIONS (already collected by UI)
Q1 – Main ZIP code
Q2 – Target segments
Q3 – Common life events
Q4 – Communities / affinity groups
Q5 – Advisor professional background
Q6 – Warm networks already available

SEGMENT GUIDANCE TABLE
| Segment                      | Age Range | Typical triggers and needs                                      |
|-----------------------------|-----------|------------------------------------------------------------------|
| Young Childfree             | 24–44     | Jobs, relationships, cash-flow changes                          |
| Young Families              | 25–44     | New baby, home purchase, childcare, education planning          |
| Mid-Career Families         | 35–54     | Job changes, eldercare, education decisions                     |
| Affluent Mid-Career Families| 35–54     | Stock comp, higher-value homes, complex taxes                   |
| Affluent Pre-Retirees       | 55+       | Retirement readiness, downsizing                                |
| Affluent Retirees           | 65+       | Income stability, healthcare, estate planning                   |

COMMUNITIES / AFFINITIES
Examples include NYL cultural markets (African American, Chinese, Korean, Latino, South Asian, Vietnamese),
LGBTQ+, faith communities, immigrant communities, parent groups, alumni networks, civic organizations.

COI INTELLIGENCE REPORT (Path A REQUIRED OUTPUT)
You MUST output all of the following:

1) CLIENT FOCUS OVERVIEW TABLE
| Item        | Summary         |
|-------------|-----------------|
| Main Area   | [ZIP and area]  |
| Segments    | [segments]      |
| Life Events | [events]        |
| Communities | [communities]   |
| Background  | [background]    |
| Networks    | [networks]      |

2) OPPORTUNITY THEMES
Write 3–5 concise themes linking:
- Segments
- Life events
- Communities
- Advisor background
- Warm networks

3) PRIORITY COI CATEGORIES TABLE
| COI Category                | Why High Priority |
|----------------------------|-------------------|
| CPA / Tax Advisor          | Planning and major financial decisions |
| Mortgage Lender / Broker   | Core during home purchase or relocation |
| Realtor (family/relocation)| Life events tied to moving, families    |
| Estate Planning Attorney   | Protection + long-term planning         |
| Immigration Attorney       | Expats + relocation cases               |
| Pediatrician / OB-GYN      | Young families + trust relationships    |
| School Counselor / Principal| Parent networks + school transitions   |
| Business Banker / RM       | Business owners + professionals         |
| Business Consultant / Coach| Job changes + career shifts             |
| Community / Cultural Leader| High-trust networks                     |

4) OPPORTUNITY CHANNELS (2–3 short sentences)
Describe:
- Where introductions naturally occur (financial/tax, housing, family, community, profession).
- How advisor background and networks enhance these opportunities.

COI SEARCH (Path A & B)
- Focus search on the advisor’s ZIP.
- If <15 results → broaden geographically.
- Use professional associations, local directories, schools, hospitals, small business clusters.

FIRST BATCH RULE
- ALWAYS attempt to deliver 20–25 COIs.
- If you broaden twice and still have <10, state scarcity clearly.

COI TABLE FORMAT (MANDATORY)
| Name | Role/Specialty | Organization + Link | Public Contact | Why They Fit |

Public Contact may include:
- Business phone
- Public business email
- LinkedIn URL
- Contact page

NEVER include personal numbers or private emails.

WHY THEY FIT must connect back to:
- Segments
- Life events
- Communities
- Advisor background
- Warm networks

ASK FOR MORE (MANDATORY)
End every batch with:
"**Would you like more COIs? I can add more (up to 125 total), or we can finish with your summary.**"

PATH B (Quick Lookup)
- Skip Intelligence Report.
- Use ZIP + COI_TYPE + optional context.
- Return ONLY first batch of 20–25 COIs.
- Use the same COI table.

FINAL SUMMARY (when advisor declines more COIs)
- Summarize their focus.
- Summarize priority COI categories.
- Summarize intro channels.
- Report total COIs identified.
- Offer PDF summary (explain contents).

COMPLIANCE
- Only share public business information.
- Avoid prohibited advice categories.
- Encourage verification of COIs.

END SYSTEM PROMPT.
"""

# =========================================
# OPENAI CLIENT
# =========================================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =========================================
# CHAT COMPLETION HELPER (BROWSING-CAPABLE MODEL)
# =========================================

def _run_chat_completion(user_input: str, max_completion_tokens: int) -> str:
    """
    Wrapper for a browsing-capable model (gpt-4o-mini-omni).
    No explicit tools parameter needed here.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini-omni",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            max_completion_tokens=max_completion_tokens,
        )
        msg = response.choices[0].message
        return msg.content or ""
    except Exception as e:
        return f"⚠️ Error while calling OpenAI: {e}"


# =========================================
# PATH A — Intelligence Report + First COI Batch
# =========================================

def run_path_a_model(q1_zip, q2_segments, q3_events, q4_comm, q5_background, q6_networks):
    """
    Build the COI Intelligence Report and return the first batch of real COIs.
    """
    user_input = (
        "You are running PATH A — Personalized COI Strategy with COI List.\n\n"
        f"Q1 – Main ZIP code: {q1_zip}\n"
        f"Q2 – Target segments: {q2_segments}\n"
        f"Q3 – Common life events: {q3_events}\n"
        f"Q4 – Communities / affinity groups: {q4_comm}\n"
        f"Q5 – Advisor background: {q5_background}\n"
        f"Q6 – Warm networks: {q6_networks}\n\n"
        "Follow the COI System Rules strictly:\n"
        "1) Build the full COI Intelligence Report.\n"
        "2) Then perform browsing and return the first batch of 20–25 real COIs.\n"
        "3) Use required table format.\n"
        "4) End with the required question."
    )

    return _run_chat_completion(user_input, max_completion_tokens=2000)


# =========================================
# PATH B — Quick COI Lookup
# =========================================

def run_path_b_model(zip_code, coi_type, extra_context):
    """
    Return ONLY the first batch of 20–25 COIs for the chosen type.
    """
    user_input = (
        "You are running PATH B — Quick COI Lookup.\n\n"
        f"ZIP code: {zip_code}\n"
        f"COI type(s): {coi_type}\n"
        f"Extra context: {extra_context}\n\n"
        "Follow the COI System Rules.\n"
        "Skip the Intelligence Report.\n"
        "Immediately perform browsing and return ONLY:\n"
        "- First COI batch (20–25 results)\n"
        "- Required COI table format\n\n"
        "End with the required line about adding more COIs."
    )

    return _run_chat_completion(user_input, max_completion_tokens=1500)

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
        <div class="sub-title">Find real COIs and build a simple, targeted COI strategy.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card-soft">
        <b>How this works</b><br>
        • Choose a path<br>
        • Answer a few questions<br>
        • The model will automatically use web search when needed<br><br>
        <span style="font-size:0.82rem;color:#6b7280;">Always verify COIs and follow NYL compliance.</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)


# =========================================
# PATH SELECTION
# =========================================

st.markdown("""
<div class="card">
    <b>Select your path</b><br>
    Choose the workflow you want to run.
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    if st.button("1️⃣ Personalized COI Strategy with COI List", key="select_A"):
        st.session_state.selected_path = "A"

    st.markdown("""
    <div class="card-soft">
        <b>You’ll get:</b>
        <ul style="color:#4b5563;">
            <li>COI Intelligence Report</li>
            <li>20–25 real COIs</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with c2:
    if st.button("2️⃣ Quick COI Lookup", key="select_B"):
        st.session_state.selected_path = "B"

    st.markdown("""
    <div class="card-soft">
        <b>You’ll get:</b>
        <ul style="color:#4b5563;">
            <li>20–25 real COIs instantly</li>
            <li>No intake required</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)


# =========================================
# PATH A — FULL-WIDTH UI
# =========================================

if st.session_state.selected_path == "A":

    st.markdown("### 1️⃣ Path A — Personalized COI Strategy & First COI Batch")

    with st.form("path_a_form"):

        # ========================
        # Q1 — Main ZIP code
        # ========================
        st.markdown("""
        <div class="qblock">
            <div class="qblock-title">Q1/6 — What is your main ZIP code?</div>
        </div>
        """, unsafe_allow_html=True)

        q1 = st.text_input(
            "",
            placeholder="e.g., 07302",
            key="qa_zip"
        )

        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)


        # ========================
        # Q2 — Target Segments
        # ========================
        st.markdown("""
        <div class="qblock">
            <div class="qblock-title">
                Q2/6 — Which target segments fit your clients’ market?
            </div>
            <div class="qblock-help">
                Use labels like Young Families, Mid-Career Families, Affluent Pre-Retirees,
                or niche segments such as expats, small business owners, teachers, or tech professionals.
            </div>
        </div>
        """, unsafe_allow_html=True)

        q2 = st.text_area(
            "",
            placeholder="e.g., Young Families; Affluent Mid-Career Professionals; French-speaking expats; small business owners",
            height=60,
            key="qa_segments"
        )

        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)


        # ========================
        # Q3 — Common Life Events
        # ========================
        st.markdown("""
        <div class="qblock">
            <div class="qblock-title">Q3/6 — Which life events are most common in your clients’ lives?</div>
            <div class="qblock-help">
                Examples: new baby, home purchase/move, job change, stock compensation,
                immigration/relocation, education decisions.
            </div>
        </div>
        """, unsafe_allow_html=True)

        q3 = st.text_area(
            "",
            placeholder="e.g., relocation, new baby, school decisions, new job with RSUs",
            height=60,
            key="qa_events"
        )

        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)


        # ========================
        # Q4 — Communities / Affinity Groups
        # ========================
        st.markdown("""
        <div class="qblock">
            <div class="qblock-title">
                Q4/6 — Are there communities or affinity groups you work closely with?
            </div>
            <div class="qblock-help">
                Examples: NYL cultural markets (African American, Chinese, Korean, Latino, South Asian, Vietnamese),
                LGBTQ+, immigrant communities, parent groups, alumni networks, faith communities.
            </div>
        </div>
        """, unsafe_allow_html=True)

        q4 = st.text_area(
            "",
            placeholder="e.g., French expat community; LGBTQ+ professionals; local parent networks; faith community",
            height=60,
            key="qa_communities"
        )

        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)


        # ========================
        # Q5 — Advisor Background
        # ========================
        st.markdown("""
        <div class="qblock">
            <div class="qblock-title">
                Q5/6 — What is your past professional background?
            </div>
            <div class="qblock-help">
                You may include roles, industries, and firms.
            </div>
        </div>
        """, unsafe_allow_html=True)

        q5 = st.text_area(
            "",
            placeholder="e.g., Former CPA at Deloitte; financial analyst; tech sales; healthcare admin",
            height=70,
            key="qa_background"
        )

        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)


        # ========================
        # Q6 — Warm Networks
        # ========================
        st.markdown("""
        <div class="qblock">
            <div class="qblock-title">
                Q6/6 — What warm networks do you already have?
            </div>
            <div class="qblock-help">
                Examples: former colleagues, alumni, local business owners, parent groups, chamber of commerce.
            </div>
        </div>
        """, unsafe_allow_html=True)

        q6 = st.text_area(
            "",
            placeholder="e.g., alumni association; daycare parents; former coworkers; local entrepreneurs",
            height=70,
            key="qa_networks"
        )

        # ========================
        # SUBMIT BUTTON — PATH A
        # ========================
        submit_A = st.form_submit_button("Generate Intelligence Report & First COI Batch")


    # ====== PROCESS PATH A SUBMISSION ======
    if submit_A:
        if not q1:
            st.warning("Please enter your main ZIP code before continuing.")
        else:
            with st.spinner("Generating Intelligence Report and searching for real COIs…"):
                st.session_state.path_a_result = run_path_a_model(
                    q1, q2, q3, q4, q5, q6
                )

    # ====== DISPLAY PATH A RESULT ======
    if st.session_state.path_a_result:
        st.markdown("### 🧠 Intelligence Report & First COI Batch")
        st.markdown(f"<div class='result-card'>{st.session_state.path_a_result}</div>", unsafe_allow_html=True)



# =========================================
# PATH B — Quick COI Lookup
# =========================================

elif st.session_state.selected_path == "B":

    st.markdown("### 2️⃣ Path B — Quick COI Lookup")

    with st.form("path_b_form"):

        # ZIP
        st.markdown("""
        <div class="qblock">
            <div class="qblock-title">ZIP code</div>
        </div>
        """, unsafe_allow_html=True)

        zip_b = st.text_input(
            "",
            placeholder="e.g., 07302",
            key="qb_zip"
        )

        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)


        # COI TYPE
        st.markdown("""
        <div class="qblock">
            <div class="qblock-title">COI Type</div>
        </div>
        """, unsafe_allow_html=True)

        coi_type = st.selectbox(
            "",
            [
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
            ],
            key="qb_type"
        )

        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)


        # OPTIONAL CONTEXT
        st.markdown("""
        <div class="qblock">
            <div class="qblock-title">Optional context</div>
        </div>
        """, unsafe_allow_html=True)

        ctx = st.text_area(
            "",
            placeholder="e.g., French-speaking expats; tech employees with stock compensation; new parents; small business owners",
            height=70,
            key="qb_ctx"
        )

        submit_B = st.form_submit_button("Find COIs Now")


    # ====== PROCESS PATH B SUBMISSION ======
    if submit_B:
        if not zip_b:
            st.warning("Please enter a ZIP code.")
        else:
            with st.spinner("Searching for real COIs…"):
                st.session_state.path_b_result = run_path_b_model(
                    zip_b, coi_type, ctx
                )

    # ====== DISPLAY PATH B RESULT ======
    if st.session_state.path_b_result:
        st.markdown("### 📋 COI List — First Batch")
        st.markdown(f"<div class='result-card'>{st.session_state.path_b_result}</div>", unsafe_allow_html=True)



# =========================================
# DEFAULT VIEW IF NO PATH SELECTED
# =========================================

else:
    st.write("Choose **Path 1** or **Path 2** above to begin.")
