import sys
import signal
from gui import SodaGui
from config import SodaConfig
from pump_controller import PumpController
from sensors import Sensors

class SodaController(object):
    def __init__(self):
        self.conf = SodaConfig()
        self.sensors = Sensors(self)
        self.pc = PumpController(self)
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
    ctrl = SodaController()
    ctrl.gui.display_idle_screen()
    ctrl.run()
