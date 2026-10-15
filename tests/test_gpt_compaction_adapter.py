import unittest
from tools.gpt_compaction_adapter import compact, build_payload, ENDPOINT


class CompactionContractTests(unittest.TestCase):
    def setUp(self):
        self.items = [{"role": "user", "content": "retain this instruction"}]

    def test_input_unmodified(self):
        before = [dict(x) for x in self.items]
        output = compact("supported-model", self.items, api_key="dummy",
            transport=lambda url, payload, key: {"output": [{"type": "compaction", "encrypted_content": "opaque"}]})
        self.assertEqual(self.items, before)
        self.assertEqual(output[0]["type"], "compaction")

    def test_exact_endpoint_and_model(self):
        called = []
        def mock(url, payload, key):
            called.append((url, payload["model"]))
            return {"output": [{"type": "compaction", "encrypted_content": "opaque"}]}
        compact("model-example", self.items, api_key="dummy", transport=mock)
        self.assertEqual(called, [(ENDPOINT, "model-example")])

    def test_invalid_response_fails_closed(self):
        for reply in ({}, {"output": []}, {"output": [{"type": "message"}]}):
            with self.subTest(reply=reply), self.assertRaises(ValueError):
                compact("x", self.items, api_key="dummy", transport=lambda *args: reply)

    def test_invalid_input(self):
        for model, items in (("", self.items), ("x", []), ("x", {})):
            with self.assertRaises(ValueError):
                build_payload(model, items)

    def test_no_key_blocks_transport(self):
        called = []
        with self.assertRaises(RuntimeError):
            compact("x", self.items, api_key="", transport=lambda *args: called.append(True))
        self.assertEqual(called, [])


if __name__ == "__main__":
    unittest.main()
