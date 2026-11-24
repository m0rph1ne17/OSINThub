import unittest
from app.investigations import investigate

class Tests(unittest.TestCase):
    def test_username(self):
        self.assertGreaterEqual(len(investigate("username", "sample_user")["findings"]), 3)
    def test_bad_email(self):
        with self.assertRaises(ValueError):
            investigate("email", "not-an-email")
    def test_domain_url_rejected(self):
        with self.assertRaises(ValueError):
            investigate("domain", "https://example.com/path")
    def test_empty(self):
        with self.assertRaises(ValueError):
            investigate("username", " ")

if __name__ == "__main__":
    unittest.main()
