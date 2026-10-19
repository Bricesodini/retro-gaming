import unittest

from retro_gaming.session import Session


class WelcomeJourneyTest(unittest.TestCase):
    def test_waiting_at_laboratory_keeps_session_clock_inactive(self):
        session = Session()

        first = session.advance(0)
        after_introduction = session.advance(3600)

        self.assertEqual(first.phase, "laboratoire")
        self.assertIsNone(first.remaining_seconds)
        self.assertEqual(first.events, ())
        self.assertEqual(after_introduction, first)


if __name__ == "__main__":
    unittest.main()
