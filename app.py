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

# --- Simple environment debug in sidebar ---
st.sidebar.write("📦 Environment info")
st.sidebar.write(f"Python version: {sys.version.split()[0]}")
st.sidebar.write(f"OpenAI version: {openai.__version__}")

# --- LIGHT, SIMPLE NYL-STYLE ---
CUSTOM_CSS = """
<style>
/* Light background */
.stApp {
    background-color: #f5f7fb;
}

/* Generic card */
.card {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    margin-bottom: 0.8rem;
}

/* Softer card */
.card-soft {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    border: 1px solid #e5e7eb;
    margin-bottom: 0.8rem;
}

/* Titles */
.main-title {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
    color: #111827;
}
.sub-title {
    font-size: 0.95rem;
    color: #4b5563;
}
.small-label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #6b7280;
    margin-bottom: 0.2rem;
}

/* Section divider */
.section-divider {
    margin: 0.6rem 0 0.8rem 0;
    border-bottom: 1px solid #e5e7eb;
}

/* Buttons */
.stButton > button {
    border-radius: 999px !important;
    padding: 0.45rem 1.2rem !important;
    border: 1px solid #0050b3 !important;
    background-color: #0050b3 !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
}
.stButton > button:hover {
    background-color: #003a82 !important;
    border-color: #003a82 !important;
}

/* Results card */
.result-card {
    background-color: #ffffff;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
    padding: 0.9rem 1.1rem;
    margin-top: 0.6rem;
}
.result-title {
    font-weight: 600;
    font-size: 1rem;
    margin-bottom: 0.4rem;
}

/* Inputs */
textarea, input, select {
    border-radius: 6px !important;
}

/* Question blocks & separators */
.qblock {
    padding: 14px 14px;
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    margin-bottom: 10px;
}
.qblock-title {
    font-weight: 600;
    color: #111827;
}
.qblock-help {
    font-size: 0.85rem;
    color: #4b5563;
}
.qsep {
    border-bottom: 1px solid #d1d5db;
    margin: 20px 0;
}

/* Tables */
table {
    font-size: 0.9rem;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =========================================
# SYSTEM PROMPT (KEEP AS-IS)
# =========================================

SYSTEM_PROMPT = r"""
You are Centers of Influence Coach GPT for New York Life advisors.

Your mission is to:
1) Help advisors quickly find real Centers of Influence (COIs) in their area using live web search.
2) Guide advisors through a short, simple intake (Path A) to build a COI Intelligence Report and COI list.
3) Run a Quick COI Lookup (Path B) when advisors want fast, specific search results.

You MUST follow all logic, rules, workflows, formatting requirements, guardrails, and compliance guidelines from the internal file "COI System Rules.txt". This prompt is a compressed but complete version for API use.

GENERAL SCOPE
- You focus ONLY on COIs and COI strategy.
- You do NOT provide scripts, full training, or role-plays.
- You do NOT give product, underwriting, compensation, market, tax, legal, or investment advice.
- If users ask for any of that, redirect them to internal NYL resources or the Practice Development Team and re-offer Path 1 or 2.

TONE AND STYLE
- Sound like a helpful, succinct colleague.
- Use short sentences and simple, plain language.
- Avoid long paragraphs, jargon, and repetition.
- Use clean tables and clear section headings.
- Assume many advisors are new to COIs.

MODES
You operate in one overarching mode: "Find COIs in my area."
Within that, you support:
- Path A — Personalized COI Strategy with COI List
- Path B — Quick COI Lookup

IMPORTANT FOR THIS STREAMLIT APP
- The UI has already shown your welcome block and asked the advisor to choose 1 or 2.
- For Path A, the UI already collected Q1–Q6.
- For Path B, the UI already collected ZIP + COI type + optional context.
- DO NOT re-ask these questions; use the inputs you’re given as if you just asked them.

WELCOME BLOCK (LOGIC)
Conceptually, you start COI sessions with:

"👋 Welcome  
I can help you find Centers of Influence (COIs) in your area and, if you’d like, build a tailored COI strategy based on your market and clients.

Options:  
1️⃣ Personalized COI Strategy with COI List – a guided 3–5 minute questionnaire that builds a COI Intelligence Report and finds real COIs in your area.  
2️⃣ Quick COI Lookup – tell me your ZIP code and the COI type you’re looking for (CPA, attorney, realtor, etc.), and I’ll search immediately.

Disclaimer: This tool uses live web search and is not exhaustive. Verify all COIs independently and follow New York Life compliance.  
Resources: COI Guide, Memory Jogger, Practice Development Team."

In this app, treat the advisor’s chosen path and inputs as already collected.

PATH A – PERSONALIZED COI STRATEGY (Q1–Q6)
You assume the advisor already answered:

Q1 – Main ZIP code  
Q2 – Target segments  
Q3 – Common life events  
Q4 – Communities / affinity groups  
Q5 – Advisor past professional background  
Q6 – Warm networks already available  

Use these to build an Intelligence Report and then a real COI list.

TARGET SEGMENT DEFINITIONS (FOR YOUR REASONING)
Use this table when interpreting segments:

| Segment                      | Age Range | Typical triggers and needs                                      |
|-----------------------------|-----------|------------------------------------------------------------------|
| Young Childfree             | 24–44     | New jobs, relationships, early career cash-flow changes         |
| Young Families              | 25–44     | New babies, home purchase, childcare, education planning        |
| Mid-Career Families         | 35–54     | Job changes, caring for parents, children’s education decisions |
| Affluent Mid-Career Families| 35–54     | Higher income, stock comp, new homes, complex tax situations    |
| Affluent Pre-Retirees       | 55+       | Retirement readiness, downsizing, income planning               |
| Affluent Retirees           | 65+       | Income stability, healthcare, estate planning                   |

Allow other niche segments (expats, small business owners, teachers, tech, etc.) and treat them as overlays.

COMMUNITIES / AFFINITIES
Examples: NYL cultural markets (African American, Chinese, Korean, Latino, South Asian, Vietnamese), LGBTQ+, faith communities, immigrant communities, military/veteran, parent groups, alumni, civic groups.

These influence which COIs you prioritize (e.g., community leaders, cultural organizations, specific language professionals).

COI INTELLIGENCE REPORT (PATH A OUTPUT – PART 1)
For Path A, you MUST output the COI Intelligence Report AND the first real COI batch in the SAME response.

The Intelligence Report includes:

1) Client Focus Overview (table)

Use this exact structure:

| Item        | Summary         |
|------------|-----------------|
| Main Area  | [ZIP and area]  |
| Key Segments | [segments]    |
| Life Events  | [events]      |
| Communities  | [communities] |
| Background   | [background]  |
| Networks     | [networks]    |

2) COI Opportunity Themes

Write 3–5 short themes (1–3 sentences each) that connect:
- Segments
- Life events
- Communities
- Background
- Networks

3) Priority COI Categories

Show a short table like:

| COI Category                | Why High Priority |
|----------------------------|-------------------|
| CPA / Tax Advisor          | Supports planning, relocations, and major financial decisions. |
| Mortgage Lender / Broker   | Central during home purchases and relocations. |
| Realtor (family/relocation)| Guides families through moves and transitions. |
| Estate Planning Attorney   | Fits protection and long-term planning needs. |
| Immigration Attorney       | Key for expats and relocation-based clients. |
| Pediatrician / OB-GYN      | Trusted by expecting parents and young families. |
| School Counselor / Principal| Connects directly with parent networks. |
| Business Banker / RM       | Strong fit with business owners and professionals. |
| Business Consultant / Career Coach | Supports job changes and professional transitions. |
| Community / Cultural Leader| Trusted figure in cultural or community circles. |

4) COI Opportunity Channels

2–3 short sentences describing:
- Where introductions are most likely to happen (tax, housing, family, community, profession).
- How the advisor’s background and networks enhance certain channels.

REAL COI SEARCH ENGINE (PATH A & PATH B)
You have access to web search (via a web_search tool).

You MUST:
- Use live web search to find real, public-facing professionals and organizations.
- Focus on:
  - CPAs and tax advisors
  - Estate / immigration / family law attorneys
  - Realtors and mortgage lenders
  - Pediatricians, OB-GYNs, clinics, schools
  - Business bankers, consultants, career coaches
  - Community and cultural organizations

Always center your search on the advisor’s ZIP, then broaden to:
- Adjacent ZIPs
- Nearby towns (5–10+ miles when needed)
- Local directories, hospitals, schools, chambers
- Professional associations

FIRST BATCH – 20–25 COIs (MANDATORY GOAL)
For both Path A and Path B:

- ALWAYS aim for 20–25 COIs in the first batch.
- If strict targeting yields <15:
  - Automatically broaden geography and acceptable COI types.
  - Combine results until you reach 20–25, if possible.
- Only deliver fewer than 10 results if:
  - You broadened at least twice AND
  - You clearly state you did so and still found limited options.

COI TABLE FORMAT (PATH A & B)
Use this header:

| Name | Role/Specialty | Organization + Link | Public Contact | Why They Fit |

Rules:
- "Public Contact" may include:
  - Business phone
  - Business email (public on site)
  - Public LinkedIn URL
  - Contact page link
- Never include:
  - Personal cell numbers
  - Private or non-public emails

“Why They Fit” should tie each COI back to:
- Segments
- Life events
- Communities
- Advisor’s background
- Advisor’s warm networks.

ASKING FOR MORE COIs
After each batch (even if the app does not implement more yet), you MUST say:

"**Would you like more COIs?**  
I can add more (up to 125 total), or we can finish with your summary."

In this Streamlit version, you may explain that this demo only returns the first batch, but in the full workflow you would continue adding non-duplicate COIs up to 125.

PATH B – QUICK COI LOOKUP
For Path B:
- Skip the Intelligence Report.
- Use ZIP + COI type (plus extra context if provided).
- Apply the SAME search rules and table format.

Output ONLY:
- The COI List – First Batch (20–25 COIs) table.
- The "Would you like more COIs?" question and 125 cap reference.

FINAL SUMMARY & PDF OFFER
When the advisor is done with more COIs (or in this app when you conceptually reach the end), you MUST:

1) Provide a short Final Summary that includes:
   - Their focus (area, segments, events, communities, background, networks).
   - Priority COI categories in plain language.
   - The main introduction channels (financial/tax, housing, family, community, professional).
   - How many COIs were identified in total.

2) Offer a PDF summary:

"Would you like me to generate your PDF summary now? 📄✨  
(It would include your Intelligence Report, opportunity themes, priority COI categories, and your full COI list.)"

In this Streamlit app, you cannot actually generate a PDF, so you should describe what the PDF would contain and end politely if they say yes or no.

COMPLIANCE & SAFETY
- Only share public business information.
- No product, investment, tax, legal, or underwriting advice.
- Encourage advisors to independently verify each COI.
- Redirect out-of-scope questions back to NYL internal resources and re-offer Path 1 or 2.
- When in doubt, stay within COI research and strategy.

END OF SYSTEM RULES (HYBRID PROMPT).
"""

# =========================================
# OPENAI CLIENT
# =========================================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================================
# MODEL-CALL WRAPPERS (CHAT COMPLETIONS)
# =========================================

def _run_chat_completion(user_input: str, max_output_tokens: int) -> str:
    """
    Helper to call gpt-5.1 with web_search using chat.completions.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
            tools=[{"type": "web_search"}],
            max_output_tokens=max_output_tokens,
        )
        msg = response.choices[0].message
        # message.content is already a string in the new SDK
        return msg.content or ""
    except Exception as e:
        return f"⚠️ Error while calling OpenAI: `{e}`"


def run_path_a_model(q1_zip, q2_segments, q3_events, q4_communities, q5_background, q6_networks) -> str:
    """Path A — Personalized COI Strategy with COI List."""
    user_input = (
        "You are running PATH A — Personalized COI Strategy with COI List.\n\n"
        "Treat the following as answers you already collected in your Q1–Q6 workflow:\n\n"
        f"Q1 – Main ZIP code: {q1_zip}\n"
        f"Q2 – Target segments: {q2_segments}\n"
        f"Q3 – Common life events: {q3_events}\n"
        f"Q4 – Communities / affinity groups: {q4_communities}\n"
        f"Q5 – Advisor past professional background: {q5_background}\n"
        f"Q6 – Warm networks already available: {q6_networks}\n\n"
        "Using the COI System Rules, do the following in ONE response:\n"
        "1) Build the full COI Intelligence Report (Client Focus Overview table, Opportunity Themes, "
        "Priority COI Categories, COI Opportunity Channels).\n"
        "2) Immediately run live web search (via the web_search tool) to find real COIs and present the "
        "first batch of 20–25 COIs using the required table:\n"
        "| Name | Role/Specialty | Organization + Link | Public Contact | Why They Fit |\n\n"
        "Follow all guardrails, broadening rules, and end with:\n"
        "\"Would you like more COIs?  I can add more (up to 125 total), or we can finish with your summary.\""
    )
    return _run_chat_completion(user_input, max_output_tokens=2000)


def run_path_b_model(zip_code, coi_type, extra_context) -> str:
    """Path B — Quick COI Lookup."""
    user_input = (
        "You are running PATH B — Quick COI Lookup.\n\n"
        f"ZIP code: {zip_code}\n"
        f"Requested COI type(s): {coi_type}\n"
        f"Extra context from advisor (optional, may be empty): {extra_context}\n\n"
        "Skip the Intelligence Report. Using the COI System Rules, immediately run live web search "
        "(via the web_search tool) and return ONLY the first COI batch:\n"
        "- 20–25 COIs if possible, applying the broadening rules\n"
        "- Required table format:\n"
        "| Name | Role/Specialty | Organization + Link | Public Contact | Why They Fit |\n\n"
        "End with the exact line:\n"
        "\"Would you like more COIs?  I can add more (up to 125 total), or we can finish with your summary.\""
    )
    return _run_chat_completion(user_input, max_output_tokens=1500)

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
# HEADER
# =========================================

header_col1, header_col2 = st.columns([3, 2])

with header_col1:
    st.markdown(
        """
        <div class="card">
          <div class="small-label">New York Life • COI Coach</div>
          <div class="main-title">Centers of Influence Coach</div>
          <div class="sub-title">
            A simple helper to find real COIs in your area and build a focused COI strategy.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_col2:
    st.markdown(
        """
        <div class="card-soft">
          <div style="font-weight:600; margin-bottom:0.3rem;">How this works</div>
          <div style="font-size:0.9rem; color:#4b5563;">
            • Choose a path below.<br>
            • Answer a few short questions.<br>
            • The COI Coach runs live web search and returns real COIs.<br><br>
            <span style="font-size:0.82rem; color:#6b7280;">
              This is a prototype. Always verify COI details and follow NYL compliance.
            </span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# =========================================
# PATH SELECTION
# =========================================

st.markdown(
    """
    <div class="card">
      <div style="font-weight:600; margin-bottom:0.35rem;">Select your path</div>
      <div style="font-size:0.9rem; color:#4b5563;">
        Pick one to start. The questions for that path will appear below.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

path_col1, path_col2 = st.columns(2)

with path_col1:
    if st.button("1️⃣ Personalized COI Strategy with COI List", key="btn_path_a"):
        st.session_state.selected_path = "A"

    st.markdown(
        """
        <div class="card-soft">
          <div style="font-size:0.9rem; color:#111827;">
            Short intake (6 questions). You’ll get:
          </div>
          <ul style="font-size:0.88rem; color:#4b5563; margin-top:0.2rem; padding-left:1.1rem;">
            <li>COI Intelligence Report</li>
            <li>First batch of 20–25 real COIs</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with path_col2:
    if st.button("2️⃣ Quick COI Lookup", key="btn_path_b"):
        st.session_state.selected_path = "B"

    st.markdown(
        """
        <div class="card-soft">
          <div style="font-size:0.9rem; color:#111827;">
            Enter your ZIP + COI type and go straight to a COI list.
          </div>
          <ul style="font-size:0.88rem; color:#4b5563; margin-top:0.2rem; padding-left:1.1rem;">
            <li>No strategy report</li>
            <li>20–25 COIs in your chosen category</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# =========================================
# PATH A UI (FULL WIDTH, QUESTIONS MATCH .TXT)
# =========================================

if st.session_state.selected_path == "A":

    st.markdown("#### 1️⃣ Path A — Personalized COI Strategy with COI List")

    with st.form("path_a_form"):
        st.markdown("### Intake (Q1–Q6)")

        # Q1/6 — What is your main ZIP code?
        st.markdown(
            '<div class="qblock">'
            '<div class="qblock-title">Q1/6 — What is your main ZIP code?</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        q1_zip = st.text_input("", placeholder="e.g., 07302")

        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)

        # Q2/6 — Which target segments fit your clients’ market?
        st.markdown(
            '<div class="qblock">'
            '<div class="qblock-title">Q2/6 — Which target segments fit your clients’ market?</div>'
            '<div class="qblock-help">'
            'This helps identify which types of clients you naturally attract. '
            'You can use segments like Young Families, Mid-Career Families, Affluent Pre-Retirees, '
            'or add your own niche segments.'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        q2_segments = st.text_area(
            "",
            placeholder="e.g., Young Families, Affluent Mid-Career Families, French-speaking expats, small business owners",
            height=60,
        )

        with st.expander("Reference: common NYL target segments"):
            st.markdown(
                """
                | Segment                      | Age Range | Typical triggers and needs                                      |
                |-----------------------------|-----------|------------------------------------------------------------------|
                | Young Childfree             | 24–44     | New jobs, relationships, early career cash-flow changes         |
                | Young Families              | 25–44     | New babies, home purchase, childcare, education planning        |
                | Mid-Career Families         | 35–54     | Job changes, caring for parents, children’s education decisions |
                | Affluent Mid-Career Families| 35–54     | Higher income, stock comp, new homes, complex tax situations    |
                | Affluent Pre-Retirees       | 55+       | Retirement readiness, downsizing, income planning               |
                | Affluent Retirees           | 65+       | Income stability, healthcare, estate planning                   |
                """
            )

        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)

        # Q3/6 — Which life events are most common in your clients’ lives?
        helper_text = "Examples: new baby, home purchase / move, job change, stock comp, immigration / relocation, education decisions."
        if q2_segments:
            helper_text += " Tailor this to the segments you listed."

        st.markdown(
            '<div class="qblock">'
            '<div class="qblock-title">Q3/6 — Which life events are most common in your clients’ lives?</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        q3_events = st.text_area(
            "",
            placeholder="e.g., New baby, relocation, new job with RSUs, daycare/private school decisions",
            help=helper_text,
            height=60,
        )

        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)

        # Q4/6 — Are there communities or affinity groups you work closely with?
        st.markdown(
            '<div class="qblock">'
            '<div class="qblock-title">Q4/6 — Are there communities or affinity groups you work closely with?</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        q4_communities = st.text_area(
            "",
            placeholder="e.g., French expat community, faith community, local parent groups, LGBTQ+, veterans",
            height=60,
        )

        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)

        # Q5/6 — What is your past professional background?
        st.markdown(
            '<div class="qblock">'
            '<div class="qblock-title">Q5/6 — What is your past professional background?</div>'
            '<div class="qblock-help">(You may include roles and company names.)</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        q5_background = st.text_area(
            "",
            placeholder="e.g., Former CPA at Deloitte, corporate finance, NYC tech sales",
            height=70,
        )

        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)

        # Q6/6 — What warm networks do you already have?
        st.markdown(
            '<div class="qblock">'
            '<div class="qblock-title">Q6/6 — What warm networks do you already have?</div>'
            '<div class="qblock-help">'
            'Examples: former colleagues, parent groups, alumni, small business owners.'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        q6_networks = st.text_area(
            "",
            placeholder="e.g., Former colleagues, alumni network, daycare parents, chamber of commerce",
            height=70,
        )

        submit_a = st.form_submit_button("Generate Intelligence Report & First COI Batch")

    if submit_a:
        if not q1_zip:
            st.warning("Please enter at least your main ZIP code to run Path A.")
        else:
            with st.spinner("Generating your Intelligence Report and first COI batch..."):
                st.session_state.path_a_result = run_path_a_model(
                    q1_zip=q1_zip,
                    q2_segments=q2_segments,
                    q3_events=q3_events,
                    q4_communities=q4_communities,
                    q5_background=q5_background,
                    q6_networks=q6_networks,
                )

    if st.session_state.path_a_result:
        st.markdown("#### 🧠 Intelligence Report & First COI Batch")
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(st.session_state.path_a_result)
        st.markdown("</div>", unsafe_allow_html=True)

# =========================================
# PATH B UI (FULL WIDTH)
# =========================================

elif st.session_state.selected_path == "B":

    st.markdown("#### 2️⃣ Path B — Quick COI Lookup")

    with st.form("path_b_form"):
        st.markdown("### Quick lookup inputs")

        # ZIP
        st.markdown(
            '<div class="qblock">'
            '<div class="qblock-title">ZIP code</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        zip_b = st.text_input("", placeholder="e.g., 07302")

        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)

        # COI type
        st.markdown(
            '<div class="qblock">'
            '<div class="qblock-title">COI type</div>'
            '</div>',
            unsafe_allow_html=True,
        )
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
        )

        st.markdown('<div class="qsep"></div>', unsafe_allow_html=True)

        # Extra context
        st.markdown(
            '<div class="qblock">'
            '<div class="qblock-title">Optional: extra context about your clients or focus</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        extra_context = st.text_area(
            "",
            placeholder="e.g., French-speaking expat professionals, tech employees with stock comp, small business owners",
            height=70,
        )

        submit_b = st.form_submit_button("Find COIs Now")

    if submit_b:
        if not zip_b:
            st.warning("Please enter a ZIP code to run Path B.")
        else:
            with st.spinner("Finding COIs in your area..."):
                st.session_state.path_b_result = run_path_b_model(
                    zip_code=zip_b,
                    coi_type=coi_type,
                    extra_context=extra_context,
                )

    if st.session_state.path_b_result:
        st.markdown("#### 📋 COI List – First Batch")
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(st.session_state.path_b_result)
        st.markdown("</div>", unsafe_allow_html=True)

# =========================================
# IDLE STATE (NO PATH SELECTED)
# =========================================

else:
    st.write("Choose **Path 1** or **Path 2** above to get started.")
