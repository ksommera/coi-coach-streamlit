import streamlit as st
from openai import OpenAI

# ---------- BASIC PAGE SETUP ----------
st.set_page_config(page_title="COI Coach – Streamlit UI", layout="wide")

st.title("COI Coach – Centers of Influence Finder")
st.caption("Streamlit front-end for your COI workflow (Path A & Path B).")

# ---------- OPENAI CLIENT ----------
# Read API key from Streamlit secrets (set in Streamlit Cloud)
api_key = st.secrets.get("OPENAI_API_KEY", None)

if not api_key:
    st.error("OPENAI_API_KEY is not set in Streamlit secrets. Please add it in the Streamlit Cloud settings.")
    st.stop()

client = OpenAI(api_key=api_key)

# ---------- SYSTEM PROMPT (COI RULES – SHORT VERSION) ----------
SYSTEM_PROMPT = """
You are COI Coach, an assistant for financial advisors.
Your job is to:
- Help advisors think about their COI strategy based on their market.
- Suggest COI opportunity themes.
- List real-world COI profiles that would make sense (types of professionals).

SCOPE:
- Only talk about COIs (CPAs, attorneys, realtors, lenders, community leaders, etc.).
- Do NOT give tax, legal, investment, product or compliance advice.
- Do not mention specific NYL products.

OUTPUT FORMAT FOR FULL STRATEGY (PATH A):
Return these three sections in order:

### 1) COI Intelligence Report
A short narrative (4–8 sentences) summarizing:
- Who the advisor serves (location, segments, communities)
- What life events matter most
- Where their biggest COI leverage points are

### 2) COI Opportunity Themes
3–5 bullet points summarizing:
- The COI categories that should be highest priority (CPAs, realtors, attorneys, etc.)
- Why they match the advisor’s segments, life events, and communities

### 3) COI List – First Batch (20–25 COIs)
A markdown table with this header:
| Name | Role/Specialty | Organization / Link | Why They Fit |

List 20–25 rows when possible. Use realistic-sounding names and organizations,
based on the advisor’s ZIP and focus. If you cannot reliably find real names,
you may use plausible placeholders but keep them professional.

For QUICK LOOKUP (PATH B):
Skip sections 1 and 2. ONLY return the markdown table under:

### COI List – First Batch (20–25 COIs)
with the same columns as above.
"""

def call_coi_model_full(advisor_inputs: dict) -> str:
    """
    Call the model for the full Path A workflow:
    Intelligence Report + Opportunity Themes + COI List (20–25 rows).
    Returns markdown text.
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
    response = client.responses.create(
        model="gpt-5.1",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.output_text

def call_coi_model_quick(zip_code: str, coi_type_hint: str, extra_context: str) -> str:
    """
    Call the model for the quick lookup (Path B) to ONLY output a table
    of 20–25 COIs.
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

{extra_context}
"""
    response = client.responses.create(
        model="gpt-5.1",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.output_text

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

        with st.spinner("Calling COI model..."):
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
        coi_hint = coi_type if coi_type != "Any" else "Any COIs that match affluent and family markets."

        with st.spinner("Calling COI model..."):
            result_markdown_b = call_coi_model_quick(
                zip_code=zip_code_b,
                coi_type_hint=coi_hint,
                extra_context=extra_context or ""
            )

        st.subheader("Model Output")
        st.markdown(result_markdown_b)
