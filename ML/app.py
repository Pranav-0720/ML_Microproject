from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Scheme Finder", page_icon="🇮🇳", layout="wide")
style = Path(__file__).with_name("assets") / "dashboard.css"
st.html(style)

with st.sidebar:
    st.html("""
        <div class="sf-brand">
            <span class="sf-brand-mark" aria-hidden="true">SF</span>
            <div><strong>Scheme Finder</strong><small>India · Welfare schemes</small></div>
        </div>
    """)

navigation = st.navigation({
    "Discover": [
        st.Page("pages/1_Home.py", title="Home", icon=":material/space_dashboard:", default=True),
        st.Page("pages/2_Scheme_Recommendation.py", title="Recommendations", icon=":material/explore:"),
        st.Page("pages/3_Eligibility_Checker.py", title="Eligibility checker", icon=":material/fact_check:"),
        st.Page("pages/4_Scheme_Comparison.py", title="Compare schemes", icon=":material/compare_arrows:"),
    ],
    "Machine learning": [
        st.Page("pages/5_Model_Performance.py", title="Model performance", icon=":material/monitoring:"),
        st.Page("pages/6_Applicant_Analysis.py", title="Applicant patterns", icon=":material/scatter_plot:"),
    ],
})
with st.sidebar:
    st.divider()
    st.caption("Educational screening only. Confirm eligibility and application requirements on the official government portal.")
navigation.run()