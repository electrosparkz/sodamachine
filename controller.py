import os
import sys
import signal
import gpiozero

from gui import SodaGui
from config import SodaConfig
from pump_controller import PumpController
from sensors import Sensors
from state import SodaState

class SodaController(object):
    def __init__(self):
        self.conf = SodaConfig()
        self.state = SodaState()
        self.sensors = Sensors(self, gpiozero)
        self.pc = PumpController(self, gpiozero)
        self.gui = SodaGui(self)

    def bottle_inserted(self):
        self.gui.display_bottle_inserted()

    def bottle_removed(self):
        self.pc.off(-1)
        self.gui.display_goodbye()

    def run(self):
        signal.signal(signal.SIGINT, self.shutdown)
        self.gui.mainloop()

    def shutdown(self, signal, frame):
        self.pc.off(-1)
        sys.exit(0)


if __name__ == '__main__':
    os.environ['DISPLAY'] = ":0.0"
    ctrl = SodaController()
    ctrl.gui.display_idle_screen()
    ctrl.run()
