from src.eligibility_checker import INELIGIBLE, POTENTIAL, UNKNOWN, evaluate, validate_profile
from src.prediction import relevance_scores


def recommend(model, profile, schemes):
    validate_profile(profile)
    ranks = {POTENTIAL: 0, UNKNOWN: 1, INELIGIBLE: 2}
    results = []
    for scheme, score in zip(schemes, relevance_scores(model, profile, schemes), strict=True):
        status, checks = evaluate(scheme, profile)
        results.append((scheme, score, status, checks))
    return sorted(results, key=lambda item: (ranks[item[2]], -item[1]))