"""Tests the rad meter and the mutation multiball."""

from tests.test_vault_multiball import BallHelpers


class TestMutationMultiball(BallHelpers):

    def rad_meter(self):
        return self.machine.state_machines.rad_meter_status.state

    def fill_rad_meter(self):
        for _ in range(10):
            self.post_event('logicblock_rad_spin_sequence_complete')
            self.advance_time_and_run(.1)

    def assertMultiballWithThreeBalls(self):
        # ejects wait out their timeouts in the simulator
        self.advance_time_and_run(30)
        self.assertBallsOnPlayfield(3)
        self.assertEqual(3, self.machine.game.balls_in_play)
        self.assertEqual(0, self.machine.ball_devices.bd_trough.balls)

    def test_ten_spins_fill_one_rad(self):
        self.start_game_and_plunge()
        self.assertEqual('rads0', self.rad_meter())
        for _ in range(10):
            self.hit_and_release_switch('s_rspinner')
            self.advance_time_and_run(.1)
        self.assertEqual('rads1', self.rad_meter())

    def test_full_meter_starts_mutation_multiball(self):
        self.start_game_and_plunge()
        self.fill_rad_meter()
        self.assertEqual('rads0', self.rad_meter(), "meter resets")
        self.assertMultiballWithThreeBalls()
        self.assertEqual(0, self.machine.ball_devices.bd_lock.balls)
        self.assertFalse(self.machine.multiball_locks.v_lock.enabled)

    def test_mutation_multiball_uses_trough_before_vault(self):
        self.start_game_and_plunge()
        self.lock_ball()            # vault 1, trough 1
        self.fill_rad_meter()
        self.assertMultiballWithThreeBalls()
        self.assertEqual(0, self.machine.ball_devices.bd_lock.balls)

    def test_mutation_multiball_releases_vault_when_trough_empty(self):
        self.start_game_and_plunge()
        self.lock_ball()
        self.lock_ball()            # vault 2, trough 0
        self.assertEqual(0, self.machine.ball_devices.bd_trough.balls)
        self.fill_rad_meter()
        self.assertMultiballWithThreeBalls()
        self.assertEqual(0, self.machine.ball_devices.bd_lock.balls)
        self.assertEqual(0, self.machine.multiball_locks.v_lock.locked_balls)

    def test_vault_lock_back_on_after_mutation_multiball(self):
        self.start_game_and_plunge()
        self.fill_rad_meter()
        self.assertMultiballWithThreeBalls()
        self.advance_time_and_run(15)   # shoot again over
        self.drain_ball()
        self.drain_ball()
        self.assertEqual(1, self.machine.game.balls_in_play)
        self.assertTrue(self.machine.multiball_locks.v_lock.enabled)
        self.assertLightColor('vlock1', 'off')
        self.lock_ball()
        self.assertEqual(1, self.machine.multiball_locks.v_lock.locked_balls)
        self.assertLightColor('vlock1', 'red')
