"""Tests the stim pack ball save earned by filling the med meter."""

from tests.test_vault_multiball import BallHelpers


class TestStimPack(BallHelpers):

    def med_meter(self):
        return self.machine.state_machines.med_meter_status.state

    def stim_pack(self):
        return self.machine.ball_saves.stim_pack

    def fill_med_meter(self):
        for _ in range(5):
            self.post_event('logicblock_med_spin_sequence_complete')
            self.advance_time_and_run(.1)
        self.assertEqual('med5', self.med_meter())

    def wait_for_ball_start_save_to_end(self):
        self.advance_time_and_run(15)
        self.assertFalse(self.machine.ball_saves.ball_start_ball_save.enabled)

    def assertStimLights(self, color):
        self.assertLightColor('stim_left', color)
        self.assertLightColor('stim_right', color)

    def test_full_meter_saves_next_drain_then_resets(self):
        self.start_game_and_plunge()
        self.wait_for_ball_start_save_to_end()
        self.assertFalse(self.stim_pack().enabled)
        self.assertStimLights('off')

        self.fill_med_meter()
        self.assertTrue(self.stim_pack().enabled)
        self.assertStimLights('red')

        # drain: the stim pack saves the ball instead of ending it
        self.drain_ball()
        self.advance_time_and_run(5)
        self.assertEqual(1, self.machine.game.player.ball)
        self.assertEqual(1, self.machine.game.balls_in_play)
        self.assertFalse(self.stim_pack().enabled)
        self.assertStimLights('off')
        self.assertEqual('med0', self.med_meter(), "meter resets")

        # with the stim pack used, the next drain ends the ball
        self.release_switch_and_run('s_shooter_lane', 1)
        self.wait_for_ball_start_save_to_end()
        self.drain_ball()
        self.advance_time_and_run(5)
        self.assertEqual(2, self.machine.game.player.ball)

    def test_meter_can_be_refilled_for_another_save(self):
        self.start_game_and_plunge()
        self.wait_for_ball_start_save_to_end()
        self.fill_med_meter()
        self.drain_ball()
        self.advance_time_and_run(5)
        self.assertEqual('med0', self.med_meter())

        self.release_switch_and_run('s_shooter_lane', 1)
        self.wait_for_ball_start_save_to_end()
        self.fill_med_meter()
        self.assertTrue(self.stim_pack().enabled)
        self.drain_ball()
        self.advance_time_and_run(5)
        self.assertEqual(1, self.machine.game.player.ball)

    def test_waits_for_ball_start_save(self):
        self.start_game_and_plunge()
        self.assertTrue(self.machine.ball_saves.ball_start_ball_save.enabled)
        self.fill_med_meter()
        self.assertFalse(self.stim_pack().enabled,
                         "not while the ball start save covers the ball")
        self.assertStimLights('off')

        self.wait_for_ball_start_save_to_end()
        self.assertTrue(self.stim_pack().enabled)
        self.assertStimLights('red')

    def test_multiball_drain_does_not_use_it(self):
        self.start_game_and_plunge()
        self.wait_for_ball_start_save_to_end()
        self.fill_med_meter()

        # vault multiball: 3 balls in play
        for _ in range(3):
            self.lock_ball()
        self.advance_time_and_run(30)
        self.assertEqual(3, self.machine.game.balls_in_play)
        self.advance_time_and_run(15)       # multiball shoot again over

        self.drain_ball()
        self.assertEqual(2, self.machine.game.balls_in_play)
        self.assertTrue(self.stim_pack().enabled)
        self.assertEqual('med5', self.med_meter())
        self.assertStimLights('red')

        # last-ball drain is saved
        self.drain_ball()
        self.drain_ball()
        self.advance_time_and_run(5)
        self.assertEqual(1, self.machine.game.player.ball)
        self.assertEqual('med0', self.med_meter())
