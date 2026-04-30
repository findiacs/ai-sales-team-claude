import unittest
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError, URLError
import sys
import os

# Add the scripts directory to the path so we can import contact_finder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from contact_finder import fetch_url

class TestFetchUrl(unittest.TestCase):
    @patch('contact_finder.urlopen')
    def test_fetch_url_success(self, mock_urlopen):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b"<html><body>Test</body></html>"
        mock_response.headers.get_content_charset.return_value = "utf-8"
        mock_urlopen.return_value = mock_response

        status, html = fetch_url("https://example.com")

        self.assertEqual(status, 200)
        self.assertEqual(html, "<html><body>Test</body></html>")
        mock_urlopen.assert_called_once()

    @patch('contact_finder.urlopen')
    def test_fetch_url_http_error(self, mock_urlopen):
        # Setup mock to raise HTTPError
        mock_urlopen.side_effect = HTTPError("https://example.com", 404, "Not Found", {}, None)

        status, html = fetch_url("https://example.com")

        self.assertEqual(status, 404)
        self.assertIsNone(html)

    @patch('contact_finder.urlopen')
    def test_fetch_url_url_error(self, mock_urlopen):
        # Setup mock to raise URLError
        mock_urlopen.side_effect = URLError("Network unreachable")

        status, html = fetch_url("https://example.com")

        self.assertIsNone(status)
        self.assertIsNone(html)

    @patch('contact_finder.urlopen')
    def test_fetch_url_os_error(self, mock_urlopen):
        # Setup mock to raise OSError
        mock_urlopen.side_effect = OSError("Connection reset")

        status, html = fetch_url("https://example.com")

        self.assertIsNone(status)
        self.assertIsNone(html)

    @patch('contact_finder.urlopen')
    def test_fetch_url_generic_exception(self, mock_urlopen):
        # Setup mock to raise a generic exception
        mock_urlopen.side_effect = Exception("Something went wrong")

        status, html = fetch_url("https://example.com")

        self.assertIsNone(status)
        self.assertIsNone(html)

    @patch('contact_finder.urlopen')
    def test_fetch_url_timeout(self, mock_urlopen):
        # Setup mock to raise TimeoutError (which is an OSError in many Python versions or its own)
        mock_urlopen.side_effect = TimeoutError("Request timed out")

        status, html = fetch_url("https://example.com")

        self.assertIsNone(status)
        self.assertIsNone(html)

if __name__ == '__main__':
    unittest.main()
