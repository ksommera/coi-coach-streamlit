import streamlit as st

st.set_page_config(page_title="COI Coach – Streamlit UI", layout="wide")

st.title("COI Coach – Centers of Influence Finder")
st.caption("Streamlit front-end for your COI workflow (Path A & Path B).")

# Sidebar mode switch
mode = st.sidebar.radio(
    "Choose mode",
    ["Personalized COI Strategy (Path A)", "Quick COI Lookup (Path B)"]
)

# =====================================================
# PATH A – Personalized COI Strategy (Q1–Q6)
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

        submitted = st.form_submit_button("Generate Intelligence Report (demo)")

    if submitted:
        st.success("Demo Intelligence Report (no AI yet).")

        st.subheader("Client Focus Overview (Demo)")
        st.markdown(f"""
        **Main Area:** {zip_code_a}  
        **Segments:** {", ".join(segments) or "—"}  
        **Life Events:** {", ".join(life_events) or "—"}  
        **Communities:** {communities or "—"}  
        **Background:** {background or "—"}  
        **Networks:** {networks or "—"}  
        """)

        st.info("Later, this is where your AI-generated COI Intelligence Report + COI list will appear.")

# ==========================================
# PATH B – Quick COI Lookup (simple demo)
# ==========================================
else:
    st.header("Path B – Quick COI Lookup")

    col1, col2 = st.columns(2)
    with col1:
        zip_code_b = st.text_input("ZIP code", value="07302")
    with col2:
        coi_type = st.selectbox(
            "COI Type",
            ["CPA / Tax Advisor", "Attorney", "Realtor", "Mortgage Lender", "Pediatrician"]
        )

    if st.button("Find COIs Now (demo)"):
        st.info(f"Showing demo COIs for {coi_type} near {zip_code_b}.")
        st.write("In the future, this section will show your AI-generated COI table.")
