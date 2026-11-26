import unittest
from app.tooling import validate_tool_target

class ToolValidationTests(unittest.TestCase):
    def test_username_tools_accept_simple_username(self):
        self.assertEqual(validate_tool_target("sherlock", "@sample_user"), "sample_user")
        self.assertEqual(validate_tool_target("maigret", "sample.user"), "sample.user")

    def test_username_rejects_spaces(self):
        with self.assertRaises(ValueError):
            validate_tool_target("sherlock", "two words")

    def test_domain_tools_accept_hostname(self):
        self.assertEqual(validate_tool_target("subfinder", "Example.org"), "example.org")

    def test_domain_tools_reject_url(self):
        with self.assertRaises(ValueError):
            validate_tool_target("whatweb", "https://example.org/path")

    def test_domain_tools_reject_ip_literal(self):
        with self.assertRaises(ValueError):
            validate_tool_target("theharvester", "192.0.2.10")

    def test_unknown_tool(self):
        with self.assertRaises(ValueError):
            validate_tool_target("unknown", "example.org")

if __name__ == "__main__":
    unittest.main()
