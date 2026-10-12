import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server import (
    MAX_CONTENT_CHARS,
    RequestValidationError,
    validate_bind_host,
    validate_messages,
)


class ValidateBindHostTests(unittest.TestCase):
    def test_accepts_only_ipv4_loopback(self):
        self.assertEqual(validate_bind_host("127.0.0.1"), "127.0.0.1")

    def test_rejects_non_loopback_hosts_without_echoing_input(self):
        for host in ("0.0.0.0", "localhost", "::1", "192.168.1.5", "secret-host"):
            with self.subTest(host=host):
                with self.assertRaises(RequestValidationError) as caught:
                    validate_bind_host(host)
                self.assertNotIn(host, str(caught.exception))
                self.assertNotIn(host, caught.exception.code)


class ValidateMessagesTests(unittest.TestCase):
    def test_preserves_a_unicode_conversation(self):
        messages = [
            {"role": "user", "content": "Olá, mundo 🌍"},
            {"role": "assistant", "content": "こんにちは"},
        ]
        self.assertEqual(validate_messages(messages), messages)

    def test_rejects_empty_history(self):
        with self.assertRaises(RequestValidationError):
            validate_messages([])

    def test_rejects_non_list_history(self):
        for value in (None, {}, "conversation", ()):
            with self.subTest(value=type(value).__name__):
                with self.assertRaises(RequestValidationError):
                    validate_messages(value)

    def test_rejects_more_than_one_hundred_messages(self):
        history = [{"role": "user", "content": "hi"}] * 101
        with self.assertRaises(RequestValidationError):
            validate_messages(history)

    def test_accepts_exactly_one_hundred_messages(self):
        history = [{"role": "user", "content": "hi"}] * 100
        self.assertEqual(validate_messages(history), history)

    def test_accepts_content_at_limit_without_normalizing(self):
        content = " " + "á" * (MAX_CONTENT_CHARS - 2) + " "
        self.assertEqual(
            validate_messages([{"role": "user", "content": content}]),
            [{"role": "user", "content": content}],
        )

    def test_rejects_malformed_messages(self):
        for message in (None, [], "message", {}, {"role": "user"}, {"content": "hi"}):
            with self.subTest(message=message):
                with self.assertRaises(RequestValidationError):
                    validate_messages([message])

    def test_rejects_unknown_roles(self):
        for role in ("system", "tool", "", None, 42, [], {}):
            with self.subTest(role=role):
                with self.assertRaises(RequestValidationError) as caught:
                    validate_messages([{"role": role, "content": "hidden"}])
                self.assertNotIn("hidden", caught.exception.message)
                self.assertNotIn("hidden", caught.exception.code)

    def test_rejects_unknown_message_fields_without_echoing_submitted_text(self):
        secret = "private-token-value"
        with self.assertRaises(RequestValidationError) as caught:
            validate_messages([{"role": "user", "content": "hello", "token": secret}])
        self.assertNotIn(secret, str(caught.exception))
        self.assertNotIn(secret, caught.exception.code)

    def test_rejects_blank_content(self):
        for content in ("", " \t\n"):
            with self.subTest(content=repr(content)):
                with self.assertRaises(RequestValidationError):
                    validate_messages([{"role": "user", "content": content}])

    def test_rejects_non_string_content(self):
        with self.assertRaises(RequestValidationError):
            validate_messages([{"role": "user", "content": 42}])

    def test_rejects_content_above_limit_without_truncating_or_echoing(self):
        too_long = "x" * (MAX_CONTENT_CHARS + 1)
        with self.assertRaises(RequestValidationError) as caught:
            validate_messages([{"role": "user", "content": too_long}])
        self.assertNotIn(too_long, str(caught.exception))
        self.assertNotIn(too_long, caught.exception.code)


if __name__ == "__main__":
    unittest.main()
