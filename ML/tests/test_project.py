import json
import unittest

from src.data_loader import DATA, MODELS, load_catalog, load_schemes
from src.eligibility_checker import INELIGIBLE, POTENTIAL, UNKNOWN, evaluate, validate_profile
from src.prediction import load_model, relevance_scores
from src.recommendation import recommend


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.schemes = load_schemes()
        self.by_id = {scheme["id"]: scheme for scheme in self.schemes}

    def test_catalog_and_source_links(self):
        self.assertEqual(len(load_catalog()), 4702)
        profiles = json.loads((DATA / "raw_audit.json").read_text(encoding="utf-8"))
        self.assertEqual({entry["rows"] for entry in profiles}, {772, 4702})
        budget = next(entry for entry in profiles if entry["rows"] == 772)
        self.assertEqual(budget["missing"]["Actuals2019-2020 - Capital"], 559)
        for scheme in self.schemes:
            self.assertTrue(scheme["source"].startswith("https://"))
            self.assertTrue(scheme["apply"].startswith("https://"))

    def test_validation(self):
        for field, value in [("age", -1), ("age", 121), ("income", -5), ("income", 10.5)]:
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                validate_profile({field: value})
        self.assertEqual(validate_profile({"income": 0, "age": None})["income"], 0)

    def test_ujjwala_boundaries_and_missing(self):
        scheme = self.by_id["pmuy"]
        profile = {"age": 18, "woman": "Yes", "lpg": "No", "deprivation": "Yes"}
        self.assertEqual(evaluate(scheme, profile)[0], POTENTIAL)
        self.assertEqual(evaluate(scheme, dict(profile, age=17))[0], INELIGIBLE)
        self.assertEqual(evaluate(scheme, dict(profile, deprivation=None))[0], UNKNOWN)
        self.assertEqual(evaluate(scheme, {"age": 17})[0], INELIGIBLE)

    def test_document_verification_and_income(self):
        self.assertEqual(evaluate(self.by_id["pmkisan"], {"land": "Yes", "kisan_excluded": "No"})[0], UNKNOWN)
        self.assertEqual(evaluate(self.by_id["pmkisan"], {"land": "Yes", "kisan_excluded": "No", "land_verified": "No"})[0], UNKNOWN)
        profile = {"student": "Yes", "domicile": "Yes", "income": 800000, "dte_verified": "Yes"}
        self.assertEqual(evaluate(self.by_id["maha_dte"], profile)[0], POTENTIAL)
        self.assertEqual(evaluate(self.by_id["maha_dte"], dict(profile, income=800001))[0], INELIGIBLE)

    def test_inference_and_actual_metrics(self):
        model = load_model()
        profile = {"age": 17, "land": "Yes", "kisan_excluded": "No", "land_verified": "Yes"}
        scores = relevance_scores(model, profile, self.schemes)
        self.assertEqual(len(scores), len(self.schemes))
        self.assertTrue(all(0 <= value <= 1 for value in scores))
        self.assertEqual(recommend(model, profile, self.schemes)[0][0]["id"], "pmkisan")
        report = json.loads((MODELS / "metrics.json").read_text(encoding="utf-8"))
        self.assertIn(report["winner"], report["results"])
        for result in report["results"].values():
            self.assertEqual(sum(map(sum, result["matrix"])), report["test_profiles"] * len(self.schemes))