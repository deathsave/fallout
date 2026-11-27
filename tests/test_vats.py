"""Tests the VATS drop targets and the VATS shot hunt mode."""

from mpf.core.rgb_color import RGBColor

from tests.test_vault_multiball import BallHelpers


class TestVats(BallHelpers):

    def drop(self, letter):
        self.hit_switch_and_run('s_{}'.format(letter), 1)

    def drop_all(self):
        for letter in 'vats':
            self.drop(letter)

    def score(self):
        return self.machine.game.player.score

    def vats_hits(self):
        return self.machine.game.player.vats_hits

    def bank(self):
        return self.machine.drop_target_banks.vats

    # crosshair insert number -> how to make that shot in the simulator
    SHOTS = {
        1: 's_lspinner',
        2: 's_left_ramp',
        3: 'bd_lock',
        4: 's_center_ramp',
        5: 'bd_scoop',
        6: 's_right_ramp',
        7: 's_rspinner',
    }

    def make_shot(self, switch_or_device):
        if switch_or_device.startswith('bd_'):
            self.machine.default_platform.add_ball_to_device(
                self.machine.ball_devices[switch_or_device])
            self.advance_time_and_run(3)
        else:
            self.hit_and_release_switch(switch_or_device)
            self.advance_time_and_run(.5)

    def lit(self):
        """Crosshair numbers whose insert is red."""
        red = RGBColor('red')
        return [n for n in range(1, 8)
                if self.machine.lights['cross{}'.format(n)].get_color() == red]

    def lit_one(self):
        lit = self.lit()
        self.assertEqual(1, len(lit), "exactly one crosshair is lit")
        return lit[0]

    def hit_lit(self):
        """Hit the lit crosshair's shot directly (no base-mode scoring)."""
        n = self.lit_one()
        shot = [s for s in self.machine.shots
                if s.name.startswith('vats_') and s.enabled][0]
        shot.hit()
        self.advance_time_and_run(.1)
        return n

    def light_only(self, n):
        for shot in self.machine.shots:
            if shot.name.startswith('vats_'):
                shot.disable()
        self.post_event('vats_light_cross{}'.format(n))
        self.advance_time_and_run(.1)

    def test_all_four_drops_start_vats(self):
        self.start_game_and_plunge()
        self.drop('v')
        self.drop('a')
        self.drop('t')
        self.assertModeNotRunning('vats')
        self.assertEqual([], self.lit())
        self.drop('s')
        self.assertModeRunning('vats')
        self.assertEqual(0, self.vats_hits())
        self.assertTrue(self.machine.timers.vats_timer.running)
        self.lit_one()

    def test_each_crosshair_shot_counts_when_lit(self):
        self.start_game_and_plunge()
        for n, how in self.SHOTS.items():
            with self.subTest(crosshair=n):
                self.drop_all()
                self.assertModeRunning('vats')
                self.light_only(n)    # in place of the random pick
                self.advance_time_and_run(.1)
                self.assertEqual([n], self.lit())
                self.make_shot(how)
                self.assertEqual(1, self.vats_hits())
                self.lit_one()                    # a new crosshair is lit
                self.advance_time_and_run(31)     # time out, bank resets
                self.assertModeNotRunning('vats')
                self.advance_time_and_run(1)

    def test_center_spinner_does_not_count(self):
        self.start_game_and_plunge()
        self.drop_all()
        self.light_only(4)
        self.make_shot('s_cspinner')
        self.assertEqual(0, self.vats_hits())
        self.assertEqual([4], self.lit())

    def test_unlit_shot_does_nothing(self):
        self.start_game_and_plunge()
        self.drop_all()
        n = self.lit_one()
        other = 2 if n != 2 else 6        # a ramp that isn't lit
        self.make_shot(self.SHOTS[other])
        self.assertEqual(0, self.vats_hits())
        self.assertEqual([n], self.lit())

    def test_hit_scores_resets_timer_and_lights_another(self):
        self.start_game_and_plunge()
        self.drop_all()
        self.advance_time_and_run(20)
        before = self.score()
        first = self.hit_lit()
        self.assertEqual(before + 10000, self.score())
        self.assertEqual(1, self.vats_hits())
        self.assertEqual(30, self.machine.timers.vats_timer.ticks)
        self.assertNotEqual(first, self.lit_one())
        # the fresh 30 seconds carries it past the original deadline
        self.advance_time_and_run(20)
        self.assertModeRunning('vats')

    def test_four_hits_complete_vats(self):
        self.start_game_and_plunge()
        self.drop_all()
        before = self.score()
        for _ in range(3):
            self.hit_lit()
            self.advance_time_and_run(25)  # each hit beats its own timer
        self.assertModeRunning('vats')
        self.hit_lit()
        self.assertEqual(4, self.vats_hits())
        self.assertEqual(before + 4 * 10000 + 200000, self.score())
        self.assertModeNotRunning('vats')
        self.assertEqual([], self.lit())
        # drop targets reset for the next VATS
        self.advance_time_and_run(1)
        self.assertFalse(self.bank().complete)
        self.drop_all()
        self.assertModeRunning('vats')
        self.assertEqual(0, self.vats_hits())

    def test_timer_runs_out(self):
        self.start_game_and_plunge()
        self.drop_all()
        self.hit_lit()
        self.advance_time_and_run(29)
        self.assertModeRunning('vats')
        self.advance_time_and_run(2)
        self.assertModeNotRunning('vats')
        self.assertEqual([], self.lit())
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
