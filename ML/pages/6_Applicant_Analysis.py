import json

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import DATA, MODELS
from src.visualization import PALETTE, bar, style_chart

st.title("Applicant patterns")
st.info("K-Means groups simulated applicant profiles. Use these groupings to explore the synthetic data.")
if not (DATA / "synthetic_clusters.csv").exists() or not (MODELS / "metrics.json").exists():
    st.warning("Run python -m src.train_model to generate cluster results.")
    st.stop()

frame = pd.read_csv(DATA / "synthetic_clusters.csv", dtype={"cluster": str})
report = json.loads((MODELS / "metrics.json").read_text(encoding="utf-8"))["clustering"]
variance = sum(report["variance_explained"])
a, b, c = st.columns(3)
a.metric("Clusters", report["clusters"], border=True)
b.metric("Silhouette", f'{report["silhouette"]:.2f}', border=True)
c.metric("Variance in 2 PCs", f"{variance:.0%}", border=True)
left, right = st.columns(2)
counts = frame.cluster.value_counts().sort_index().rename_axis("Cluster").reset_index(name="Profiles")
with left.container(border=True):
    st.plotly_chart(bar(counts, "Cluster", "Profiles", title="Cluster distribution"), theme=None)
with right.container(border=True):
    scatter = px.scatter(frame, x="PC1", y="PC2", color="cluster", opacity=.65,
                         color_discrete_sequence=PALETTE, title="PCA projection of synthetic profiles")
    st.plotly_chart(style_chart(scatter), theme=None)
st.subheader("Cluster characteristics")
summary = frame.assign(student=frame.student.eq("Yes") * 100,
                       land=frame.land.eq("Yes") * 100, lpg=frame.lpg.eq("Yes") * 100)
by_group = summary.groupby("cluster").agg(
    Profiles=("age", "size"), Median_age=("age", "median"), Median_income=("income", "median"),
    Students_pct=("student", "mean"), Landholders_pct=("land", "mean"), LPG_pct=("lpg", "mean"))
st.dataframe(by_group.round(1))
st.caption("The PCA chart compresses the feature space to two dimensions. The table shows which profile characteristics distinguish each cluster.")