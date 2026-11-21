import streamlit as st

from src.data_loader import load_schemes
from src.prediction import load_model
from src.profile_form import profile_form
from src.recommendation import recommend
from src.visualization import scheme_details, show_checks

st.title("Scheme recommendations")
st.write("Answer the questions you can. Reviewed eligibility checks come first, and an ML relevance score ranks schemes within each status.")
st.caption("The model learned initial screening patterns from synthetic profiles. The score is a ranking signal.")
schemes = load_schemes()
for scheme in schemes:
    st.markdown(f'[{scheme["name"]} requirements]({scheme["source"]})')
submitted, profile = profile_form(schemes, recommendation=True)
if submitted:
    if not any(value is not None for value in profile.values()):
        st.warning("Answer at least one question to get recommendations.")
    else:
        try:
            model = st.cache_resource(load_model)()
            for scheme, score, status, checks in recommend(model, profile, schemes):
                with st.expander(f'{scheme["category"]} · {scheme["name"]}', expanded=True):
                    st.caption(f"Synthetic-model relevance score: {score:.0%}")
                    scheme_details(scheme)
                    show_checks(status, checks)
        except FileNotFoundError:
            st.error("Train the model from the VS Code terminal with python -m src.train_model.")
        except ValueError as error:
            st.error(str(error))