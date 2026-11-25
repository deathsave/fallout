"""Shared base test case for MPF 0.80."""

import os

from mpf.tests.MpfMachineTestCase import MpfMachineTestCase
from mpf.tests.MpfTestCase import MpfTestCase


class FalloutMachineTestCase(MpfMachineTestCase):

    """Machine test case that works with MPF 0.80 (no mpf-mc).

    MPF 0.80's MpfMachineTestCase still tries to mock the old Kivy
    mpf-mc config players by importing ``mpfmc``, which no longer
    exists. In 0.80 slide_player, sound_player and widget_player are
    built into MPF core, so we skip that mock entirely.
    """

    def setUp(self):
        MpfTestCase.setUp(self)

    def get_config_file(self):
        return 'config.yaml'

    def get_machine_path(self):
        return os.path.abspath(os.path.join(
            os.path.realpath(__file__),
            os.pardir, os.pardir
        ))
