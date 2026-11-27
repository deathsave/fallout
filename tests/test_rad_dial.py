"""Tests that the rad dial coil (c_rdial) fires whenever c_uv does."""

from tests.machine_test_case import FalloutMachineTestCase


class TestRadDial(FalloutMachineTestCase):

    def coil_state(self, name):
        return self.machine.coils[name].hw_driver.state

    def test_rdial_held_with_uv_in_attract(self):
        self.assertModeRunning('attract')
        self.assertEqual('enabled', self.coil_state('c_uv'))
        self.assertEqual('enabled', self.coil_state('c_rdial'))

    def test_rdial_on_same_switch_as_uv(self):
        uv = self.machine.autofire_coils['ac_uv']
        rdial = self.machine.autofire_coils['ac_rdial']
        self.assertEqual(uv.config['switch'], rdial.config['switch'])
        self.assertEqual('s_rspinner', rdial.config['switch'].name)
        self.assertEqual('0804-3', self.machine.coils['c_rdial'].config['number'])
        # both rules switch on and off together
        self.assertEqual(uv._enabled, rdial._enabled)
        self.hit_and_release_switch('s_start')
        self.advance_time_and_run(4)
        self.assertModeRunning('base')
        self.assertTrue(uv._enabled)
        self.assertTrue(rdial._enabled)
