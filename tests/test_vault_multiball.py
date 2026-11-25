"""Tests the vault lock and vault multiball."""

from tests.machine_test_case import FalloutMachineTestCase


class BallHelpers(FalloutMachineTestCase):

    """Helpers for moving balls around in a game (no tests of its own)."""

    def start_game_and_plunge(self):
        self.hit_and_release_switch('s_start')
        self.advance_time_and_run(4)
        self.assertModeRunning('base')
        self.release_switch_and_run('s_shooter_lane', 1)
        self.advance_time_and_run(4)
        self.assertEqual(1, self.machine.game.balls_in_play)

    def lock_ball(self):
        self.machine.default_platform.add_ball_to_device(
            self.machine.ball_devices.bd_lock)
        self.advance_time_and_run(6)

    def drain_ball(self):
        """Move one ball from the playfield into the trough."""
        self.machine.default_platform.add_ball_to_device(
            self.machine.ball_devices.bd_trough)
        self.advance_time_and_run(1)


class TestVaultMultiball(BallHelpers):

    def lock_three_and_start_multiball(self):
        lock = self.machine.multiball_locks.v_lock
        for locked in (1, 2):
            self.lock_ball()
            self.assertEqual(locked, lock.locked_balls)
            self.assertEqual(locked, self.machine.ball_devices.bd_lock.balls)
            # a replacement ball is served so play continues
            self.assertBallsOnPlayfield(1)
            self.assertEqual(1, self.machine.game.balls_in_play)

        self.lock_ball()
        # ejects wait out the 10s eject timeout because nothing hits a
        # playfield switch in the simulator
        self.advance_time_and_run(30)
        self.assertEqual(0, self.machine.ball_devices.bd_lock.balls)
        self.assertBallsOnPlayfield(3)
        self.assertEqual(3, self.machine.game.balls_in_play)

    def test_lock_three_starts_multiball(self):
        self.start_game_and_plunge()
        self.lock_three_and_start_multiball()
        self.assertEqual(1, self.machine.game.player.ball)
        # vault is empty again for the next vault multiball
        self.assertEqual(0, self.machine.multiball_locks.v_lock.locked_balls)

    def test_locks_carry_over_to_next_ball(self):
        self.start_game_and_plunge()
        self.lock_ball()
        self.lock_ball()
        self.drain_ball()
        self.advance_time_and_run(5)
        self.assertEqual(2, self.machine.game.player.ball)
        self.assertEqual(2, self.machine.multiball_locks.v_lock.locked_balls)
        self.release_switch_and_run('s_shooter_lane', 5)

        self.lock_ball()
        self.advance_time_and_run(30)
        self.assertEqual(0, self.machine.ball_devices.bd_lock.balls)
        self.assertBallsOnPlayfield(3)
        self.assertEqual(3, self.machine.game.balls_in_play)

    def test_multiball_ends_and_lock_works_again(self):
        self.start_game_and_plunge()
        self.lock_three_and_start_multiball()

        # let shoot again (10s) expire, then drain down to one ball
        self.advance_time_and_run(15)
        self.drain_ball()
        self.drain_ball()
        self.assertEqual(1, self.machine.game.balls_in_play)
        self.assertEqual(1, self.machine.game.player.ball)
        self.assertTrue(self.machine.multiball_locks.v_lock.enabled)

        # the vault can be locked again for a second multiball
        self.lock_ball()
        self.assertEqual(1, self.machine.multiball_locks.v_lock.locked_balls)
        self.assertEqual(1, self.machine.ball_devices.bd_lock.balls)

    def test_ball_into_vault_during_multiball_is_kicked_out(self):
        self.start_game_and_plunge()
        self.lock_three_and_start_multiball()
        self.assertFalse(self.machine.multiball_locks.v_lock.enabled)

        self.lock_ball()
        self.advance_time_and_run(15)
        self.assertEqual(0, self.machine.ball_devices.bd_lock.balls)
        self.assertEqual(0, self.machine.multiball_locks.v_lock.locked_balls)
        self.assertEqual(3, self.machine.game.balls_in_play)

    def assertVaultLights(self, lock1, lock2, lock3):
        self.assertLightColor('vlock1', lock1)
        self.assertLightColor('vlock2', lock2)
        self.assertLightColor('vlock3', lock3)

    def test_vault_lights_show_lock_progress(self):
        self.start_game_and_plunge()
        self.assertVaultLights('off', 'off', 'off')

        self.lock_ball()
        self.assertVaultLights('red', 'off', 'off')
        self.lock_ball()
        self.assertVaultLights('red', 'ffff00', 'off')

        # progress survives a drain to the next ball
        self.drain_ball()
        self.advance_time_and_run(5)
        self.assertEqual(2, self.machine.game.player.ball)
        self.release_switch_and_run('s_shooter_lane', 5)
        self.assertVaultLights('red', 'ffff00', 'off')

        # third lock: lights chase during the multiball
        self.lock_ball()
        seen = set()
        for _ in range(9):
            self.advance_time_and_run(.15)
            seen.add(tuple(str(self.machine.lights[name].get_color())
                           for name in ('vlock1', 'vlock2', 'vlock3')))
        self.assertEqual(3, len(seen), "vault lights should chase")

        # multiball over: lights reset for the next lock
        self.advance_time_and_run(40)
        self.drain_ball()
        self.drain_ball()
        self.assertEqual(1, self.machine.game.balls_in_play)
        self.assertVaultLights('off', 'off', 'off')
