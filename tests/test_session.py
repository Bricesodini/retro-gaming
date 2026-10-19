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


class MysteryJourneyTest(unittest.TestCase):
    def test_trigger_starts_once_and_elf_message_persists(self):
        session = Session(session_seconds=180, possession_seconds=12)

        started = session.advance(0, animator_action="declencher_mystere")
        repeated = session.advance(4, animator_action="declencher_mystere")
        contact = session.advance(5, animator_action=None)
        intervention = session.advance(3, animator_action=None)
        long_after = session.advance(20, animator_action="declencher_mystere")

        self.assertEqual(started.phase, "possession")
        self.assertEqual(started.remaining_seconds, 180)
        self.assertEqual(repeated.remaining_seconds, 176)
        self.assertEqual(contact.phase, "possession")
        self.assertIn("ELF", " ".join(contact.messages))
        self.assertEqual(intervention.phase, "elf")
        self.assertEqual(intervention.remaining_seconds, 168)
        self.assertEqual(long_after.phase, "elf")
        self.assertEqual(long_after.remaining_seconds, 148)
        self.assertEqual(long_after.messages, intervention.messages)
        self.assertEqual(long_after.events, ())


if __name__ == "__main__":
    unittest.main()
