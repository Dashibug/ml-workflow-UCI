from __future__ import annotations

from sklearn.metrics import (
    accuracy_score, confusion_matrix, f1_score, log_loss,
    precision_score, recall_score, roc_auc_score,
)


def calculate_metrics(model, x, y) -> dict:
    predictions = model.predict(x)
    positive_scores = model.predict_proba(x)[:, 1]
    if len(set(y)) != 2:
        raise ValueError("ROC-AUC requires both target classes in evaluation split")
    return {
        "n_rows": int(len(y)),
        "positive_rate": round(float(y.mean()), 6),
        "accuracy": round(float(accuracy_score(y, predictions)), 6),
        "precision": round(float(precision_score(y, predictions, zero_division=0)), 6),
        "recall": round(float(recall_score(y, predictions, zero_division=0)), 6),
        "f1": round(float(f1_score(y, predictions, zero_division=0)), 6),
        "roc_auc": round(float(roc_auc_score(y, positive_scores)), 6),
        "log_loss": round(float(log_loss(y, positive_scores, labels=[0, 1])), 6),
        "confusion_matrix": confusion_matrix(y, predictions, labels=[0, 1]).tolist(),
    }
