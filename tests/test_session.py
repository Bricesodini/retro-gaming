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
        self.assertIn("salle suivante", " ".join(end.messages))

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
    def test_free_games_can_be_replayed_and_deadline_stops_play(self):
        session = Session(20, 2, 5, room_digit=3)
        session.advance(0, "declencher_mystere")
        session.advance(2, None)
        session.advance(0, "continuer")
        session.advance(0, "choisir_maze")
        session.advance(1, None, "victory")
        session.advance(0, None)
        session.advance(0, "continuer")
        first = session.advance(0, "choisir_maze")
        self.assertEqual((first.active_game, first.free_mode, first.timer_visible),
                         ("maze", True, False))
        result = session.advance(1, None, "defeat")
        self.assertEqual((result.phase, result.free_mode), (Phase.RESULTAT, True))
        choices = session.advance(0, None)
        self.assertEqual((choices.phase, choices.available_games),
                         (Phase.LIBRE, ("maze", "space_combat", "platformer")))
        second = session.advance(0, "choisir_platformer")
        self.assertEqual(second.active_game, "platformer")
        warning = session.advance(11, None)
        self.assertEqual((warning.remaining_seconds, warning.events), (5, ("avertissement",)))
        end = session.advance(5, "choisir_space_combat", "victory")
        self.assertEqual((end.phase, end.events, end.active_game), (Phase.FIN, ("alarme",), None))
        self.assertIn("salle suivante", " ".join(end.messages))
        self.assertEqual(session.advance(1, "choisir_maze", "victory").events, ())

    def test_reset_from_free_mode_clears_room_result_and_starts_new_session(self):
        session = Session(20, 2, 5, room_digit=9)
        session.advance(0, "declencher_mystere")
        session.advance(2, None)
        session.advance(0, "continuer")
        session.advance(0, "choisir_maze")
        session.advance(0, None, "victory")
        session.advance(0, None)
        session.advance(0, "continuer")
        reset = session.advance(4, "reinitialiser")
        self.assertEqual(reset, SessionState(Phase.LABORATOIRE, None, ()))
        started = session.advance(0, "declencher_mystere")
        self.assertEqual((started.remaining_seconds, started.room_result,
                          started.free_mode, started.events), (20, None, False, ()))

    def test_victory_remains_the_room_result_if_time_expires_before_elf_screen(self):
        session = Session(10, 2, 3, room_digit=5)
        session.advance(0, "declencher_mystere")
        session.advance(2, None)
        session.advance(0, "continuer")
        session.advance(0, "choisir_maze")
        won = session.advance(7, None, "victory")
        self.assertEqual((won.phase, won.room_result, won.timer_visible),
                         (Phase.RESULTAT, "victory", False))
        ended = session.advance(1, None)
        self.assertEqual((ended.phase, ended.room_result, ended.events),
                         (Phase.FIN, "victory", ("alarme",)))

    def test_each_game_victory_reveals_configured_digit_then_opens_all_free_games(self):
        for game in ("maze", "space_combat", "platformer"):
            with self.subTest(game=game):
                session = Session(60, 2, 10, room_digit=7)
                session.advance(0, "declencher_mystere")
                session.advance(2, None)
                session.advance(0, "continuer")
                session.advance(0, f"choisir_{game}")
                result = session.advance(3, None, "victory")
                won = session.advance(0, None)
                self.assertEqual(result.phase, Phase.RESULTAT)
                self.assertEqual(won.phase, Phase.VICTOIRE)
                self.assertEqual(won.room_result, "victory")
                self.assertIn("7", " ".join(won.messages))
                self.assertFalse(won.timer_visible)
                free = session.advance(0, "continuer")
                self.assertEqual(free.phase, Phase.LIBRE)
                self.assertEqual(free.available_games, ("maze", "space_combat", "platformer"))
                self.assertTrue(free.free_mode)
                self.assertFalse(free.timer_visible)

    def test_deadline_overrides_final_entity_takeover(self):
        session = Session(session_seconds=10, possession_seconds=2, warning_seconds=0.5)
        session.advance(0, "declencher_mystere")
        session.advance(2, None)
        session.advance(0, "continuer")
        for game in ("maze", "space_combat", "platformer"):
            session.advance(0, f"choisir_{game}")
            session.advance(1, None, game_result="defeat")
            takeover = session.advance(0, None)
            self.assertEqual(takeover.phase, Phase.POSSESSION)
            if game != "platformer":
                self.assertEqual(session.advance(2, None).phase, Phase.ELF)
                session.advance(0, "continuer")

        ended = session.advance(1, None)
        self.assertEqual((ended.phase, ended.remaining_seconds), (Phase.FIN, 0))
        self.assertEqual(ended.events, ("avertissement", "alarme"))

    def test_elf_return_cannot_be_skipped_by_continue_at_takeover_boundary(self):
        session = Session(session_seconds=20, possession_seconds=2, warning_seconds=5)
        session.advance(0, "declencher_mystere")
        session.advance(2, None)
        session.advance(0, "continuer")
        session.advance(0, "choisir_maze")
        session.advance(0, None, game_result="defeat")
        session.advance(0, None)

        elf = session.advance(2, "continuer")

        self.assertEqual(elf.phase, Phase.ELF)
        self.assertEqual(session.advance(0, "continuer").phase, Phase.CHOIX)

    def test_deadline_overrides_defeat_recovery_and_choice(self):
        for phase in (Phase.POSSESSION, Phase.ELF, Phase.CHOIX):
            with self.subTest(phase=phase):
                session = Session(session_seconds=10, possession_seconds=2, warning_seconds=3)
                session.advance(0, "declencher_mystere")
                session.advance(2, None)
                session.advance(0, "continuer")
                session.advance(0, "choisir_maze")
                session.advance(1, None, game_result="defeat")
                current = session.advance(0, None)
                if phase in (Phase.ELF, Phase.CHOIX):
                    current = session.advance(2, None)
                if phase is Phase.CHOIX:
                    current = session.advance(0, "continuer")
                self.assertEqual(current.phase, phase)
                ended = session.advance(current.remaining_seconds, "choisir_platformer", "defeat")
                self.assertEqual((ended.phase, ended.remaining_seconds), (Phase.FIN, 0))
                self.assertEqual(ended.events, ("avertissement", "alarme"))
                self.assertEqual(ended.available_games, ())
                self.assertIsNone(ended.active_game)

    def test_third_distinct_loss_ends_after_entity_and_elf_without_fourth_game(self):
        session = Session(session_seconds=90, possession_seconds=2, warning_seconds=10)
        session.advance(0, "declencher_mystere")
        session.advance(2, None)
        session.advance(0, "continuer")
        for game in ("maze", "space_combat", "platformer"):
            started = session.advance(0, f"choisir_{game}")
            self.assertEqual((started.phase, started.active_game), (Phase.JEU, game))
            session.advance(1, None, game_result="defeat")
            entity = session.advance(0, None)
            self.assertEqual(entity.phase, Phase.POSSESSION)
            self.assertIn("ENTITE", " ".join(entity.messages))
            after_takeover = session.advance(2, None)
            if game != "platformer":
                self.assertEqual(after_takeover.phase, Phase.ELF)
                self.assertIn("nouvelle chance", " ".join(after_takeover.messages).lower())
                session.advance(0, "continuer")

        failure = after_takeover
        self.assertEqual(failure.phase, Phase.ECHEC)
        self.assertIn("ELF", " ".join(failure.messages))
        self.assertIn("ECHOU", " ".join(failure.messages))
        self.assertEqual(failure.available_games, ())
        self.assertIsNone(failure.active_game)
        self.assertNotIn("chiffre", " ".join(failure.messages).lower())
        self.assertEqual(session.advance(0, "choisir_maze"), failure)
        self.assertEqual(session.advance(0, "continuer"), failure)
        expired = session.advance(failure.remaining_seconds, None)
        self.assertEqual((expired.phase, expired.remaining_seconds), (Phase.FIN, 0))
        self.assertEqual(expired.events, ("avertissement", "alarme"))
        self.assertEqual(expired.room_result, "defeat")
        self.assertIn("salle suivante", " ".join(expired.messages))
        self.assertEqual(session.advance(0, "choisir_maze", "victory").phase, Phase.FIN)

    def test_defeat_brings_entity_then_elf_and_only_untried_choices(self):
        session = Session(session_seconds=90, possession_seconds=4, warning_seconds=10)
        session.advance(0, "declencher_mystere")
        session.advance(4, None)
        session.advance(0, "continuer")
        session.advance(0, "choisir_maze")

        lost = session.advance(5, None, game_result="defeat")
        takeover = session.advance(0, None)
        elf = session.advance(4, None)
        choice = session.advance(0, "continuer")

        self.assertEqual((lost.phase, lost.game_result), (Phase.RESULTAT, "defeat"))
        self.assertEqual(takeover.phase, Phase.POSSESSION)
        self.assertIn("ENTITE", " ".join(takeover.messages))
        self.assertEqual(takeover.remaining_seconds, 81)
        self.assertEqual(elf.phase, Phase.ELF)
        self.assertIn("nouvelle chance", " ".join(elf.messages).lower())
        self.assertEqual(choice.available_games, ("space_combat", "platformer"))
        self.assertEqual(session.advance(0, "choisir_maze").phase, Phase.CHOIX)
        self.assertEqual(session.advance(0, "choisir_platformer").active_game, "platformer")

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
