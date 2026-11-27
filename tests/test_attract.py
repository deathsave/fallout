"""Tests the attract mode light show."""

from tests.machine_test_case import FalloutMachineTestCase


class TestAttractLightShow(FalloutMachineTestCase):

    def color(self, light):
        return str(self.machine.lights[light].get_color())

    def test_show_plays_and_loops(self):
        self.assertModeRunning('attract')
        # sample every light over one full loop (~15.4s) and make sure each
        # one the show drives actually changes
        lights = list(self.machine.lights.keys())
        seen = {name: set() for name in lights}
        for _ in range(160):
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


class TestAttractSlides(FalloutMachineTestCase):

    """Replays the attract slide show against a model of the GMC stack.

    GMC ignores "play" for a slide already on the stack and shows the
    most recently added one, so a slide the show never removes keeps the
    loop from changing what's on screen.
    """

    def setUp(self):
        super().setUp()
        self.stack = []
        self.on_screen = []
        player = self.machine.show_controller.show_players['slides']
        original = player.play

        def play(settings, context, calling_context, priority=0, **kwargs):
            for name, entry in settings.items():
                action = entry.get('action', 'play')
                if action == 'play' and name not in self.stack:
                    self.stack.append(name)
                elif action == 'remove' and name in self.stack:
                    self.stack.remove(name)
            top = self.stack[-1] if self.stack else None
            if not self.on_screen or self.on_screen[-1] != top:
                self.on_screen.append(top)
            return original(settings, context, calling_context, priority,
                            **kwargs)
        player.play = play

    def test_slides_restart_when_show_loops(self):
        show = self.machine.shows['attract_display_show']
        show.play(priority=300, loops=-1)
        self.advance_time_and_run(34)            # a little over one loop
        first = list(self.on_screen)
        self.advance_time_and_run(33)
        expected = ['attract_slide1', 'dspc_animation_slide',
                    'show_final_scores', 'attract_slide2',
                    'show_high_scores', 'attract_slide3']
        self.assertEqual(expected, first[:6])
        self.assertEqual(expected * 2, self.on_screen[:12])
