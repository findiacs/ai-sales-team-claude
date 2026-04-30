import unittest
from unittest.mock import patch
import sys
import os

# Add scripts directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.analyze_prospect import analyze

class TestAnalyzeProspect(unittest.TestCase):

    @patch('scripts.analyze_prospect.fetch_url')
    def test_analyze_aggregates_html(self, mock_fetch):
        # Setup mock responses
        def side_effect(url, timeout=None):
            if url == "https://example.com":
                return 200, "<html><body><h1>Home</h1><a href='https://twitter.com/home'>Twitter</a></body></html>"
            elif "/about" in url:
                return 200, "<html><body><a href='https://linkedin.com/company/about'>LinkedIn</a></body></html>"
            elif "/contact" in url:
                return 200, "<html><body><a href='https://facebook.com/contact'>Facebook</a></body></html>"
            else:
                return 404, None

        mock_fetch.side_effect = side_effect

        result = analyze("https://example.com")

        # Verify pages analyzed
        self.assertIn("https://example.com", result["pages_analyzed"])
        self.assertIn("https://example.com/about", result["pages_analyzed"])
        self.assertIn("https://example.com/contact", result["pages_analyzed"])

        # Verify social links are aggregated from multiple pages
        self.assertIn("twitter", result["social_links"])
        self.assertEqual(result["social_links"]["twitter"], ["https://twitter.com/home"])

        self.assertIn("linkedin", result["social_links"])
        self.assertEqual(result["social_links"]["linkedin"], ["https://linkedin.com/company/about"])

        self.assertIn("facebook", result["social_links"])
        self.assertEqual(result["social_links"]["facebook"], ["https://facebook.com/contact"])

if __name__ == '__main__':
    unittest.main()
