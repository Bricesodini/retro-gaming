import unittest

from retro_gaming.session import Session


class WelcomeJourneyTest(unittest.TestCase):
    def test_waiting_at_laboratory_keeps_session_clock_inactive(self):
        session = Session()

        first = session.advance(0, animator_action=None)
        after_introduction = session.advance(3600, animator_action=None)

        self.assertEqual(first.phase, "laboratoire")
        self.assertIsNone(first.remaining_seconds)
        self.assertEqual(first.events, ())
        self.assertEqual(after_introduction, first)

    def test_unassigned_animator_action_keeps_laboratory_waiting(self):
        session = Session()

        state = session.advance(5, animator_action="unassigned_key")

        self.assertEqual(state.phase, "laboratoire")
        self.assertIsNone(state.remaining_seconds)
        self.assertEqual(state.events, ())


if __name__ == "__main__":
    unittest.main()
