import unittest
from unittest.mock import patch, MagicMock
import ssl
import scripts.contact_finder as contact_finder
import scripts.analyze_prospect as analyze_prospect

class TestSSLVerification(unittest.TestCase):

    @patch("scripts.contact_finder.urlopen")
    def test_contact_finder_ssl_context(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.headers.get_content_charset.return_value = "utf-8"
        mock_resp.read.return_value = b"<html></html>"
        mock_resp.status = 200
        mock_urlopen.return_value = mock_resp

        contact_finder.fetch_url("https://example.com")

        self.assertTrue(mock_urlopen.called)
        args, kwargs = mock_urlopen.call_args
        ctx = kwargs.get("context")
        self.assertIsNotNone(ctx, "SSL context should be provided")
        self.assertTrue(ctx.check_hostname, "check_hostname should be True")
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED, "verify_mode should be ssl.CERT_REQUIRED")

    @patch("scripts.analyze_prospect.urlopen")
    def test_analyze_prospect_ssl_context(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.headers.get_content_charset.return_value = "utf-8"
        mock_resp.read.return_value = b"<html></html>"
        mock_resp.status = 200
        mock_urlopen.return_value = mock_resp

        analyze_prospect.fetch_url("https://example.com")

        self.assertTrue(mock_urlopen.called)
        args, kwargs = mock_urlopen.call_args
        ctx = kwargs.get("context")
        self.assertIsNotNone(ctx, "SSL context should be provided")
        self.assertTrue(ctx.check_hostname, "check_hostname should be True")
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED, "verify_mode should be ssl.CERT_REQUIRED")

if __name__ == "__main__":
    unittest.main()
