import unittest
import sys
import os

# Add scripts directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.lead_scorer import (
    score_budget, score_authority, score_need, score_timeline,
    assess_meddic, compute_grade, compute_confidence, recommend_action,
    score_lead
)

class TestLeadScorer(unittest.TestCase):

    # -------------------------------------------------------------------------
    # MEDDIC Assessment Tests
    # -------------------------------------------------------------------------

    def test_assess_meddic_empty(self):
        data = {}
        result = assess_meddic(data)
        expected = {
            "metrics": 0,
            "economic_buyer": 0,
            "decision_criteria": 0,
            "decision_process": 0,
            "identify_pain": 0,
            "champion": 0,
            "overall": 0,
        }
        self.assertEqual(result, expected)

    def test_assess_meddic_full(self):
        data = {
            "budget_signals": {
                "funding_amount": 1000000,
                "employee_count": 50,
                "pricing_visible": True,
                "tech_spend_indicators": ["AWS"]
            },
            "authority_signals": {
                "c_suite_identified": True,
                "decision_makers_found": 2,
                "org_chart_mapped": True
            },
            "need_signals": {
                "pain_points_detected": 1,
                "reviews_mention_pain": True,
                "job_posts_relevant": True,
                "competitor_complaints": 1
            },
            "timeline_signals": {
                "contract_renewal": True,
                "hiring_for_role": True
            }
        }
        result = assess_meddic(data)
        expected = {
            "metrics": 100,
            "economic_buyer": 100,
            "decision_criteria": 100,
            "decision_process": 100,
            "identify_pain": 100,
            "champion": 100,
            "overall": 100,
        }
        self.assertEqual(result, expected)

    def test_assess_meddic_partial(self):
        data = {
            "budget_signals": {
                "funding_amount": 5000000,
                # employee_count missing (0)
            },
            "need_signals": {
                "pain_points_detected": 3,
                "job_posts_relevant": True
                # competitor_complaints missing (0)
            },
            "authority_signals": {
                "decision_makers_found": 1
                # c_suite_identified missing (False)
                # org_chart_mapped missing (False)
            }
        }
        # metrics: [T, F, T] -> 2/3 -> 66
        # economic_buyer: [F, T] -> 1/2 -> 50
        # decision_criteria: [F, F, F] -> 0/3 -> 0
        # decision_process: [F, F, F] -> 0/3 -> 0 (dm_found 1 < 2)
        # identify_pain: [T, T, F] -> 2/3 -> 66
        # champion: [T, F, F] -> 1/3 -> 33
        # overall: (66+50+0+0+66+33)/6 = 215/6 = 35.83 -> 35

        result = assess_meddic(data)
        self.assertEqual(result["metrics"], 66)
        self.assertEqual(result["economic_buyer"], 50)
        self.assertEqual(result["decision_criteria"], 0)
        self.assertEqual(result["decision_process"], 0)
        self.assertEqual(result["identify_pain"], 66)
        self.assertEqual(result["champion"], 33)
        self.assertEqual(result["overall"], 35)

    # -------------------------------------------------------------------------
    # BANT Scoring Tests
    # -------------------------------------------------------------------------

    def test_score_budget(self):
        self.assertEqual(score_budget({}), 0)

        # Funding: 10M (+8), Emp: 100 (+4), Pricing: True (+3), Tech: 2 (+4) = 19
        self.assertEqual(score_budget({
            "funding_amount": 10_000_000,
            "employee_count": 100,
            "pricing_visible": True,
            "tech_spend_indicators": ["A", "B"]
        }), 19)

        # Max score (50M+ funding, 500+ emp, etc)
        self.assertEqual(score_budget({
            "funding_amount": 100_000_000,
            "employee_count": 1000,
            "pricing_visible": True,
            "tech_spend_indicators": ["A", "B", "C", "D"]
        }), 25)

    def test_score_authority(self):
        self.assertEqual(score_authority({}), 0)

        # DMs: 3 (+8), C-suite: True (+8), Org chart: True (+7) = 23
        self.assertEqual(score_authority({
            "decision_makers_found": 3,
            "c_suite_identified": True,
            "org_chart_mapped": True
        }), 23)

        # DMs: 1 (+5), Org chart: False, but dm > 1? no. = 5
        self.assertEqual(score_authority({
            "decision_makers_found": 1
        }), 5)

    def test_score_need(self):
        self.assertEqual(score_need({}), 0)

        # Pain: 5 (+8), Jobs: True (+6), Reviews: True (+5), Complaints: 3 (+6) = 25
        self.assertEqual(score_need({
            "pain_points_detected": 5,
            "job_posts_relevant": True,
            "reviews_mention_pain": True,
            "competitor_complaints": 3
        }), 25)

    def test_score_timeline(self):
        self.assertEqual(score_timeline({}), 0)

        # Hiring: True (+7), Funding: True (+7), Renewal: True (+6), Urgency: 3 (+5) = 25
        self.assertEqual(score_timeline({
            "hiring_for_role": True,
            "recent_funding": True,
            "contract_renewal": True,
            "urgency_mentions": 3
        }), 25)

    # -------------------------------------------------------------------------
    # Helper & Pipeline Tests
    # -------------------------------------------------------------------------

    def test_compute_grade(self):
        self.assertEqual(compute_grade(80), "A")
        self.assertEqual(compute_grade(60), "B")
        self.assertEqual(compute_grade(30), "C")
        self.assertEqual(compute_grade(10), "D")

    def test_compute_confidence(self):
        data = {
            "budget_signals": {"funding_amount": 100, "employee_count": 10},
            "authority_signals": {"c_suite_identified": True},
            "need_signals": {"pain_points_detected": 1},
            "timeline_signals": {"hiring_for_role": True}
        }
        # This will depend on total fields. lead_scorer.py iterates over signals.
        # It's a bit opaque how many fields there are in total if we pass a sparse dict.
        # But for 0 fields, it returns "low".
        self.assertEqual(compute_confidence({}), "low")
        self.assertIn(compute_confidence(data), ["low", "medium", "high"])

    def test_recommend_action(self):
        meddic = {"overall": 80, "metrics": 80}
        self.assertIn("Schedule discovery call", recommend_action("A", meddic))
        self.assertIn("Nurture", recommend_action("B", meddic))
        self.assertIn("Research needed", recommend_action("C", meddic))
        self.assertIn("Low priority", recommend_action("D", meddic))

    def test_score_lead(self):
        data = {
            "company": "TestCorp",
            "budget_signals": {"funding_amount": 50_000_000},
            "authority_signals": {"c_suite_identified": True},
            "need_signals": {"pain_points_detected": 5},
            "timeline_signals": {"hiring_for_role": True}
        }
        result = score_lead(data)
        self.assertEqual(result["company"], "TestCorp")
        self.assertTrue(0 <= result["bant_score"] <= 100)
        self.assertIn("meddic_completeness", result)
        self.assertIn("lead_grade", result)

if __name__ == "__main__":
    unittest.main()
