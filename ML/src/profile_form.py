import streamlit as st

QUESTIONS = {
    "student": "Are you currently enrolled as a student?",
    "land": "Does your family own cultivable land?",
    "lpg": "Does anyone in your household already have an LPG connection?",
    "woman": "Are you a woman? (PM Ujjwala requirement)",
    "deprivation": "Does your household qualify under the official PM Ujjwala deprivation declaration?",
    "domicile": "Do you have Maharashtra domicile?",
    "kisan_excluded": "Does any PM-KISAN exclusion apply to your family?",
    "land_verified": "Has the authority confirmed your land records, ownership timing and any regional exception?",
    "dte_verified": "Have you confirmed the remaining DTE requirements against MahaDBT?",
}


def profile_form(schemes, recommendation=False):
    fields = {field for scheme in schemes for field, *_ in scheme["rules"]}
    profile = {}
    with st.form("citizen_profile", border=True):
        st.caption("You can leave questions unanswered. Use official requirements for questions about exemptions and declarations.")
        left, right = st.columns(2)
        if "age" in fields:
            profile["age"] = left.number_input("Age in years", 0, 120, value=None, step=1)
        if "income" in fields:
            profile["income"] = right.number_input(
                "Annual family income (₹)", 0, 1_000_000_000, value=None, step=1)
        for index, (key, label) in enumerate(QUESTIONS.items()):
            if key in fields:
                column = left if index % 2 == 0 else right
                profile[key] = column.selectbox(label, ["Yes", "No"], index=None,
                                                placeholder="Unanswered", key=key)
        submitted = st.form_submit_button("Find schemes" if recommendation else "Check eligibility",
                                          type="primary")
    return submitted, profile