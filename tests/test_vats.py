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

    def test_ball_end_stops_vats(self):
        self.start_game_and_plunge()
        self.advance_time_and_run(15)     # ball start save over
        self.drop_all()
        self.assertModeRunning('vats')
        self.drain_ball()
        self.advance_time_and_run(5)
        self.assertModeNotRunning('vats')
        self.assertEqual(2, self.machine.game.player.ball)
        self.assertFalse(self.bank().complete)
