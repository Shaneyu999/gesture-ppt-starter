"""Classification metrics implemented without scikit-learn."""

from __future__ import annotations

from collections import defaultdict
from typing import Sequence


def confusion_matrix(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    num_classes: int,
) -> list[list[int]]:
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length.")
    matrix = [[0 for _ in range(num_classes)] for _ in range(num_classes)]
    for truth, prediction in zip(y_true, y_pred):
        if not 0 <= truth < num_classes or not 0 <= prediction < num_classes:
            raise ValueError("Class ids are outside the configured range.")
        matrix[truth][prediction] += 1
    return matrix


def accuracy(y_true: Sequence[int], y_pred: Sequence[int]) -> float:
    if not y_true:
        raise ValueError("Cannot compute accuracy for an empty sequence.")
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length.")
    return sum(int(a == b) for a, b in zip(y_true, y_pred)) / len(y_true)


def macro_f1(y_true: Sequence[int], y_pred: Sequence[int]) -> float:
    if not y_true:
        raise ValueError("Cannot compute F1 for an empty sequence.")
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length.")

    tp: dict[int, int] = defaultdict(int)
    fp: dict[int, int] = defaultdict(int)
    fn: dict[int, int] = defaultdict(int)
    for truth, prediction in zip(y_true, y_pred):
        if truth == prediction:
            tp[truth] += 1
        else:
            fp[prediction] += 1
            fn[truth] += 1

    labels = sorted(set(y_true) | set(y_pred))
    scores = []
    for label in labels:
        denominator = 2 * tp[label] + fp[label] + fn[label]
        scores.append(0.0 if denominator == 0 else 2 * tp[label] / denominator)
    return sum(scores) / len(scores)


def summarize(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    labels: Sequence[str],
) -> dict[str, object]:
    matrix = confusion_matrix(y_true, y_pred, len(labels))
    recalls: dict[str, float] = {}
    for class_id, label in enumerate(labels):
        total = sum(matrix[class_id])
        recalls[label] = 0.0 if total == 0 else matrix[class_id][class_id] / total
    return {
        "accuracy": accuracy(y_true, y_pred),
        "macro_f1": macro_f1(y_true, y_pred),
        "per_class_recall": recalls,
        "confusion_matrix": matrix,
    }
