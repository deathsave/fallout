"""Tests the 3-bank drop targets."""

from tests.test_vault_multiball import BallHelpers


class TestThreeBank(BallHelpers):

    def bank(self):
        return self.machine.drop_target_banks['3bank']

    def drop(self, number):
        self.hit_switch_and_run('s_3b{}'.format(number), 1)

    def test_each_target_scores(self):
        self.start_game_and_plunge()
        before = self.machine.game.player.score
        self.drop(1)
        self.assertEqual(before + 300, self.machine.game.player.score)

    def test_bank_resets_when_all_down(self):
        self.start_game_and_plunge()
        self.mock_event('drop_target_bank_3bank_down')
        for n in (1, 2, 3):
            self.drop(n)
        self.assertEventCalled('drop_target_bank_3bank_down')
        # the reset coil fires; the targets come back up on the real machine
        for n in (1, 2, 3):
            self.release_switch_and_run('s_3b{}'.format(n), 1)
        self.assertEqual(0, self.bank().down)
