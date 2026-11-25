"""Tests General/Base Functionality"""

from tests.machine_test_case import FalloutMachineTestCase


class TestGeneral(FalloutMachineTestCase):

    """Tests start-up sequence"""

    def test_start(self):
        self.assertModeRunning('attract')
        self.assertEqual(3,
            self.machine.ball_devices.bd_trough.balls)

    def test_game_start(self):
        """Start a game and make sure base mode and the ball run."""
        self.hit_and_release_switch('s_start')
        self.advance_time_and_run(4)
        self.assertIsNotNone(self.machine.game)
        self.assertModeRunning('base')
        self.assertEqual(1, self.machine.game.player.ball)
        self.hit_and_release_switch('s_rspinner')
        self.advance_time_and_run(1)
        self.assertEqual(100, self.machine.game.player.score)
