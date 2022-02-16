from gui import SodaGui
from config import SodaConfig
from pump_controller import PumpController


class SodaController(object):
    def __init__(self):
        self.conf = SodaConfig()
        self.gui = SodaGui(self)
        self.pc = PumpController(self)

    def run(self):
        self.gui.mainloop()


if __name__ == '__main__':
    ctrl = SodaController()
    ctrl.gui.display_flavor_picker()
    ctrl.run()
