import json

from matplotlib.figure import Figure
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st

from src.data_loader import MODELS
from src.visualization import PALETTE, style_chart

st.title("Model performance")
st.info("Synthetic screening experiment. These metrics measure recovery of simplified screening patterns in simulated data.")
path = MODELS / "metrics.json"
if not path.exists():
    st.warning("Run python -m src.train_model to generate evaluation results.")
    st.stop()

report = json.loads(path.read_text(encoding="utf-8"))
rows = pd.DataFrame(report["results"]).T
a, b, c = st.columns(3)
a.metric("Selected by mean CV F1", report["winner"], border=True)
b.metric("Training profiles", report["train_profiles"], border=True)
c.metric("Held-out profiles", report["test_profiles"], border=True)
columns = {"accuracy": "Test accuracy", "precision": "Test precision", "recall": "Test recall",
           "f1": "Test F1", "cv_f1": "Validation CV F1", "train_cv_f1": "Training CV F1"}
st.dataframe(rows[list(columns)].astype(float).round(4).rename(columns=columns))
st.caption("Compare training and validation F1 to look for overfitting. Low scores on both can indicate underfitting.")
algorithm = st.selectbox("Inspect an algorithm", rows.index, index=list(rows.index).index(report["winner"]))
result = report["results"][algorithm]
a, b = st.columns(2)
labels = ["No initial match", "Initial match"]
figure = Figure(figsize=(5.5, 3.6), layout="constrained")
axes = figure.subplots()
sns.heatmap(result["matrix"], annot=True, fmt="d", cmap="GnBu", cbar=False,
            xticklabels=labels, yticklabels=labels, ax=axes)
axes.set(xlabel="Predicted", ylabel="Actual", title="Held-out confusion matrix")
axes.tick_params(axis="y", labelrotation=0)
with a.container(border=True):
    st.pyplot(figure)
with b.container(border=True):
    folds = px.line(x=list(range(1, 6)), y=result["folds"], markers=True, range_y=[0, 1],
                    labels={"x": "Cross-validation fold", "y": "F1"},
                    color_discrete_sequence=PALETTE, title="Validation F1 by fold")
    st.plotly_chart(style_chart(folds), theme=None)
with st.expander("Selected hyperparameters"):
    st.json(result["parameters"])