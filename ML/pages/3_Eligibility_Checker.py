import streamlit as st

from src.data_loader import load_schemes
from src.eligibility_checker import evaluate, validate_profile
from src.profile_form import profile_form
from src.visualization import scheme_details, show_checks

st.title("Eligibility checker")
schemes = {scheme["name"]: scheme for scheme in load_schemes()}
requested = st.query_params.get("scheme")
names = list(schemes)
index = next((i for i, option in enumerate(names) if schemes[option]["id"] == requested), 0)
name = st.selectbox("Select a scheme", names, index=index)
scheme = schemes[name]
st.caption(f'{scheme["category"]} · {scheme["state"]}')
st.write(scheme["purpose"])
scheme_details(scheme)
with st.expander("Reviewed requirements"):
    for _, _, _, description in scheme["rules"]:
        st.write(f"• {description}")
submitted, profile = profile_form([scheme])
if submitted:
    try:
        show_checks(*evaluate(scheme, validate_profile(profile)))
    except ValueError as error:
        st.error(str(error))