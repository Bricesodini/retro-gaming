import unittest

from retro_gaming.session import Phase, Session, SessionState


class WelcomeJourneyTest(unittest.TestCase):
    def test_waiting_at_laboratory_keeps_session_clock_inactive(self):
        session = Session()

        first = session.advance(0, animator_action=None)
        after_introduction = session.advance(3600, animator_action=None)

        self.assertEqual(first.phase, Phase.LABORATOIRE)
        self.assertIsNone(first.remaining_seconds)
        self.assertEqual(first.events, ())
        self.assertEqual(after_introduction, first)

    def test_unassigned_animator_action_keeps_laboratory_waiting(self):
        session = Session()

        state = session.advance(5, animator_action="unassigned_key")

        self.assertEqual(state.phase, Phase.LABORATOIRE)
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

        self.assertEqual(started.phase, Phase.POSSESSION)
        self.assertEqual(started.remaining_seconds, 180)
        self.assertEqual(repeated.remaining_seconds, 176)
        self.assertEqual(contact.phase, Phase.POSSESSION)
        self.assertIn("ELF", " ".join(contact.messages))
        self.assertEqual(intervention.phase, Phase.ELF)
        self.assertEqual(intervention.remaining_seconds, 168)
        self.assertEqual(long_after.phase, Phase.ELF)
        self.assertEqual(long_after.remaining_seconds, 148)
        self.assertEqual(long_after.messages, intervention.messages)
        self.assertEqual(long_after.events, ())


class SessionEndJourneyTest(unittest.TestCase):
    def test_warning_then_alarm_once_without_negative_time(self):
        session = Session(session_seconds=30, possession_seconds=5, warning_seconds=10)
        session.advance(0, "declencher_mystere")
        self.assertEqual(session.advance(19, None).events, ())
        warning = session.advance(1, None)
        self.assertEqual((warning.remaining_seconds, warning.events), (10, ("avertissement",)))
        self.assertEqual(session.advance(9, None).events, ())
        end = session.advance(1, None)
        self.assertEqual((end.phase, end.remaining_seconds, end.events), (Phase.FIN, 0, ("alarme",)))
        self.assertEqual(session.advance(100, None).events, ())
        self.assertEqual(session.advance(0, "declencher_mystere").phase, Phase.FIN)

    def test_jump_crosses_warning_and_alarm_in_order_during_possession(self):
        session = Session(session_seconds=10, possession_seconds=6, warning_seconds=4)
        session.advance(0, "declencher_mystere")
        end = session.advance(11, None)
        self.assertEqual((end.phase, end.remaining_seconds), (Phase.FIN, 0))
        self.assertEqual(end.events, ("avertissement", "alarme"))
        self.assertEqual(end.messages, ())

    def test_expiration_during_elf_intervention(self):
        session = Session(session_seconds=10, possession_seconds=2, warning_seconds=3)
        session.advance(0, "declencher_mystere")
        self.assertEqual(session.advance(2, None).phase, Phase.ELF)
        self.assertEqual(session.advance(8, None).phase, Phase.FIN)

    def test_reset_from_each_phase_and_second_cycle(self):
        for elapsed in (0, 2, 10):
            with self.subTest(elapsed=elapsed):
                session = Session(session_seconds=10, possession_seconds=2, warning_seconds=3)
                session.advance(0, "declencher_mystere")
                session.advance(elapsed, None)
                reset = session.advance(5, "reinitialiser")
                self.assertEqual(reset, SessionState(Phase.LABORATOIRE, None, ()))
                restarted = session.advance(0, "declencher_mystere")
                self.assertEqual(restarted.remaining_seconds, 10)
                self.assertEqual(restarted.events, ())
                self.assertEqual(restarted.messages, ())
                self.assertEqual(session.advance(10, None).events, ("avertissement", "alarme"))

    def test_warning_must_be_inside_session(self):
        for warning in (0, -1, 30, 31):
            with self.subTest(warning=warning):
                with self.assertRaisesRegex(ValueError, "avertissement"):
                    Session(session_seconds=30, possession_seconds=5, warning_seconds=warning)


if __name__ == "__main__":
    unittest.main()

class ArcadeJourneyTest(unittest.TestCase):
    def test_entity_speaks_before_elf_asks_for_help_and_choice(self):
        session = Session(session_seconds=60, possession_seconds=10, warning_seconds=15)
        initial = session.advance(0, "declencher_mystere")
        entity = session.advance(4, None)
        elf = session.advance(6, None)
        choice = session.advance(0, "continuer")
        self.assertEqual(initial.phase, Phase.POSSESSION)
        self.assertIn("ENTITE", " ".join(entity.messages))
        self.assertEqual(elf.phase, Phase.ELF)
        self.assertIn("aide", " ".join(elf.messages).lower())
        self.assertEqual(choice.phase, Phase.CHOIX)
        self.assertEqual(choice.available_games, ("maze", "space_combat", "platformer"))
        self.assertEqual(choice.remaining_seconds, 50)

    def test_each_game_can_be_chosen_and_report_a_public_result(self):
        for game in ("maze", "space_combat", "platformer"):
            with self.subTest(game=game):
                session = Session(session_seconds=60, possession_seconds=2, warning_seconds=10)
                session.advance(0, "declencher_mystere")
                session.advance(2, None)
                session.advance(0, "continuer")
                playing = session.advance(0, f"choisir_{game}")
                self.assertEqual((playing.phase, playing.active_game), (Phase.JEU, game))
                self.assertTrue(playing.timer_visible)
                result = session.advance(3, None, game_result="victory")
                self.assertEqual((result.phase, result.active_game, result.game_result),
                                 (Phase.RESULTAT, game, "victory"))
                self.assertEqual(result.remaining_seconds, 55)

    def test_time_expiry_overrides_game_result_and_reset_clears_game(self):
        session = Session(session_seconds=10, possession_seconds=2, warning_seconds=3)
        session.advance(0, "declencher_mystere")
        session.advance(2, None)
        session.advance(0, "continuer")
        session.advance(0, "choisir_maze")
        ended = session.advance(10, None, game_result="victory")
        self.assertEqual((ended.phase, ended.active_game, ended.game_result), (Phase.FIN, None, None))
        self.assertEqual(ended.events, ("avertissement", "alarme"))
        self.assertFalse(ended.timer_visible)
        reset = session.advance(0, "reinitialiser")
        self.assertEqual(reset.phase, Phase.LABORATOIRE)
        self.assertIsNone(reset.active_game)
        self.assertEqual(session.advance(0, "declencher_mystere").remaining_seconds, 10)

    def test_reset_from_each_added_phase_starts_a_fresh_choice(self):
        for target in (Phase.CHOIX, Phase.JEU, Phase.RESULTAT):
            with self.subTest(target=target):
                session = Session(session_seconds=30, possession_seconds=2, warning_seconds=5)
                session.advance(0, "declencher_mystere")
                session.advance(2, None)
                session.advance(0, "continuer")
                if target in (Phase.JEU, Phase.RESULTAT):
                    session.advance(0, "choisir_space_combat")
                if target is Phase.RESULTAT:
                    defeated = session.advance(0, None, game_result="defeat")
                    self.assertEqual((defeated.phase, defeated.game_result),
                                     (Phase.RESULTAT, "defeat"))
                reset = session.advance(0, "reinitialiser")
                self.assertEqual((reset.phase, reset.active_game, reset.game_result),
                                 (Phase.LABORATOIRE, None, None))
                session.advance(0, "declencher_mystere")
                session.advance(2, None)
                choice = session.advance(0, "continuer")
                self.assertEqual(choice.available_games, ("maze", "space_combat", "platformer"))

    def test_choice_ends_at_global_deadline(self):
        session = Session(session_seconds=10, possession_seconds=2, warning_seconds=3)
        session.advance(0, "declencher_mystere")
        session.advance(2, None)
        session.advance(0, "continuer")
        ended = session.advance(8, "choisir_platformer")
        self.assertEqual((ended.phase, ended.active_game), (Phase.FIN, None))
        self.assertEqual(ended.events, ("avertissement", "alarme"))
