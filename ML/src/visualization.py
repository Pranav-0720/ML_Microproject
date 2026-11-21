"""Shared chart styling and scheme display components."""
import pandas as pd
import plotly.express as px
import streamlit as st

from src.eligibility_checker import INELIGIBLE, POTENTIAL, UNKNOWN


PALETTE = ["#07796E", "#446BC6", "#AE6731", "#8B5CB2", "#327DA1"]


def style_chart(figure, height=345):
    figure.update_layout(
        height=height, margin=dict(l=12, r=16, t=45 if figure.layout.title.text else 8, b=18),
        font=dict(family="Arial, sans-serif", color="#243950", size=12),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="#13283B", font_color="#FFFFFF"),
    )
    figure.update_xaxes(gridcolor="#E4EDF1", zeroline=False, automargin=True)
    figure.update_yaxes(gridcolor="#E4EDF1", zeroline=False, automargin=True)
    return figure


def bar(data, x, y, **kwargs):
    figure = px.bar(data, x=x, y=y, color_discrete_sequence=PALETTE, **kwargs)
    figure.update_traces(marker_cornerradius=4)
    if kwargs.get("orientation") == "h":
        figure.update_yaxes(title=None, showgrid=False)
    else:
        figure.update_xaxes(showgrid=False)
    return style_chart(figure)


def scheme_details(scheme):
    left, right = st.columns(2)
    with left:
        st.markdown("**Benefits**")
        st.write(scheme["benefit"])
        st.link_button("Official application portal", scheme["apply"])
    with right:
        st.markdown("**Application documents**")
        st.write(scheme["documents"])
        st.markdown(f'[Official requirements]({scheme["source"]}) · Reviewed {scheme["reviewed"]}')


def show_checks(status, checks):
    tones = {POTENTIAL: "positive", INELIGIBLE: "negative", UNKNOWN: "pending"}
    st.html(f'<div class="sf-status sf-{tones[status]}" role="status">{status}</div>')
    st.dataframe(pd.DataFrame(checks, columns=["Requirement", "Result"]), hide_index=True)
    if any(result == "Unknown" for _, result in checks):
        st.caption("Verify items marked Unknown against the official requirements.")