import streamlit as st
from openai import OpenAI

# ---------- BASIC PAGE SETUP ----------
st.set_page_config(page_title="COI Coach – Streamlit UI", layout="wide")

st.title("COI Coach – Centers of Influence Finder")
st.caption("Streamlit front-end using your COI System Rules with web search (Option B).")

# ---------- OPENAI CLIENT ----------
# Read API key from Streamlit secrets (set in Streamlit Cloud)
api_key = st.secrets.get("OPENAI_API_KEY", None)

if not api_key:
    st.error("OPENAI_API_KEY is not set in Streamlit secrets. Add it in the Streamlit Cloud settings.")
    st.stop()

client = OpenAI(api_key=api_key)

# ---------- SYSTEM PROMPT (BASED ON YOUR COI SYSTEM RULES) ----------
SYSTEM_PROMPT = """
You are **Centers of Influence Coach**, built for New York Life advisors and managers.

Your job is simple:
- Help advisors identify COI opportunities
- Help advisors find real COIs in their area using live web search
- Keep everything short, simple, and advisor-friendly

Tone and style:
- Short sentences
- Clear tables
- Minimal repetition
- Warm, human tone — never robotic

You operate in ONE main mode: “Find COIs in my area”
Inside that, you support two paths:
1) Path A — Personalized COI Strategy with COI List
2) Path B — Quick COI Lookup

SCOPE:
You ARE allowed to:
- Ask Q1–Q6 for Path A
- Build the COI Intelligence Report
- Automatically search for real COIs using web search
- Present clean tables
- Produce a final summary

You are NOT allowed to:
- Write outreach scripts
- Provide deep language or sales coaching
- Answer NYL product, underwriting, compensation, compliance, or investment questions
- Provide tax, legal, or market advice

If user asks about non-COI topics (products, markets, investments, etc.),
gently redirect them back to the COI workflow.

-------------------------
PATH A — PERSONALIZED COI STRATEGY (Q1–Q6)
-------------------------

You assume the Streamlit app already collected these answers:

Q1/6 – Main ZIP code
Q2/6 – Target segments
Q3/6 – Common life events
Q4/6 – Communities / affinity groups
Q5/6 – Advisor past professional background
Q6/6 – Warm networks already available

From these inputs, you MUST output, in order:

### 1) COI Intelligence Report

Include:
- A short intro paragraph (4–8 sentences) summarizing:
  - Who the advisor serves (location, key segments, communities)
  - The most relevant life events
  - Where COI leverage is strongest
- A **Client Focus Overview** table:

| Item | Summary |
|------|---------|
| Main Area | [ZIP] |
| Key Segments | [segments] |
| Life Events | [events] |
| Communities | [communities] |
| Background | [background] |
| Networks | [networks] |

### 2) COI Opportunity Themes

Write 3–5 bullet points. Use themes like:
- Financial & tax triggers (job change, cash-flow shifts, relocations, education costs)
- Housing & relocation (realtors, lenders, relocation specialists)
- Family & children professionals (pediatricians, OB-GYNs, schools)
- Background & networks (business bankers, consultants, professionals tied to advisor’s background)
- Community anchors (cultural, faith, immigrant, parent groups)

Each bullet should mention:
- A COI category (e.g., CPA, realtor, immigration attorney)
- Why that COI is high leverage for this advisor’s segments and events.

### 3) COI List – First Batch (20–25 COIs)

You MUST generate **between 20 and 25 rows** in a markdown table. Never fewer than 20 unless web results are extremely limited after broadening.

Table header MUST be:

| Name | Role/Specialty | Organization / Link | Why They Fit |

Behavior rules:
- Use **web_search** to find real COIs whenever possible.
- Focus on public-facing professionals and organizations:
  - CPAs, tax advisors
  - Estate / immigration / family law attorneys
  - Realtors and mortgage lenders
  - Pediatricians / OB-GYNs / schools
  - Business bankers, consultants, career coaches
  - Community and cultural organizations
- Use the advisor’s ZIP as the center, then broaden:
  - Adjacent ZIPs
  - Nearby towns (5–10 miles)
  - Local directories, schools, hospitals, chambers, associations

Broaden logic:
- If initial narrowing yields fewer than 15 COIs:
  - Automatically broaden geography and categories
- Only deliver fewer than 10 if:
  - You broadened at least twice AND
  - You clearly say: “Limited results after broadening. Here’s what I found.”

Contact info (if you include it in “Organization / Link”):
- Only public business websites or public LinkedIn pages
- No personal phone numbers
- No personal emails

After the table, ALWAYS ask:

> **Would you like more COIs?**
> I can add more (up to 125 total), or we can finish with your summary.

If the user wants more:
- In this Streamlit version, just say something like:
  “In this demo, I generate only the first batch. In a full version, I would continue up to 125 COIs.”

-------------------------
PATH B — QUICK COI LOOKUP
-------------------------

For the quick lookup (Path B), you skip the full Intelligence Report and Themes.
Instead, you ONLY output:

### COI List – First Batch (20–25 COIs)

In the SAME markdown table format:

| Name | Role/Specialty | Organization / Link | Why They Fit |

You still:
- Use web_search
- Focus on the advisor’s ZIP and optional COI type hint
- Broaden when needed to 20–25 COIs
- Follow the same compliance and public-info rules

-------------------------
COMPLIANCE & FINAL NOTES
-------------------------

- Only use public business contact info (websites, LinkedIn, office phone).
- No personal cell numbers or personal emails.
- No product, tax, legal, investment, or market advice.
- Encourage advisors to independently verify every COI.
- Use the advisor’s community info ONLY if they provided it.

Always keep responses structured, warm, and concise.
"""

# ---------- HELPER FUNCTIONS TO CALL THE MODEL WITH WEB SEARCH ----------

def call_coi_model_full(advisor_inputs: dict) -> str:
    """
    Path A:
    - Intelligence Report
    - Opportunity Themes
    - COI List (20–25 rows)
    Uses gpt-5.1 + web_search.
    """
    user_prompt = f"""
Advisor inputs:

- ZIP code: {advisor_inputs.get('zip')}
- Target segments: {advisor_inputs.get('segments')}
- Common life events: {advisor_inputs.get('life_events')}
- Communities / affinity groups: {advisor_inputs.get('communities')}
- Advisor background: {advisor_inputs.get('background')}
- Warm networks: {advisor_inputs.get('networks')}

Using the structure described in the SYSTEM PROMPT, generate:

1) COI Intelligence Report
2) COI Opportunity Themes
3) COI List – First Batch (20–25 COIs) as a markdown table.
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
    Path B:
    Quick COI lookup, only returns the COI table (20–25 rows).
    Uses gpt-5.1 + web_search.
    """
    user_prompt = f"""
Quick COI lookup.

- ZIP code: {zip_code}
- COI type focus (hint): {coi_type_hint}

Please SKIP the intelligence report and themes.
ONLY output:

### COI List – First Batch (20–25 COIs)

as a markdown table with:
| Name | Role/Specialty | Organization / Link | Why They Fit |

If possible, generate between 20 and 25 rows. Never fewer than 20 unless web results remain limited even after broadening.

Extra context from advisor:
{extra_context}
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

# ---------- UI: MODE SWITCH ----------
mode = st.sidebar.radio(
    "Choose mode",
    ["Personalized COI Strategy (Path A)", "Quick COI Lookup (Path B)"]
)

# =====================================================
# PATH A – Personalized COI Strategy (Q1–Q6 + MODEL)
# =====================================================
if mode.startswith("Personalized"):
    st.header("Path A – Personalized COI Strategy")

    with st.form("coi_strategy_form"):
        zip_code_a = st.text_input("Q1/6 – Main ZIP code", value="07302")

        segments = st.multiselect(
            "Q2/6 – Key client segments",
            [
                "Young Childfree",
                "Young Families",
                "Mid-Career Families",
                "Affluent Mid-Career Families",
                "Affluent Pre-Retirees",
                "Affluent Retirees",
            ],
            default=["Affluent Mid-Career Families"]
        )

        life_events = st.multiselect(
            "Q3/6 – Common life events",
            [
                "New baby",
                "Home purchase / move",
                "Job change / stock compensation",
                "Kids’ education decisions",
                "Cash-flow / tax changes",
                "Immigration / relocation",
            ],
            default=["Home purchase / move", "Job change / stock compensation"]
        )

        communities = st.text_input(
            "Q4/6 – Communities / affinity groups",
            placeholder="e.g., French expats, tech professionals..."
        )

        background = st.text_area(
            "Q5/6 – Past professional background",
            placeholder="e.g., Former auditor, strong CPA network..."
        )

        networks = st.text_area(
            "Q6/6 – Warm networks you already have",
            placeholder="e.g., former colleagues, alumni, parent groups..."
        )

        submitted = st.form_submit_button("Generate Intelligence Report & COI List")

    if submitted:
        advisor_inputs = {
            "zip": zip_code_a,
            "segments": ", ".join(segments) if segments else "None specified",
            "life_events": ", ".join(life_events) if life_events else "None specified",
            "communities": communities or "None specified",
            "background": background or "None specified",
            "networks": networks or "None specified",
        }

        with st.spinner("Calling COI model with web search..."):
            result_markdown = call_coi_model_full(advisor_inputs)

        st.subheader("Model Output")
        st.markdown(result_markdown)

# ==========================================
# PATH B – Quick COI Lookup (TABLE ONLY)
# ==========================================
else:
    st.header("Path B – Quick COI Lookup")

    col1, col2 = st.columns(2)
    with col1:
        zip_code_b = st.text_input("ZIP code", value="07302")
    with col2:
        coi_type = st.selectbox(
            "COI Type (hint for the model)",
            ["Any", "CPA / Tax Advisor", "Attorney", "Realtor", "Mortgage Lender", "Pediatrician", "Community / Cultural"]
        )

    extra_context = st.text_area(
        "Optional extra context",
        placeholder="e.g., Focus on affluent mid-career families moving into this area."
    )

    if st.button("Find COIs Now"):
        coi_hint = coi_type if coi_type != "Any" else "Any COIs that match my core market."

        with st.spinner("Calling COI model with web search..."):
            result_markdown_b = call_coi_model_quick(
                zip_code=zip_code_b,
                coi_type_hint=coi_hint,
                extra_context=extra_context or ""
            )

        st.subheader("Model Output")
        st.markdown(result_markdown_b)
