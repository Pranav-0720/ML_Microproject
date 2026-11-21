"""Fit preprocessing within each cross-validation fold."""
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer, OneHotEncoder, StandardScaler

NUMERIC = ["age", "income"]
CATEGORICAL = ["student", "land", "lpg"]
FEATURES = NUMERIC + CATEGORICAL


def preprocessing(include_scheme=False, normalize=False):
    categorical = CATEGORICAL + (["scheme"] if include_scheme else [])
    columns = ColumnTransformer([
        ("numeric", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), NUMERIC),
        ("categorical", make_pipeline(SimpleImputer(strategy="most_frequent"),
                                      OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
         categorical),
    ])
    return make_pipeline(columns, Normalizer()) if normalize else columns