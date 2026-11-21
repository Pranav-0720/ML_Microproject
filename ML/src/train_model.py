"""Train models to rank schemes by synthetic initial screening relevance."""
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import GridSearchCV, GroupKFold, GroupShuffleSplit
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from threadpoolctl import threadpool_limits

from src.clustering import analyze
from src.data_loader import DATA, MODELS, load_schemes, profile_raw
from src.eligibility_checker import INELIGIBLE, evaluate
from src.preprocessing import FEATURES, NUMERIC, preprocessing


def synthetic_profiles(samples=1600):
    rng = np.random.default_rng(42)
    age = rng.integers(15, 76, samples)
    profiles = pd.DataFrame({
        "age": age,
        "income": np.clip(rng.lognormal(12.65, 0.85, samples).astype(int), 0, 4_000_000),
        "student": np.where(rng.random(samples) < np.where(age < 27, .75, .08), "Yes", "No"),
        "land": rng.choice(["Yes", "No"], samples, p=[.32, .68]),
        "lpg": rng.choice(["Yes", "No"], samples, p=[.62, .38]),
    }).drop_duplicates().reset_index(drop=True)
    profiles.index.name = "synthetic_profile_id"
    return profiles


def main():
    profile_raw()
    profiles = synthetic_profiles()
    # Labels come from the subset of reviewed checks represented by model features.
    # Missing model inputs are injected only after constructing the complete-data labels.
    rng = np.random.default_rng(7)
    noisy = profiles.astype(dict.fromkeys(NUMERIC, float))
    for field in FEATURES:
        noisy.loc[rng.random(len(noisy)) < .04, field] = np.nan
    rows = []
    for scheme in load_schemes():
        labels = [evaluate(scheme, row)[0] != INELIGIBLE for row in profiles.to_dict("records")]
        rows.append(noisy.assign(scheme=scheme["id"], relevant=labels))
    pairs = pd.concat(rows).reset_index()
    pairs.to_csv(DATA / "synthetic_training.csv", index=False)

    X = pairs[FEATURES + ["scheme"]]
    y, groups = pairs["relevant"], pairs["synthetic_profile_id"]
    train, test = next(GroupShuffleSplit(test_size=.2, random_state=42).split(X, y, groups))
    candidates = {
        "Logistic Regression": (LogisticRegression(max_iter=1000), {"C": [.1, 1, 10]}),
        "Decision Tree": (DecisionTreeClassifier(random_state=42), {"max_depth": [3, 6, 12]}),
        "Random Forest": (RandomForestClassifier(random_state=42, n_estimators=80),
                          {"max_depth": [4, 8, None], "min_samples_leaf": [2, 6]}),
        "k-Nearest Neighbors": (KNeighborsClassifier(), {"n_neighbors": [3, 7, 15]}),
    }
    searches = {}
    for name, (model, grid) in candidates.items():
        pipeline = Pipeline([("prep", preprocessing(include_scheme=True)), ("model", model)])
        search = GridSearchCV(pipeline, {"model__" + key: value for key, value in grid.items()},
                              cv=GroupKFold(n_splits=5), scoring="f1",
                              return_train_score=True, error_score="raise")
        searches[name] = search.fit(X.iloc[train], y.iloc[train], groups=groups.iloc[train])
    winner = max(searches, key=lambda name: searches[name].best_score_)
    results = {}
    for name, search in searches.items():
        pred = search.predict(X.iloc[test])
        precision, recall, f1, _ = precision_recall_fscore_support(
            y.iloc[test], pred, average="binary", zero_division=0)
        index = search.best_index_
        cv = search.cv_results_
        results[name] = {
            "accuracy": accuracy_score(y.iloc[test], pred), "precision": precision,
            "recall": recall, "f1": f1, "cv_f1": search.best_score_,
            "train_cv_f1": cv["mean_train_score"][index],
            "folds": [cv[f"split{i}_test_score"][index] for i in range(5)],
            "parameters": search.best_params_,
            "matrix": confusion_matrix(y.iloc[test], pred, labels=[False, True]).tolist(),
        }
    with threadpool_limits(limits=2):
        clustered, cluster_metrics = analyze(profiles)
    clustered.to_csv(DATA / "synthetic_clusters.csv", index=False)
    joblib.dump(searches[winner].best_estimator_, MODELS / "recommendation.joblib")
    report = {"winner": winner, "profiles": len(profiles), "pairs": len(pairs),
              "train_profiles": int(groups.iloc[train].nunique()),
              "test_profiles": int(groups.iloc[test].nunique()),
              "results": results, "clustering": cluster_metrics}
    (MODELS / "metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    with threadpool_limits(limits=2):
        main()