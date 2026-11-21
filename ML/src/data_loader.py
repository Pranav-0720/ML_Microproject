"""Load the reviewed rule catalog and profile the raw Kaggle files."""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DATA = ROOT / "data" / "processed"
MODELS = ROOT / "models"


def load_schemes():
    return json.loads((DATA / "schemes.json").read_text(encoding="utf-8"))


def load_catalog():
    return pd.read_csv(RAW / "indian_government_schemes.csv")


def profile_raw():
    reports = []
    for path in sorted(RAW.glob("*.csv")):
        frame = pd.read_csv(path)
        blank = frame.isna() | frame.astype(str).apply(
            lambda col: col.str.strip().isin({"", "NA", "N/A", "NaN", "NULL"})
        )
        reports.append({
            "file": path.name,
            "rows": len(frame),
            "columns": len(frame.columns),
            "duplicate_rows": int(frame.duplicated().sum()),
            "missing": {key: int(value) for key, value in blank.sum().items()},
        })
    (DATA / "raw_audit.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")
    return reports


if __name__ == "__main__":
    print(json.dumps(profile_raw(), indent=2))