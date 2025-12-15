import streamlit as st
from openai import OpenAI

# =========================
# BASIC PAGE SETUP
# =========================
st.set_page_config(page_title="Centers of Influence Coach", layout="wide")

st.title("Centers of Influence Coach")
st.caption("Streamlit front-end that follows your COI System Rules and GPT behavior.")

# =========================
# SIMPLE CUSTOM STYLING
# =========================
st.markdown(
    """
    <style>
    body {
        background-color: #020617;
        color: #e5e7eb;
    }
    .coi-card {
        padding: 1rem 1.4rem;
        border-radius: 0.9rem;
        border: 1px solid #1f2937;
        background: #020617;
        margin-bottom: 1.2rem;
    }
    .coi-question {
        padding: 1.1rem 1.4rem;
        border-radius: 0.9rem;
        border: 1px solid #1f2937;
        background: #020617;
        margin-bottom: 0.6rem;
    }
    .stButton > button {
        border-radius: 999px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        border: 1px solid #1f2937;
    }
    /* Left button = blue */
    div[data-testid="column"]:nth-of-type(1) .stButton > button {
        background: linear-gradient(90deg, #1d4ed8, #3b82f6);
        color: #f9fafb;
    }
    /* Right button = dark */
    div[data-testid="column"]:nth-of-type(2) .stButton > button {
        background: #111827;
        color: #e5e7eb;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# OPENAI CLIENT
# =========================
api_key = st.secrets.get("OPENAI_API_KEY", None)

if not api_key:
    st.error("OPENAI_API_KEY is not set in Streamlit secrets. Add it in the Streamlit Cloud settings.")
    st.stop()

client = OpenAI(api_key=api_key)

# =========================
# SYSTEM PROMPT (HYBRID)
# =========================
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

# =========================
# MODEL CALL HELPERS
# =========================

def call_coi_model_full(advisor_inputs: dict) -> str:
    """
    Path A: Intelligence Report + first COI batch (20–25).
    """
    user_prompt = f"""
We are in Path A — Personalized COI Strategy with COI List.

Here are the advisor's answers:

- Q1 – Main ZIP code: {advisor_inputs.get('zip')}
- Q2 – Target segments: {advisor_inputs.get('segments')}
- Q3 – Common life events: {advisor_inputs.get('life_events')}
- Q4 – Communities / affinity groups: {advisor_inputs.get('communities')}
- Q5 – Advisor background: {advisor_inputs.get('background')}
- Q6 – Warm networks: {advisor_inputs.get('networks')}

Follow the COI System Rules strictly:

1) Generate the COI Intelligence Report:
   - Client Focus Overview (table)
   - COI Opportunity Themes
   - Priority COI Categories
   - COI Opportunity Channels
2) Immediately generate the first batch of real COIs (20–25 rows) as a markdown table with the required columns.
3) Use live web search and broadening logic to reach 20–25 when possible.
4) Ask if they want more COIs and mention the 125-name cap.
5) Use short sentences and simple language.
"""

    try:
        response = client.responses.create(
            model="gpt-5.1",
            tools=[{"type": "web_search"}],
            tool_choice="auto",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.output_text
    except Exception as e:
        return f"**Error calling OpenAI (Path A):** `{e}`"


def call_coi_model_quick(zip_code: str, coi_type_hint: str, extra_context: str) -> str:
    """
    Path B: Quick lookup, only the first COI batch (20–25).
    """
    user_prompt = f"""
We are in Path B — Quick COI Lookup.

Inputs:
- ZIP code: {zip_code}
- COI type focus: {coi_type_hint}
- Extra context: {extra_context}

Follow the COI System Rules strictly for Path B:

1) Skip the Intelligence Report and themes.
2) ONLY output the COI List – First Batch (20–25 COIs) as a markdown table with the required columns.
3) Use live web search and broadening logic to hit 20–25 rows when possible.
4) Ask if they want more COIs and mention the 125-name cap.
5) Use short sentences and simple language.
"""

    try:
        response = client.responses.create(
            model="gpt-5.1",
            tools=[{"type": "web_search"}],
            tool_choice="auto",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.output_text
    except Exception as e:
        return f"**Error calling OpenAI (Path B):** `{e}`"


# =========================
# PATH SELECTION – BUTTONS
# =========================

st.markdown(
    """
<div class="coi-card">
  <h3 style="margin-bottom:0.4rem;">👋 Welcome</h3>
  <p style="margin-top:0; font-size:0.95rem;">
    I can help you find Centers of Influence (COIs) in your area and, if you’d like,
    build a tailored COI strategy based on your market and clients.
  </p>

  <table style="width:100%; font-size:0.9rem; border-collapse:collapse; margin-top:0.4rem;">
    <tr>
      <th style="text-align:left; padding:0.25rem 0;">Option</th>
      <th style="text-align:left; padding:0.25rem 0;">Description</th>
    </tr>
    <tr>
      <td style="padding:0.25rem 0; vertical-align:top;"><b>1️⃣ Personalized COI Strategy with COI List</b></td>
      <td style="padding:0.25rem 0;">A guided 3–5 minute questionnaire that builds a COI Intelligence Report and finds real COIs in your area.</td>
    </tr>
    <tr>
      <td style="padding:0.25rem 0; vertical-align:top;"><b>2️⃣ Quick COI Lookup</b></td>
      <td style="padding:0.25rem 0;">Fast COI search by ZIP and COI type (CPA, attorney, realtor, etc.).</td>
    </tr>
  </table>

  <p style="font-size:0.8rem; margin-top:0.6rem; opacity:0.75;">
    Disclaimer: This tool uses live web search and is not exhaustive. Verify all COIs independently and follow New York Life compliance.<br/>
    Resources: COI Guide, Memory Jogger, Practice Development Team.
  </p>
</div>
""",
    unsafe_allow_html=True,
)

if "selected_path" not in st.session_state:
    st.session_state.selected_path = None

st.markdown("### How would you like to start?")

col_a, col_b = st.columns(2)
with col_a:
    if st.button("1️⃣ Personalized COI Strategy with COI List", use_container_width=True):
        st.session_state.selected_path = "A"
with col_b:
    if st.button("2️⃣ Quick COI Lookup", use_container_width=True):
        st.session_state.selected_path = "B"

st.divider()

# =========================
# PATH A – FULL STRATEGY
# =========================
if st.session_state.selected_path == "A":
    st.subheader("Path A – Personalized COI Strategy with COI List")

    with st.form("coi_strategy_form"):

        # Q1
        st.markdown(
            """
            <div class="coi-question">
                <h4>🔷 Q1/6 – What is your main ZIP code?</h4>
                <p>This anchors your COI search to a primary market. We’ll automatically consider nearby areas.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        zip_code_a = st.text_input("Main ZIP code", value="07302")

        st.markdown("<br/>", unsafe_allow_html=True)

        # Q2 – helper table + free text
        st.markdown(
            """
            <div class="coi-question">
                <h4>🔷 Q2/6 — Which target segments fit your clients’ market?</h4>
                <p>This helps identify <b>who you naturally attract</b>. Each segment points us toward
                different COI types (CPAs, realtors, attorneys, etc.).</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
| Segment                      | Age Range | Typical Needs                                |
|-----------------------------|-----------|----------------------------------------------|
| Young Childfree             | 24–44     | New job, recently engaged or married         |
| Young Families              | 25–44     | New baby, new house, job change              |
| Mid-Career Families         | 35–54     | Job changes, loss, caregiving, kids’ education |
| Affluent Mid-Career Families| 35–54     | Job changes, new home purchase               |
| Affluent Pre-Retirees       | 55+       | Approaching retirement, reviewing finances   |
| Affluent Retirees           | 65+       | In retirement, updating plans                |

You can also add **niche segments** (e.g., tech professionals, expats, small business owners, teachers, medical professionals).

👉 Write the segment(s) that best fit your clients, plus any niche focus you want me to factor in.
"""
        )

        segments_text = st.text_area(
            "Your key segments:",
            placeholder="Example: Affluent Mid-Career Families and Pre-Retirees, plus French expats in Jersey City.",
        )

        st.markdown("<br/>", unsafe_allow_html=True)

        # Q3 – examples based on Q2 + free text
        st.markdown(
            """
            <div class="coi-question">
                <h4>🔷 Q3/6 — What life events or financial triggers show up most for your clients?</h4>
                <p>This identifies <b>why</b> clients come to you, which shapes the COI categories we prioritize.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        segments_lower = (segments_text or "").lower()
        suggested_events = []

        if any(s in segments_lower for s in ["pre-retiree", "pre retiree", "retiree"]):
            suggested_events.extend(
                [
                    "Approaching retirement",
                    "Downsizing / relocating",
                    "Large tax concerns",
                    "Inheritance or sudden wealth",
                ]
            )

        if any(s in segments_lower for s in ["mid-career", "mid career", "young families", "families"]):
            suggested_events.extend(
                [
                    "Home purchase / move",
                    "Job change / stock compensation",
                    "Kids’ education decisions",
                    "Cash-flow / tax changes",
                ]
            )

        if any(s in segments_lower for s in ["expat", "immigr", "relocat"]):
            suggested_events.extend(
                [
                    "Immigration / relocation",
                    "Cross-border tax questions",
                ]
            )

        if not suggested_events:
            suggested_events = [
                "Approaching retirement",
                "Sale of a business",
                "Downsizing / relocating",
                "Inheritance or sudden wealth",
                "Executive comp / stock decisions",
                "Caring for aging parents",
                "Divorce later in life",
                "Large tax concerns",
            ]

        st.markdown("**Examples include:**")
        st.markdown("\n".join([f"- {e}" for e in suggested_events]))

        st.markdown(
            "\n👉 Which triggers apply most to your clients? List the top life events or triggers you see."
        )

        life_events_text = st.text_area(
            "Your key life events / triggers:",
            placeholder="Example: Home purchase or move, job change with stock, immigration, large tax bills.",
        )

        st.markdown("<br/>", unsafe_allow_html=True)

        # Q4
        st.markdown(
            """
            <div class="coi-question">
                <h4>🔷 Q4/6 – Are there communities or affinity groups you work closely with?</h4>
                <p>Communities and cultural markets create warm, trust-based introductions.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        communities = st.text_input(
            "Communities / affinity groups:",
            placeholder="e.g., French expats, tech professionals, teachers, small business owners...",
        )

        st.markdown("<br/>", unsafe_allow_html=True)

        # Q5
        st.markdown(
            """
            <div class="coi-question">
                <h4>🔷 Q5/6 – What is your past professional background?</h4>
                <p>Your prior roles and industries create natural COI overlap.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        background = st.text_area(
            "Past professional background:",
            placeholder="e.g., Former auditor at Deloitte, strong CPA and controller network...",
        )

        st.markdown("<br/>", unsafe_allow_html=True)

        # Q6
        st.markdown(
            """
            <div class="coi-question">
                <h4>🔷 Q6/6 – What warm networks do you already have?</h4>
                <p>These are the easiest, warmest paths to COI relationships.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        networks = st.text_area(
            "Warm networks you already have:",
            placeholder="e.g., alumni, former colleagues, parent groups, chamber of commerce...",
        )

        st.markdown("<br/>", unsafe_allow_html=True)

        submitted = st.form_submit_button("🚀 Generate Intelligence Report & First COI Batch", use_container_width=True)

    if submitted:
        advisor_inputs = {
            "zip": zip_code_a,
            "segments": segments_text or "None specified",
            "life_events": life_events_text or "None specified",
            "communities": communities or "None specified",
            "background": background or "None specified",
            "networks": networks or "None specified",
        }

        with st.spinner("Calling COI model with web search (Path A)..."):
            result_markdown = call_coi_model_full(advisor_inputs)

        st.subheader("COI Intelligence Report + First COI Batch")
        st.markdown(result_markdown)

# =========================
# PATH B – QUICK LOOKUP
# =========================
elif st.session_state.selected_path == "B":
    st.subheader("Path B – Quick COI Lookup")

    st.markdown(
        "Use this when you want **fast names** in a specific area, without running the full strategy."
    )

    st.markdown("<br/>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        zip_code_b = st.text_input("ZIP code:", value="07302")
    with col2:
        coi_type = st.selectbox(
            "COI Type (hint for the model):",
            [
                "Any",
                "CPA / Tax Advisor",
                "Attorney",
                "Realtor",
                "Mortgage Lender",
                "Pediatrician",
                "Community / Cultural Leader",
                "Business Banker",
                "School / Education",
            ],
        )

    st.markdown("<br/>", unsafe_allow_html=True)

    extra_context = st.text_area(
        "Optional extra context for the search:",
        placeholder="Example: Focus on affluent mid-career families moving into this area.",
    )

    if st.button("🔍 Find COIs Now", use_container_width=True):
        coi_hint = coi_type if coi_type != "Any" else "Any COIs that best match my core market."

        with st.spinner("Calling COI model with web search (Path B)..."):
            result_markdown_b = call_coi_model_quick(
                zip_code=zip_code_b,
                coi_type_hint=coi_hint,
                extra_context=extra_context or "",
            )

        st.subheader("First COI Batch (20–25 COIs)")
        st.markdown(result_markdown_b)

# =========================
# NO PATH YET
# =========================
else:
    st.info("Choose **Path 1** or **Path 2** above to get started.")
