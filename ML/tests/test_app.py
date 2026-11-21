import unittest

from streamlit.testing.v1 import AppTest

from src.data_loader import ROOT


class AppTests(unittest.TestCase):
    def app(self):
        return AppTest.from_file(str(ROOT / "app.py"), default_timeout=25).run()

    def test_every_page_and_charts(self):
        pages = [
            ("1_Home", "Find government schemes in India", 2),
            ("2_Scheme_Recommendation", "Scheme recommendations", 0),
            ("3_Eligibility_Checker", "Eligibility checker", 0),
            ("4_Scheme_Comparison", "Compare schemes", 0),
            ("5_Model_Performance", "Model performance", 1),
            ("6_Applicant_Analysis", "Applicant patterns", 2),
        ]
        app = self.app()
        for file, title, charts in pages:
            with self.subTest(page=file):
                app.switch_page(f"pages/{file}.py").run()
                self.assertFalse(app.exception)
                self.assertEqual(app.title[0].value, title)
                self.assertEqual(len(app.get("plotly_chart")), charts)
                if file == "5_Model_Performance":
                    self.assertEqual(len(app.get("image")), 1)

    def test_blank_then_partial_recommendation(self):
        app = self.app().switch_page("pages/2_Scheme_Recommendation.py").run()
        app.button[0].click().run()
        self.assertIn("Answer at least one", app.warning[0].value)
        app.number_input[0].set_value(17)
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.expander), 3)

    def test_blank_eligibility_check(self):
        app = self.app().switch_page("pages/3_Eligibility_Checker.py").run()
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any("More Information Required" in item.proto.body for item in app.get("html")))

    def test_reviewed_scheme_link_preselects_checker(self):
        app = self.app()
        self.assertEqual(len(app.get("image")), 4)
        app.switch_page("pages/3_Eligibility_Checker.py")
        app.query_params["scheme"] = "pmkisan"
        app.run()
        self.assertFalse(app.exception)
        self.assertIn("Kisan", app.selectbox[0].value)

    def test_catalog_pagination_resets_on_search(self):
        app = self.app()
        app.number_input(key="catalog_page").set_value(2).run()
        self.assertTrue(any("Showing 26" in item.value for item in app.caption))
        app.text_input[0].set_value("Kisan").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.number_input(key="catalog_page").value, 1)
        self.assertTrue(any("Showing 1" in item.value for item in app.caption))
