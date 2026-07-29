import unittest
from unittest.mock import patch
from banner_grabber import validate_ip, format_banner

class TestBannerGrabber(unittest.TestCase):
    def test_valid_ip(self):
        with patch("builtins.exit") as mock_exit:
            validate_ip("192.168.1.1")
            mock_exit.assert_not_called()

    def test_valid_domain(self):
        with patch("builtins.exit") as mock_exit:
            validate_ip("google.com")
            mock_exit.assert_not_called()

    def test_invalid_ip(self):
        with patch("builtins.exit") as mock_exit:
            validate_ip("999.999.999.999")
            mock_exit.assert_called_once()

    def test_invalid_string(self):
        with patch("builtins.exit") as mock_exit:
            validate_ip("notanip")
            mock_exit.assert_called_once()

    def test_format_banners(self):
        banners = {80: ['HTTP/1.1 301 Moved Permanently\r\nContent-Length: 0\r\nLocation: https://github.com/\r\nconnection: close\r\n\r\n', 'http'], 22: ['SSH-2.0-cd00c9e\r\n', 'ssh']}
        result = ['80 (http): HTTP/1.1 301 Moved Permanently', '22 (ssh): SSH-2.0-cd00c9e']
        output = format_banner(banners)
        self.assertListEqual(output, result)

if __name__ == "__main__":
    unittest.main()