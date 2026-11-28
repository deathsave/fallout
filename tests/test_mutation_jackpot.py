"""Tests the mutation jackpot that runs during mutation multiball."""

from tests import test_mutation_multiball


class TestMutationJackpot(test_mutation_multiball.TestMutationMultiball):

    # don't rerun the inherited mutation multiball tests here
    test_ten_spins_fill_one_rad = None
    test_full_meter_starts_mutation_multiball = None
    test_mutation_multiball_uses_trough_before_vault = None
    test_mutation_multiball_releases_vault_when_trough_empty = None
    test_vault_lock_back_on_after_mutation_multiball = None

    def jackpot(self):
        return self.machine.game.player.mutation_jackpot

    def spin(self, times):
        for _ in range(times):
            self.hit_and_release_switch('s_rspinner')
            self.advance_time_and_run(.1)

    def start_mutation_multiball(self):
        self.start_game_and_plunge()
        self.fill_rad_meter()
        self.assertMultiballWithThreeBalls()
        self.assertModeRunning('mutation_jackpot')

    def test_not_running_outside_multiball(self):
        self.start_game_and_plunge()
        self.assertModeNotRunning('mutation_jackpot')
        self.assertLightColor('cross2', 'off')

    def test_ramps_lit_red(self):
        self.start_mutation_multiball()
        for light in ('cross2', 'cross4', 'cross6'):
            self.assertLightColor(light, 'red')
        for light in ('cross1', 'cross3', 'cross5', 'cross7'):
            self.assertLightColor(light, 'off')

    def test_spins_build_jackpot(self):
        self.start_mutation_multiball()
        self.assertEqual(0, self.jackpot())
        self.spin(5)
        self.assertEqual(25000, self.jackpot())

    def test_each_ramp_collects(self):
        self.start_mutation_multiball()
        for ramp in ('s_left_ramp', 's_center_ramp', 's_right_ramp'):
            self.spin(3)
            score = self.machine.game.player.score
            self.hit_and_release_switch(ramp)
            self.advance_time_and_run(.1)
            gained = self.machine.game.player.score - score
            self.assertGreaterEqual(gained, 15000, ramp)
            self.assertEqual(0, self.jackpot(), "jackpot resets after " + ramp)
        self.assertEqual(3, self.machine.game.player.mutation_jackpots_collected)

    def test_ramp_without_multiball_collects_nothing(self):
        self.start_game_and_plunge()
        self.spin(3)
        self.hit_and_release_switch('s_left_ramp')
        self.advance_time_and_run(.1)
        self.assertEqual(0, self.machine.game.player.mutation_jackpots_collected)

    def test_ends_with_multiball(self):
        self.start_mutation_multiball()
        self.advance_time_and_run(15)   # shoot again over
        self.drain_ball()
        self.drain_ball()
        self.assertEqual(1, self.machine.game.balls_in_play)
        self.assertModeNotRunning('mutation_jackpot')
        self.assertLightColor('cross2', 'off')
