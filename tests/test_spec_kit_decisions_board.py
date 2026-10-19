import unittest
from examples.spec_kit_decisions_board.decisions import Decision, DecisionsBoard

class TestDecisionsBoard(unittest.TestCase):
    def test_capture_retains_all_fields(self):
        """TEST-01 / REQ-01 / SC-01."""
        board = DecisionsBoard()
        board.add_decision(Decision("D-01", "First", "Reason 1", "2026-10-15"))

        captured = board.list_decisions()[0]

        self.assertEqual(
            (captured.id, captured.title, captured.rationale, captured.date),
            ("D-01", "First", "Reason 1", "2026-10-15"),
        )

    def test_list_orders_by_date_then_id(self):
        """TEST-02 / REQ-02 / SC-02."""
        board = DecisionsBoard()
        board.add_decision(Decision("D-02", "Second", "Reason 2", "2026-10-15"))
        board.add_decision(Decision("D-01", "First", "Reason 1", "2026-10-15"))
        board.add_decision(Decision("D-03", "Old", "Reason 3", "2026-10-14"))
        self.assertEqual([d.id for d in board.list_decisions()], ["D-03", "D-01", "D-02"])

    def test_export_markdown_sanitizes_fields(self):
        """TEST-03 / REQ-03 / SC-03."""
        board = DecisionsBoard()
        board.add_decision(Decision("A", "X|Y", "line1\nline2", "2026-10-15"))

        exported = board.export_markdown()

        self.assertIn("X\\|Y", exported)
        self.assertIn("line1 line2", exported)

    def test_duplicate_id(self):
        board = DecisionsBoard()
        board.add_decision(Decision("A", "Title", "Reason", "2026-10-15"))
        with self.assertRaises(ValueError):
            board.add_decision(Decision("A", "Title", "Reason", "2026-10-15"))

    def test_invalid_fields(self):
        for values in (("A", "", "R", "2026-10-15"), ("A", "T", "", "2026-10-15"), ("A", "T", "R", "2026-99-15")):
            with self.subTest(values=values), self.assertRaises(ValueError):
                Decision(*values)

if __name__ == "__main__":
    unittest.main()
