"""Tests the attract mode light show."""

from tests.machine_test_case import FalloutMachineTestCase


class TestAttractLightShow(FalloutMachineTestCase):

    def color(self, light):
        return str(self.machine.lights[light].get_color())

    def test_show_plays_and_loops(self):
        self.assertModeRunning('attract')
        # sample every light over one full loop (~13.8s) and make sure each
        # one the show drives actually changes
        lights = list(self.machine.lights.keys())
        seen = {name: set() for name in lights}
        for _ in range(150):
            self.advance_time_and_run(.1)
            for name in lights:
                seen[name].add(self.color(name))
        static = [name for name in lights if len(seen[name]) < 2]
        self.assertEqual([], static, "lights that never change in attract")

    def test_rad_meter_fills_in_order(self):
        self.assertModeRunning('attract')
        # re-sync to the start of the loop
        self.machine.events.post('mode_attract_stopping')
        self.advance_time_and_run(.1)
        self.machine.shows['attract_light_show'].play(priority=300, loops=-1)
        self.advance_time_and_run(.05)
        self.assertEqual('(0, 255, 0)', self.color('rads1'))
        self.assertEqual('(0, 0, 0)', self.color('rads2'))
        self.advance_time_and_run(.12 * 4)
        self.assertEqual('(0, 255, 0)', self.color('rads4'))
        self.assertEqual('(255, 255, 0)', self.color('rads5'))
        self.advance_time_and_run(.12 * 5)
        self.assertEqual('(255, 0, 0)', self.color('rads10'))

    def test_game_start_stops_show(self):
        self.hit_and_release_switch('s_start')
        self.advance_time_and_run(4)
        self.assertModeRunning('base')
        before = {n: self.color(n) for n in ('rads1', 'power1', 'vlock1', 'cap_left')}
        self.advance_time_and_run(3)
        after = {n: self.color(n) for n in ('rads1', 'power1', 'vlock1', 'cap_left')}
        self.assertEqual(before, after, "playfield lights steady once the game starts")
        self.assertEqual('(0, 128, 0)', self.color('rads1'))
