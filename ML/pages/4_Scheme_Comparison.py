import pandas as pd
import streamlit as st

from src.data_loader import load_schemes

st.title("Compare schemes")
schemes = {scheme["name"]: scheme for scheme in load_schemes()}
names = st.multiselect("Choose two or three schemes", list(schemes),
                       default=list(schemes)[:2], max_selections=3)
if len(names) < 2:
    st.info("Select at least two schemes to compare.")
else:
    rows = []
    for name in names:
        scheme = schemes[name]
        rows.append({"Scheme": name, "Coverage": scheme["state"], "Purpose": scheme["purpose"],
                     "Benefits": scheme["benefit"],
                     "Eligibility": " • ".join(rule[3] for rule in scheme["rules"]),
                     "Documents": scheme["documents"], "Application": scheme["apply"]})
    st.dataframe(pd.DataFrame(rows), hide_index=True, row_height=120,
                 column_config={"Application": st.column_config.LinkColumn(display_text="Open portal"),
                                "Eligibility": st.column_config.TextColumn(width="large")})
    for name in names:
        st.markdown(f'[{name} application portal]({schemes[name]["apply"]})')