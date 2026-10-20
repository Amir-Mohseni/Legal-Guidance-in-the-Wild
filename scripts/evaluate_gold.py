"""Recompute the gold-set results of Legal Guidance in the Wild from frozen predictions.

Reads supplementary/evaluation/per_example_predictions.parquet, prints the
guidance, topic/cascade, and McNemar tables, and exits with status 1 if any
value differs from supplementary/evaluation/summary_metrics.csv.

    python scripts/evaluate_gold.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score

ROOT = Path(__file__).resolve().parents[1]
EVALUATION = ROOT / "supplementary" / "evaluation"
N_BOOTSTRAP = 2000
SEED = 42

FULL_SYSTEMS = {
    "TF-IDF + LogReg": "tf_idf_logreg",
    "ModernBERT-base": "modernbert_base",
    "ModernBERT-large": "modernbert_large",
}
PREFIX_SYSTEMS = {
    "TF-IDF + LogReg (prefix)": "tfidf_prefix",
    "ModernBERT-base (prefix)": "modernbert_base_prefix",
    "ModernBERT-large (prefix)": "modernbert_large_prefix",
}


def macro_f1(y_true, y_pred, labels=None):
    return f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)


def bootstrap_ci(y_true, y_pred, labels=None):
    rng = np.random.default_rng(SEED)
    n = len(y_true)
    scores = []
    for _ in range(N_BOOTSTRAP):
        idx = rng.integers(0, n, size=n)
        scores.append(macro_f1(y_true[idx], y_pred[idx], labels))
    low, high = np.quantile(scores, [0.025, 0.975])
    return low, high


def guidance_row(preds, key):
    y_true = preds["gold_guidance"].to_numpy(dtype=int)
    y_pred = preds[f"{key}_guidance_prediction"].to_numpy(dtype=int)
    low, high = bootstrap_ci(y_true, y_pred)
    return {
        "accuracy": (y_true == y_pred).mean(),
        "macro_f1": macro_f1(y_true, y_pred),
        "macro_f1_ci_low": low,
        "macro_f1_ci_high": high,
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "positive_f1": f1_score(y_true, y_pred, zero_division=0),
        "auprc": average_precision_score(y_true, preds[f"{key}_guidance_probability"]),
        "fp": int(((y_pred == 1) & (y_true == 0)).sum()),
        "fn": int(((y_pred == 0) & (y_true == 1)).sum()),
    }


def labelled_row(y_true, y_pred):
    labels = sorted(set(y_true))
    low, high = bootstrap_ci(y_true, y_pred, labels)
    return {
        "accuracy": (y_true == y_pred).mean(),
        "macro_f1": macro_f1(y_true, y_pred, labels),
        "macro_f1_ci_low": low,
        "macro_f1_ci_high": high,
    }


def topic_cascade_rows(preds, key):
    positive = preds["gold_guidance"].to_numpy()
    guidance = preds[f"{key}_guidance_prediction"].to_numpy()
    topic = preds[f"{key}_topic_prediction"].to_numpy()
    gold_topic = preds["gold_topic"].to_numpy()
    errors = {
        "fp": int((guidance & ~positive).sum()),
        "fn": int((~guidance & positive).sum()),
        "topic": int((guidance & positive & (topic != gold_topic)).sum()),
    }
    errors["all"] = sum(errors.values())
    oracle = labelled_row(gold_topic[positive], topic[positive])
    cascade = labelled_row(preds["gold_cascade"].to_numpy(), preds[f"{key}_cascade_prediction"].to_numpy())
    return oracle, cascade, errors


def mcnemar(correct_a, correct_b):
    a_only = int((correct_a & ~correct_b).sum())
    b_only = int((~correct_a & correct_b).sum())
    p = binomtest(a_only, a_only + b_only, 0.5).pvalue if a_only + b_only else 1.0
    return a_only, b_only, p


def significance_rows(preds):
    positive = preds["gold_guidance"]

    def correct(key, task):
        if task == "Guidance":
            return preds[f"{key}_guidance_prediction"] == positive
        if task == "Topic only":
            return preds.loc[positive, f"{key}_topic_prediction"] == preds.loc[positive, "gold_topic"]
        return preds[f"{key}_cascade_prediction"] == preds["gold_cascade"]

    comparisons = [
        ("Guidance", "ModernBERT-large", "TF-IDF + LogReg"),
        ("Guidance", "ModernBERT-large", "ModernBERT-base"),
        ("Guidance", "ModernBERT-large (prefix)", "ModernBERT-large"),
        ("Guidance", "ModernBERT-large (prefix)", "ModernBERT-base"),
        ("Topic only", "ModernBERT-large", "TF-IDF + LogReg"),
        ("Topic only", "ModernBERT-large", "ModernBERT-base"),
        ("Cascade", "ModernBERT-large", "TF-IDF + LogReg"),
        ("Cascade", "ModernBERT-large", "ModernBERT-base"),
    ]
    keys = FULL_SYSTEMS | PREFIX_SYSTEMS
    rows = []
    for task, a, b in comparisons:
        a_only, b_only, p = mcnemar(correct(keys[a], task), correct(keys[b], task))
        rows.append({"task": task, "comparison": f"{a} vs. {b}", "a_only": a_only, "b_only": b_only, "p": p})
    return pd.DataFrame(rows)


def check_gold_labels(preds):
    gold = pd.read_csv(ROOT / "annotations" / "gold_set.csv", usecols=["id", "seeks_legal_guidance", "primary_topic"])
    merged = preds.merge(gold, on="id", validate="one_to_one")
    if len(merged) != len(preds) or len(preds) != 200:
        sys.exit("per_example_predictions.parquet and annotations/gold_set.csv do not cover the same 200 ids")
    if not (merged["gold_guidance"] == merged["seeks_legal_guidance"].astype(bool)).all():
        sys.exit("gold guidance labels differ from annotations/gold_set.csv")
    positive = merged[merged["gold_guidance"]]
    if not (positive["gold_topic"] == positive["primary_topic"]).all():
        sys.exit("gold topic labels differ from annotations/gold_set.csv")


def compare_with_summary(computed):
    summary = pd.read_csv(EVALUATION / "summary_metrics.csv").set_index(["system", "evaluation"])
    mismatches = []
    for (system, evaluation), row in computed.items():
        for column, value in row.items():
            if column not in summary.columns or pd.isna(summary.at[(system, evaluation), column]):
                continue
            expected = summary.at[(system, evaluation), column]
            if abs(value - expected) > 1e-9:
                mismatches.append(f"{system} / {evaluation} / {column}: {value} != {expected}")
    return mismatches


def show(title, rows):
    print(f"\n{title}")
    print(pd.DataFrame(rows).to_string(index=False, float_format=lambda x: f"{x:.3f}"))


def main():
    preds = pd.read_parquet(EVALUATION / "per_example_predictions.parquet")
    check_gold_labels(preds)
    computed = {}

    guidance = []
    for systems, evaluation in ((FULL_SYSTEMS, "guidance"), (PREFIX_SYSTEMS, "final_prefix_guidance")):
        for system, key in systems.items():
            row = guidance_row(preds, key)
            computed[(system, evaluation)] = {k: v for k, v in row.items() if k not in ("fp", "fn")}
            guidance.append({"model": system, **row})
    show("Guidance detection (n=200; prefix models after the final user turn)", guidance)

    topic_cascade = []
    for system, key in FULL_SYSTEMS.items():
        oracle, cascade, errors = topic_cascade_rows(preds, key)
        computed[(system, "oracle_topic")] = oracle
        computed[(system, "end_to_end_cascade")] = cascade
        topic_cascade.append({
            "model": system,
            "topic_acc": oracle["accuracy"],
            "topic_macro_f1": oracle["macro_f1"],
            "topic_ci_low": oracle["macro_f1_ci_low"],
            "topic_ci_high": oracle["macro_f1_ci_high"],
            "cascade_acc": cascade["accuracy"],
            "cascade_macro_f1": cascade["macro_f1"],
            **{f"errors_{k}": v for k, v in errors.items()},
        })
    show("Topic classification on the 84 gold positives, and end-to-end cascade (n=200)", topic_cascade)

    show("Exact paired McNemar tests", significance_rows(preds))

    mismatches = compare_with_summary(computed)
    if mismatches:
        print("\nMismatches against summary_metrics.csv:\n  " + "\n  ".join(mismatches))
        sys.exit(1)
    print("\nAll values match supplementary/evaluation/summary_metrics.csv.")


if __name__ == "__main__":
    main()
