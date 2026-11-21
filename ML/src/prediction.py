"""Load the locally trained artifact and calculate relevance scores."""
import joblib
import numpy as np
import pandas as pd

from src.data_loader import MODELS
from src.preprocessing import CATEGORICAL, FEATURES


def load_model():
    return joblib.load(MODELS / "recommendation.joblib")


def relevance_scores(model, profile, schemes):
    features = {key: profile.get(key) if profile.get(key) is not None else np.nan
                for key in FEATURES}
    rows = pd.DataFrame([dict(features, scheme=scheme["id"]) for scheme in schemes])
    rows[CATEGORICAL] = rows[CATEGORICAL].astype(object)
    return model.predict_proba(rows)[:, list(model.classes_).index(True)]