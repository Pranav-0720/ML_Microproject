"""Evaluate reviewed conditions against self-reported responses."""
from operator import eq, ge, le

POTENTIAL = "Potentially Eligible"
INELIGIBLE = "Not Eligible Based on Provided Information"
UNKNOWN = "More Information Required"
OPERATORS = {"eq": eq, "min": ge, "max": le}


def evaluate(scheme, profile):
    results = []
    for field, operation, threshold, description in scheme["rules"]:
        value = profile.get(field)
        if value is None or (operation == "verify" and value != threshold):
            outcome = "Unknown"
        elif operation == "verify" or OPERATORS[operation](value, threshold):
            outcome = "Met"
        else:
            outcome = "Unmet"
        results.append((description, outcome))
    outcomes = {item[1] for item in results}
    if "Unmet" in outcomes:
        return INELIGIBLE, results
    if "Unknown" in outcomes:
        return UNKNOWN, results
    return POTENTIAL, results


def validate_profile(profile):
    for field, upper in [("age", 120), ("income", 1_000_000_000)]:
        value = profile.get(field)
        if value is not None and (type(value) is not int or not 0 <= value <= upper):
            raise ValueError(f"{field.title()} must be a whole number between 0 and {upper:,}.")
    return profile