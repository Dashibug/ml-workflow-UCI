from __future__ import annotations

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.common import CATEGORICAL_COLUMNS, FEATURE_COLUMNS, NUMERIC_COLUMNS, TARGET


def make_pipeline(config: dict) -> Pipeline:
    numeric = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    categorical = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("one_hot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    preprocess = ColumnTransformer([
        ("numerical", numeric, NUMERIC_COLUMNS),
        ("categorical", categorical, CATEGORICAL_COLUMNS),
    ], remainder="drop")

    model_cfg = config["model"]
    name = model_cfg["name"]
    params = dict(model_cfg.get("params") or {})
    if name == "logistic_regression":
        params.setdefault("random_state", int(config.get("random_state", 42)))
        estimator = LogisticRegression(**params)
    elif name == "hist_gradient_boosting":
        params.setdefault("random_state", int(config.get("random_state", 42)))
        estimator = HistGradientBoostingClassifier(**params)
    else:
        raise ValueError(f"Unsupported model: {name!r}")
    return Pipeline([("preprocess", preprocess), ("model", estimator)])


def split_xy(frame):
    missing = (set(FEATURE_COLUMNS) | {TARGET}) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if not frame[TARGET].isin([0, 1]).all():
        raise ValueError("Target must consist only of 0 and 1")
    return frame[FEATURE_COLUMNS], frame[TARGET].astype(int)
