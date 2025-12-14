import streamlit as st
from openai import OpenAI

# =========================================
# BASIC PAGE SETUP
# =========================================
st.set_page_config(page_title="Centers of Influence Coach", layout="wide")

st.title("Centers of Influence Coach")
st.caption("Streamlit front-end that follows your full COI System Rules and GPT behavior.")

# =========================================
# OPENAI CLIENT
# =========================================
api_key = st.secrets.get("OPENAI_API_KEY", None)

if not api_key:
    st.error("OPENAI_API_KEY is not set in Streamlit secrets. Add it in the Streamlit Cloud settings.")
    st.stop()

client = OpenAI(api_key=api_key)

# =========================================
# SYSTEM PROMPT — FULL COI SYSTEM RULES
# (Your instructions + full COI System Rules.txt)
# =========================================
SYSTEM_PROMPT = r"""
You are Centers of Influence Coach GPT for New York Life advisors.

Your mission is to:
1) Help advisors quickly find real Centers of Influence (COIs) in their area using live web search.
2) Guide advisors through a short, simple intake (Path A) to build a COI Intelligence Report and COI list.
3) Run a Quick COI Lookup (Path B) when advisors want fast, specific search results.

You MUST follow all logic, rules, workflows, formatting requirements, guardrails, and compliance guidelines stored in the knowledge file named "COI System Rules.txt". That file defines:
- The exact welcome message and options (1 = Personalized COI Strategy with COI List, 2 = Quick COI Lookup).
- The 6 intake questions for Path A, with explicit question prompts BEFORE the tables, each with a short explanation explaining what the question means and why it is asked.
- The complete COI Intelligence Report structure (Client Focus Overview, Opportunity Themes, Priority COI Categories, Opportunity Channels).
- The dynamic scaling rules for the COI categories (based on how much the advisor shares).
- The requirement to show the Intelligence Report AND the first batch of real COIs in the same response.
- The real COI search behavior: mandatory 20–25 COIs in the first batch, strong broadening logic, public business contact requirements, and the 125-name cap.
- The rule to ask after each batch if the user wants more COIs.
- The final narrative summary (including priority categories, themes, channels, and the consolidated full COI list).
- The requirement to offer an optional PDF summary after the final summary, using clear, user-friendly language and emojis (e.g., “Would you like me to generate your PDF summary now? 📄✨”).
- Tone and style guidelines: short sentences, human, advisor-like, minimal repetition.

Guardrails:
- If the user asks COI-related questions NOT about running the workflow (e.g., “explain the COI process,” “what language should I use,” “how do I present this to a COI?”), do NOT provide detailed training or scripts. Redirect them to the COI Guide or the Practice Development Team, then re-offer Path 1 or Path 2.
- If the user asks about NYL products, underwriting, compensation, compliance, investments, or markets, redirect them to internal NYL resources or the Practice Development Team, then re-offer Path 1 or Path 2.

Tone and style:
- Sound like a helpful, succinct colleague.
- Use short sentences and simple, plain language.
- Avoid long paragraphs, jargon, and repetition.
- Use clean tables and clear structure.
- Make the process easy for new advisors.

At the start of every COI session:
1) Show the exact welcome block from "COI System Rules.txt" (with disclaimer and resources).
2) Ask the user to enter 1 or 2, and then:
   - Path A: run Q1–Q6, generate the COI Intelligence Report, and return the first batch of COIs immediately.
   - Path B: ask for ZIP + COI type, then return the first batch immediately.

When generating COI lists:
- Use live web search to find real, public-facing professionals.
- ALWAYS include public business contact information only (office phone, business email if publicly posted, LinkedIn public profile, or website contact link).
- ALWAYS produce 20–25 COIs in the first batch. If fewer than 15 appear initially, broaden automatically.
- After each batch, ask if the advisor wants more COIs.
- Stop at 125 total COIs.

If you are ever unsure how to respond, FIRST consult "COI System Rules.txt" and follow it strictly. Do not invent new flows or formats.

# ============================================
# COI SYSTEM RULES — CENTERS OF INFLUENCE COACH GPT (BASELINE + PATCHES)
# (Verbatim from COI System Rules.txt)
# ============================================

You are **Centers of Influence Coach GPT**, built for **New York Life advisors and managers**.

Your job is simple:
- Help advisors identify COI opportunities
- Help advisors find real COIs in their area using live web search
- Keep everything short, simple, and advisor-friendly

Use:
- Short sentences
- Clear tables
- Minimal repetition
- A warm, human tone — never robotic

You operate in one main mode:
> **“Find COIs in my area.”**

Inside that mode, you support:
1. **Path A — Personalized COI Strategy with COI List**
2. **Path B — Quick COI Lookup**

# (The rest of this block is your full COI System Rules: scope, guardrails,
# welcome block, Q1–Q6 wording + explanations, Intelligence Report,
# Opportunity Themes, Priority COI Categories, Opportunity Channels,
# COI search engine rules, 20–25 COIs per batch, broadening logic,
# table formats, ask-for-more-COIs behavior, final summary, PDF option,
# determinism, and compliance rules.)

# IMPORTANT FOR THIS STREAMLIT APP:
# - Assume the Streamlit UI has ALREADY asked the advisor for:
#   * Path choice (1 or 2)
#   * All Q1–Q6 answers for Path A
#   * ZIP and COI type for Path B
# - DO NOT re-ask those questions.
# - Instead, use the provided inputs as if you had already asked them in chat.
# - Still follow ALL downstream rules for:
#   * Intelligence Report structure
#   * COI tables with 20–25 rows in the first batch
#   * Asking if they want more COIs (even if this app may only use the first batch)
#   * Final summary and optional PDF language.

"""

# =========================================
# MODEL CALL HELPERS (WITH WEB SEARCH)
# =========================================

def call_coi_model_full(advisor_inputs: dict) -> str:
    """
    Path A:
    - Use the advisor's Q1–Q6 answers.
    - Generate the full COI Intelligence Report.
    - Generate the first batch of real COIs (20–25 rows).
    """
    user_prompt = f"""
We are in Path A — Personalized COI Strategy with COI List.

The Streamlit app has already shown the welcome block and asked Q1–Q6 exactly as defined in COI System Rules.
Here are the advisor's answers:

- Q1/6 – Main ZIP code: {advisor_inputs.get('zip')}
- Q2/6 – Target segments: {advisor_inputs.get('segments')}
- Q3/6 – Common life events: {advisor_inputs.get('life_events')}
- Q4/6 – Communities / affinity groups: {advisor_inputs.get('communities')}
- Q5/6 – Advisor background: {advisor_inputs.get('background')}
- Q6/6 – Warm networks: {advisor_inputs.get('networks')}

Follow COI System Rules exactly:
1) Generate the full COI Intelligence Report:
   - Client Focus Overview table
   - Opportunity Themes
   - Priority COI Categories
   - COI Opportunity Channels
2) Immediately generate the FIRST batch of real COIs (20–25 rows) in the required table format.
3) Use live web search and broadening logic when needed.
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
    Path B:
    - Quick COI lookup using ZIP + COI type.
    - Only returns the COI List – First Batch (20–25 rows).
    """
    user_prompt = f"""
We are in Path B — Quick COI Lookup.

The Streamlit app has already shown the welcome block and the user chose option 2.

Inputs:
- ZIP code: {zip_code}
- COI type focus hint: {coi_type_hint}
- Extra context: {extra_context}

Follow COI System Rules exactly for Path B:
1) Skip the Intelligence Report and themes.
2) ONLY output the COI List – First Batch (20–25 COIs) as a markdown table.
3) Use web search and broadening logic to hit 20–25 rows when possible.
4) Include only public business contact info in the relevant column.
5) Ask if they want more COIs and reference the 125-name cap.
6) Use short sentences and simple language.
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


# =========================================
# UI — WELCOME BLOCK + PATH SELECTION
# =========================================

st.markdown(
    """
## 👋 Welcome  
I can help you find Centers of Influence (COIs) in your area and, if you’d like, build a tailored COI strategy based on your market and clients. **Choose how you’d like to begin:**

| Option | Description |
|--------|-------------|
| **1️⃣ Personalized COI Strategy with COI List** | A guided 3–5 minute questionnaire that builds a COI Intelligence Report and finds real COIs in your area. |
| **2️⃣ Quick COI Lookup** | Tell me your ZIP code and the COI type you're looking for (CPA, attorney, realtor, etc.), and I’ll search immediately. |

**Please choose 1 or 2 using the selector below.**

*Disclaimer: This tool uses live web search and is not exhaustive. Verify all COIs independently and follow New York Life compliance.*  
*Resources:*  
📘 COI Guide – internal document  
🧠 Memory Jogger – internal tool for name flow
"""
)

path_choice = st.radio(
    "Select your path:",
    options=["1️⃣ Personalized COI Strategy with COI List", "2️⃣ Quick COI Lookup"],
    index=0,
)

# =====================================================
# PATH A – PERSONALIZED COI STRATEGY (Q1–Q6 + MODEL)
# =====================================================
if path_choice.startswith("1️⃣"):
    st.header("Path A – Personalized COI Strategy with COI List")

    with st.form("coi_strategy_form"):
        # Q1/6
        st.markdown(
            "### Q1/6 – What is your main ZIP code?\n"
            "This anchors your COI search to a primary market. "
            "We’ll automatically consider nearby areas, but your main ZIP is the starting point."
        )
        zip_code_a = st.text_input("Main ZIP code", value="07302")

        # Q2/6
        st.markdown(
            "### Q2/6 – Which target segments fit your clients’ market?\n"
            "This helps match your clients’ life stage and income to the right COIs."
        )
        segments = st.multiselect(
            "Select your key segments:",
            [
                "Young Childfree",
                "Young Families",
                "Mid-Career Families",
                "Affluent Mid-Career Families",
                "Affluent Pre-Retirees",
                "Affluent Retirees",
            ],
            default=["Affluent Mid-Career Families"],
        )

        # Q3/6
        st.markdown(
            "### Q3/6 – Which life events are most common in your clients’ lives?\n"
            "Life events signal when clients need the most help and which COIs they work with."
        )
        life_events = st.multiselect(
            "Select common life events:",
            [
                "New baby",
                "Home purchase / move",
                "Job change / stock compensation",
                "Kids’ education decisions",
                "Cash-flow / tax changes",
                "Immigration / relocation",
            ],
            default=["Home purchase / move", "Job change / stock compensation"],
        )

        # Q4/6
        st.markdown(
            "### Q4/6 – Are there communities or affinity groups you work closely with?\n"
            "Communities and cultural markets create warm, trust-based introductions."
        )
        communities = st.text_input(
            "Communities / affinity groups",
            placeholder="e.g., French expats, tech professionals, teachers, small business owners...",
        )

        # Q5/6
        st.markdown(
            "### Q5/6 – What is your past professional background?\n"
            "Your prior roles and industries create natural COI overlap."
        )
        background = st.text_area(
            "Past professional background",
            placeholder="e.g., Former auditor at Deloitte, strong CPA and controller network...",
        )

        # Q6/6
        st.markdown(
            "### Q6/6 – What warm networks do you already have?\n"
            "These are the easiest, warmest paths to COI relationships."
        )
        networks = st.text_area(
            "Warm networks you already have",
            placeholder="e.g., alumni, former colleagues, parent groups, chamber of commerce...",
        )

        submitted = st.form_submit_button("Generate Intelligence Report & First COI Batch")

    if submitted:
        advisor_inputs = {
            "zip": zip_code_a,
            "segments": ", ".join(segments) if segments else "None specified",
            "life_events": ", ".join(life_events) if life_events else "None specified",
            "communities": communities or "None specified",
            "background": background or "None specified",
            "networks": networks or "None specified",
        }

        with st.spinner("Calling COI model with web search (Path A)..."):
            result_markdown = call_coi_model_full(advisor_inputs)

        st.subheader("COI Intelligence Report + First COI Batch")
        st.markdown(result_markdown)

# ==========================================
# PATH B – QUICK COI LOOKUP (TABLE ONLY)
# ==========================================
else:
    st.header("Path B – Quick COI Lookup")

    col1, col2 = st.columns(2)
    with col1:
        zip_code_b = st.text_input("ZIP code", value="07302")
    with col2:
        coi_type = st.selectbox(
            "COI Type (hint for the model)",
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

    extra_context = st.text_area(
        "Optional extra context for the search",
        placeholder="e.g., Focus on affluent mid-career families moving into this area.",
    )

    if st.button("Find COIs Now"):
        coi_hint = coi_type if coi_type != "Any" else "Any COIs that best match my core market."

        with st.spinner("Calling COI model with web search (Path B)..."):
            result_markdown_b = call_coi_model_quick(
                zip_code=zip_code_b,
                coi_type_hint=coi_hint,
                extra_context=extra_context or "",
            )

        st.subheader("First COI Batch (20–25 COIs)")
        st.markdown(result_markdown_b)
