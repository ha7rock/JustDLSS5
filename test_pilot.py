"""Offline gates for the v1.9 desktop integration; no game is started."""
import unittest
from types import SimpleNamespace as NS
from threading import Event
from unittest.mock import patch
from core import dlss, installer
from frontend import pilot
from test_ui import entry

class PilotTests(unittest.TestCase):
    def test_anticheat_and_vr_are_rejected_before_trials(self):
        item=entry('Control')
        for protected,vr in ((True,False),(False,True)):
            with patch.object(installer,'check_supported',return_value=(True,'')), patch.object(pilot.anticheat,'detect',return_value=NS(present=protected)):
                with self.assertRaises(ValueError):
                    pilot.prepare(item,installer.Options(path=dlss.OPTI,vr=vr),NS())

    def test_route_options_are_independent_and_constrained(self):
        item=entry('Control');item.game.api='DX12'
        options=installer.Options(path=dlss.OPTI,fg=True,mfg=True)
        inspection=NS(support=NS(options=[dlss.OPTI,dlss.FEEDER]),fit={dlss.OPTI:(True,''),dlss.FEEDER:(True,'')},mfg_available=True)
        with patch.object(installer,'check_supported',return_value=(True,'')), patch.object(pilot.anticheat,'detect',return_value=NS(present=False)), patch.object(pilot.autopilot,'plan',return_value=[dlss.OPTI,dlss.FEEDER]), patch.object(pilot.autopilot,'may_start',return_value=(True,'')), patch.object(pilot.community,'fetch',return_value={}):
            _,choices,_=pilot.prepare(item,options,inspection)
        self.assertTrue(choices[dlss.OPTI].fg)
        self.assertFalse(choices[dlss.FEEDER].fg)
        self.assertFalse(choices[dlss.OPTI].mfg)
        self.assertTrue(choices[dlss.FEEDER].mfg)
        self.assertIsNot(choices[dlss.OPTI],options)

    def test_stop_blocks_install_and_launch_hooks(self):
        item=entry('Control');stop=Event();stop.set()
        def exercise(game,options,routes,hooks):
            with self.assertRaisesRegex(RuntimeError,'Stopped'):
                hooks.install(game,options)
            self.assertFalse(hooks.start(game)[0])
        with patch.object(pilot.autopilot,'run',side_effect=exercise), patch.object(installer,'install') as install, patch.object(pilot.autopilot,'start') as start:
            pilot.run(item,([dlss.OPTI],{dlss.OPTI:installer.Options(path=dlss.OPTI)},(True,'')),stop,lambda *args:None)
            install.assert_not_called();start.assert_not_called()

if __name__=='__main__': unittest.main()
