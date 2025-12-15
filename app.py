import os
import streamlit as st
from openai import OpenAI

# =========================================
# CONFIG
# =========================================

st.set_page_config(
    page_title="Centers of Influence Coach",
    page_icon="🧭",
    layout="wide"
)

# --- DARK THEME + CARD STYLES ---
CUSTOM_CSS = """
<style>
/* Global */
body, .stApp {
    background-color: #050611;
    color: #f5f5f7;
}

/* Main containers */
.main-title {
    font-size: 1.9rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}
.sub-title {
    font-size: 0.95rem;
    opacity: 0.8;
}

/* Cards */
.card {
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1.0rem;
    background: radial-gradient(circle at top left, #1c2333 0, #050611 55%);
    border: 1px solid rgba(255,255,255,0.06);
}
.card-soft {
    border-radius: 14px;
    padding: 1rem 1.1rem;
    margin-bottom: 0.75rem;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(148, 163, 184, 0.3);
}
.card-header {
    font-weight: 600;
    font-size: 1.0rem;
    margin-bottom: 0.35rem;
}
.small-label {
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #a5b4fc;
    margin-bottom: 0.15rem;
}

/* Buttons */
.stButton > button {
    border-radius: 999px !important;
    padding: 0.6rem 1.4rem !important;
    border: 1px solid rgba(148,163,184,0.7) !important;
    background: linear-gradient(135deg, #1d4ed8, #4f46e5) !important;
    color: #f9fafb !important;
    font-weight: 600 !important;
}
.stButton > button:hover {
    filter: brightness(1.08);
}

/* Path selector buttons */
.path-button {
    width: 100%;
    text-align: left;
}
.path-pill {
    font-size: 0.8rem;
    opacity: 0.8;
}

/* Inputs tweaks */
textarea, input, select {
    border-radius: 10px !important;
}

/* Results area */
.result-card {
    border-radius: 16px;
    padding: 1.0rem 1.2rem;
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid rgba(148, 163, 184, 0.3);
}
.result-title {
    font-weight: 600;
    font-size: 1.0rem;
    margin-bottom: 0.4rem;
}
.section-divider {
    margin: 0.9rem 0;
    border-bottom: 1px solid rgba(148, 163, 184, 0.35);
}

/* Tables */
table {
    font-size: 0.9rem;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =========================================
# SYSTEM PROMPT (DO NOT CHANGE)
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
# MODEL-CALL WRAPPERS
# =========================================
# IMPORTANT:
# Paste your EXISTING model calls inside these functions
# WITHOUT changing the logic, prompt wording, tools, or model.


def run_path_a_model(q1_zip, q2_segments, q3_events, q4_communities, q5_background, q6_networks) -> str:
    """
    Wrapper for your EXISTING Path A OpenAI call.
    Paste your current implementation between the markers.
    It must return a markdown string with:
      - Intelligence Report
      - COI list table (20–25)
      - 'Would you like more COIs?' line
    """
    # >>> BEGIN ORIGINAL PATH A IMPLEMENTATION (KEEP LOGIC IDENTICAL) <<<
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
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
            ),
        },
    ]

    response = client.responses.create(
        model="gpt-5.1",
        input=messages,
        tools=[{"type": "web_search"}],
        max_output_tokens=2000,
    )

    # Extract text (adjust if your existing code uses a different access pattern)
    content_parts = []
    for item in response.output[0].content:
        if item.type == "output_text":
            content_parts.append(item.text)
    return "\n".join(content_parts)
    # >>> END ORIGINAL PATH A IMPLEMENTATION <<<


def run_path_b_model(zip_code, coi_type, extra_context) -> str:
    """
    Wrapper for your EXISTING Path B OpenAI call.
    Paste your current implementation between the markers.
    It must return a markdown string with:
      - COI list (20–25)
      - 'Would you like more COIs?' line
    """
    # >>> BEGIN ORIGINAL PATH B IMPLEMENTATION (KEEP LOGIC IDENTICAL) <<<
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
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
            ),
        },
    ]

    response = client.responses.create(
        model="gpt-5.1",
        input=messages,
        tools=[{"type": "web_search"}],
        max_output_tokens=1500,
    )

    content_parts = []
    for item in response.output[0].content:
        if item.type == "output_text":
            content_parts.append(item.text)
    return "\n".join(content_parts)
    # >>> END ORIGINAL PATH B IMPLEMENTATION <<<


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
            Find real Centers of Influence in your area and build a simple, tailored COI strategy.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_col2:
    st.markdown(
        """
        <div class="card-soft">
          <div class="card-header">How this demo works</div>
          <ul style="margin-left: -1rem; font-size: 0.86rem; opacity:0.9;">
            <li>Choose a path below.</li>
            <li>Answer a few short questions.</li>
            <li>The COI Coach runs live web search and returns real COIs.</li>
          </ul>
          <div style="font-size:0.78rem; opacity:0.7; margin-top:0.2rem;">
            This is a prototype. Always verify COI details and follow NYL compliance.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# =========================================
# PATH SELECTION CARD
# =========================================

st.markdown(
    """
    <div class="card">
      <div class="card-header">Select your path</div>
      <div style="font-size:0.9rem; opacity:0.85; margin-bottom:0.8rem;">
        Pick one to start. The questions for your path will appear below.
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
          <div class="path-pill">Path 1 • 3–5 minutes</div>
          <div style="font-size:0.88rem; margin-top:0.3rem;">
            Short intake (6 questions). You’ll get:
            <ul style="margin-left:-1rem;">
              <li>COI Intelligence Report</li>
              <li>First batch of 20–25 real COIs</li>
            </ul>
          </div>
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
          <div class="path-pill">Path 2 • ~1 minute</div>
          <div style="font-size:0.88rem; margin-top:0.3rem;">
            Enter your ZIP + COI type and go straight to
            a list of 20–25 COIs, no strategy report.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# =========================================
# PATH A FORM (Only if selected)
# =========================================

if st.session_state.selected_path == "A":
    left, right = st.columns([1.4, 1.1])

    with left:
        st.markdown("### 1️⃣ Path A — Personalized COI Strategy with COI List")

        with st.form("path_a_form"):
            st.markdown("#### Intake (Q1–Q6)")

            # Q1
            q1_zip = st.text_input("Q1 – Main ZIP code", placeholder="e.g., 07302")

            # Q2 with helper table
            st.markdown("Q2 – Target segments")
            st.markdown(
                """
                Use short labels like **Young Families**, **Mid-Career Families**, **Affluent Pre-Retirees**, or your own niches.
                """
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
                    """,
                    help="Internal NYL segmentation reference.",
                )

            # Q3
            st.markdown("Q3 – Common life events")
            helper_text = "Examples: new baby, home purchase, job change, stock comp, immigration, kids’ education decisions."
            if q2_segments:
                helper_text += " Tailor this to the segments you listed above."
            q3_events = st.text_area(
                "",
                placeholder="e.g., New baby, relocation, new job with RSUs, daycare/private school decisions",
                help=helper_text,
                height=60,
            )

            # Q4
            q4_communities = st.text_area(
                "Q4 – Communities / affinity groups",
                placeholder="e.g., French expat community, faith community, local parent groups, LGBTQ+, veterans",
                height=60,
            )

            # Q5
            q5_background = st.text_area(
                "Q5 – Advisor background (roles, industries, firms)",
                placeholder="e.g., Former CPA at Deloitte, corporate finance, NYC tech sales",
                height=70,
            )

            # Q6
            q6_networks = st.text_area(
                "Q6 – Warm networks already available",
                placeholder="e.g., Former colleagues, alumni network, daycare parents, chamber of commerce",
                height=70,
            )

            st.markdown("<br>", unsafe_allow_html=True)

            submit_a = st.form_submit_button("Generate Intelligence Report & First COI Batch")

        if submit_a:
            if not q1_zip:
                st.warning("Please enter at least your main ZIP code to run Path A.")
            else:
                with st.spinner("Generating your Intelligence Report and first COI batch…"):
                    result = run_path_a_model(
                        q1_zip=q1_zip,
                        q2_segments=q2_segments,
                        q3_events=q3_events,
                        q4_communities=q4_communities,
                        q5_background=q5_background,
                        q6_networks=q6_networks,
                    )
                    st.session_state.path_a_result = result

    with right:
        st.markdown("#### Path A Output")
        st.markdown(
            """
            <div class="card-soft">
              <div style="font-size:0.9rem;">
                Once you click the button, the COI Coach will:
                <ol style="margin-left:-0.8rem;">
                  <li>Summarize your focus in a COI Intelligence Report.</li>
                  <li>Run live web search.</li>
                  <li>Return 20–25 real COIs in a table with public contact only.</li>
                </ol>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.path_a_result:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown('<div class="result-title">🧠 Intelligence Report & First COI Batch</div>', unsafe_allow_html=True)
            st.markdown(st.session_state.path_a_result)
            st.markdown("</div>", unsafe_allow_html=True)


# =========================================
# PATH B FORM (Only if selected)
# =========================================

elif st.session_state.selected_path == "B":
    left, right = st.columns([1.4, 1.1])

    with left:
        st.markdown("### 2️⃣ Path B — Quick COI Lookup")

        with st.form("path_b_form"):
            zip_b = st.text_input("ZIP code", placeholder="e.g., 07302")

            coi_type = st.selectbox(
                "COI type",
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

            extra_context = st.text_area(
                "Optional: extra context about your clients or focus",
                placeholder="e.g., French-speaking expat professionals, tech employees with stock comp, small business owners",
                height=70,
            )

            submit_b = st.form_submit_button("Find COIs Now")

        if submit_b:
            if not zip_b:
                st.warning("Please enter a ZIP code to run Path B.")
            else:
                with st.spinner("Finding COIs in your area…"):
                    result = run_path_b_model(zip_code=zip_b, coi_type=coi_type, extra_context=extra_context)
                    st.session_state.path_b_result = result

    with right:
        st.markdown("#### Path B Output")
        st.markdown(
            """
            <div class="card-soft">
              <div style="font-size:0.9rem;">
                Path B skips the Intelligence Report and goes straight to:
                <ul style="margin-left:-1rem;">
                  <li>20–25 COIs in your chosen category</li>
                  <li>All centered on your ZIP (with broadening when needed)</li>
                  <li>Public business contact info only</li>
                </ul>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.path_b_result:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown('<div class="result-title">📋 COI List – First Batch</div>', unsafe_allow_html=True)
            st.markdown(st.session_state.path_b_result)
            st.markdown("</div>", unsafe_allow_html=True)


# =========================================
# IDLE STATE MESSAGE
# =========================================

else:
    st.markdown(
        """
        <div class="card-soft">
          <div class="card-header">Start by choosing a path</div>
          <div style="font-size:0.9rem; opacity:0.9;">
            • Path 1 builds a COI strategy and your first COI list.<br>
            • Path 2 jumps straight to a COI list based on ZIP and COI type.<br><br>
            Click one of the buttons above to begin.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
