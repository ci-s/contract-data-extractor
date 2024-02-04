from langchain.evaluation import ExactMatchStringEvaluator
import pandas as pd
from typing import Any


# Batch evaluation
def evaluate_includes(ground_truth: pd.Series, prediction: pd.Series) -> bool:
    """
    Evaluate if each element in the ground_truth series is included in the corresponding element of the prediction series.

    Args:
        ground_truth (pd.Series): The series containing the ground truth values.
        prediction (pd.Series): The series containing the predicted values.

    Returns:
        bool: True if each element in the ground_truth series is included in the corresponding element of the prediction series, False otherwise.
    """
    tmp = pd.DataFrame({"ground_truth": ground_truth, "prediction": prediction})
    return tmp.apply(lambda row: row["ground_truth"] in str(row["prediction"]), axis=1)


def evaluate_equals(ground_truth: pd.Series, prediction: pd.Series) -> bool:
    """
    Evaluate if the ground truth values are equal to the predicted values.

    Args:
        ground_truth (pd.Series): The ground truth values.
        prediction (pd.Series): The predicted values.

    Returns:
        bool: True if the ground truth values are equal to the predicted values, False otherwise.
    """
    tmp = pd.DataFrame({"ground_truth": ground_truth, "prediction": prediction})
    return tmp.apply(lambda row: row["ground_truth"] == row["prediction"], axis=1)


def evaluate_w_evaluator(
    ground_truth: pd.Series, prediction: pd.Series, evaluator=None
):
    if evaluator is None:
        evaluator = ExactMatchStringEvaluator(
            ignore_case=True,
            ignore_numbers=False,
            ignore_punctuation=True,
        )
    tmp = pd.DataFrame({"ground_truth": ground_truth, "prediction": prediction})
    return tmp.apply(
        lambda row: evaluator.evaluate_strings(
            prediction=str(row["preds"]),
            reference=row["start_date"],
        )["score"],
        axis=1,
    )


# Single evaluation
def clean_string(s: str):
    s = s.lower().replace(",", "").replace(".", "").replace("-", " ")
    return s


def evaluate_string_similarity(
    ground_truth: str,
    prediction: str,
    distance_evaluator,
    distance_threshold: float = 0.5,
) -> bool:
    ground_truth = clean_string(ground_truth)
    prediction = clean_string(prediction)
    if (
        (ground_truth in prediction)
        or (
            distance_evaluator.evaluate_strings(
                prediction=prediction, reference=ground_truth
            )["score"]
            < distance_threshold
        )
        or all(word in prediction.split() for word in ground_truth.split())
    ):
        return True
    else:
        return False


def evaluate_string_similarity_old(
    ground_truth: str,
    prediction: str,
    distance_evaluator: Any,
    distance_threshold: float = 0.5,
) -> bool:
    if (
        ground_truth.lower() in prediction.lower()
    ) or distance_evaluator.evaluate_strings(
        prediction=prediction.lower(), reference=ground_truth.lower()
    )[
        "score"
    ] < distance_threshold:
        return True
    else:
        return False


def evaluate_number_similarity(
    ground_truth: float,
    prediction: float,
    distance_threshold: float = 0.5,
) -> bool:
    if abs(ground_truth - prediction) <= distance_threshold:
        return True
    else:
        return False
