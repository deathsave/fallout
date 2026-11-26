"""Tests the VATS drop targets and the VATS shot hunt mode."""

from tests.test_vault_multiball import BallHelpers


class TestVats(BallHelpers):

    def drop(self, number):
        self.hit_switch_and_run('s_vats{}'.format(number), 1)

    def drop_all(self):
        for n in (1, 2, 3):
            self.drop(n)

    def score(self):
        return self.machine.game.player.score

    def vats_hits(self):
        return self.machine.game.player.vats_hits

    def bank(self):
        return self.machine.drop_target_banks.vats

    def hit_ramp(self, switch):
        self.hit_and_release_switch(switch)
        self.advance_time_and_run(.5)

    def hit_scoop(self):
        self.machine.default_platform.add_ball_to_device(
            self.machine.ball_devices.bd_scoop)
        self.advance_time_and_run(3)

    def test_all_three_drops_start_vats(self):
        self.start_game_and_plunge()
        self.drop(1)
        self.drop(2)
        self.assertModeNotRunning('vats')
        self.drop(3)
        self.assertModeRunning('vats')
        self.assertEqual(0, self.vats_hits())
        self.assertTrue(self.machine.timers.vats_timer.running)

    def test_each_shot_scores_once(self):
        self.start_game_and_plunge()
        self.drop_all()
        before = self.score()
        self.hit_ramp('s_center_ramp')
        self.assertEqual(before + 10000, self.score())
        self.assertEqual(1, self.vats_hits())
        # same shot again: no second VATS award
        self.hit_ramp('s_center_ramp')
        self.assertEqual(before + 10000, self.score())
        self.assertEqual(1, self.vats_hits())

    def test_all_four_shots_award_bonus_and_end_mode(self):
        self.start_game_and_plunge()
        self.drop_all()
        before = self.score()
        self.hit_ramp('s_left_ramp')      # base scores 1000 for this too
        self.hit_ramp('s_center_ramp')
        self.hit_ramp('s_right_ramp')
        self.hit_scoop()                  # base scores 1000 for this too
        self.assertEqual(4, self.vats_hits())
        self.assertEqual(before + 4 * 10000 + 50000 + 2 * 1000, self.score())
        self.advance_time_and_run(2)
        self.assertModeNotRunning('vats')
        # drop targets reset for the next VATS
        self.advance_time_and_run(1)
        self.assertFalse(self.bank().complete)
        self.drop_all()
        self.assertModeRunning('vats')

    def test_timer_runs_out(self):
        self.start_game_and_plunge()
        self.drop_all()
        self.advance_time_and_run(20)
        self.assertModeRunning('vats')
        self.advance_time_and_run(11)
        self.assertModeNotRunning('vats')
        self.advance_time_and_run(1)
        self.assertFalse(self.bank().complete)

    def test_every_drain_saved_during_vats(self):
        self.start_game_and_plunge()
        self.advance_time_and_run(15)     # ball start save over
        self.drop_all()
        self.assertTrue(self.machine.ball_saves.vats_ball_save.enabled)
        self.assertLightColor('shoot_again', 'lime')
        for _ in range(2):
            self.drain_ball()
            self.advance_time_and_run(5)
            self.assertEqual(1, self.machine.game.player.ball)
            self.assertEqual(1, self.machine.game.balls_in_play)
            self.assertModeRunning('vats')
            self.release_switch_and_run('s_shooter_lane', 1)

    def test_drain_after_vats_ends_the_ball(self):
        self.start_game_and_plunge()
        self.advance_time_and_run(15)
        self.drop_all()
        self.advance_time_and_run(31)     # VATS timer runs out
        self.assertModeNotRunning('vats')
        self.assertFalse(self.machine.ball_saves.vats_ball_save.enabled)
        self.assertLightColor('shoot_again', 'off')
        self.drain_ball()
        self.advance_time_and_run(5)
        self.assertEqual(2, self.machine.game.player.ball)
        self.assertFalse(self.bank().complete)

    def test_stim_pack_paused_during_vats(self):
        self.start_game_and_plunge()
        self.advance_time_and_run(15)
        for _ in range(5):                # fill the med meter
            self.post_event('logicblock_med_spin_sequence_complete')
            self.advance_time_and_run(.1)
        stim = self.machine.ball_saves.stim_pack
        self.assertTrue(stim.enabled)

        self.drop_all()
        self.assertFalse(stim.enabled, "VATS covers drains, stim pack waits")
        self.drain_ball()
        self.advance_time_and_run(5)
        self.assertEqual('med5', self.machine.state_machines.med_meter_status.state,
                         "a VATS save doesn't use up the stim pack")
        self.release_switch_and_run('s_shooter_lane', 1)

        self.advance_time_and_run(31)     # VATS over: stim pack back
        self.assertModeNotRunning('vats')
        self.assertTrue(stim.enabled)
        self.assertLightColor('stim_left', 'red')
