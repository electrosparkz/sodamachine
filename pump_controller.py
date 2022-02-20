import threading

import sched, time, signal, sys
from copy import deepcopy

try:
    import RPi.GPIO as GPIO
except ImportError:
    from unittest.mock import MagicMock
    GPIO = MagicMock()

GPIO.setmode(GPIO.BCM)


class PumpController(object):
    def __init__(self, controller):
        self.controller = controller

        self.scheduler = sched.scheduler(time.time, time.sleep)

        self.clockline = 17
        self.latchline = 27
        self.dataline = 22

        self.lockline = 23
        self.enableline = 5

        self.bitstate = [0, 0, 0, 0, 0, 0, 0, 0]

        self.setup()

        self.run = True

        self.bitloop()

    def __del__(self):
        GPIO.output(self.enableline, 1)
        GPIO.cleanup()

    def setup(self):
        print("Setup pins")
        GPIO.setup((self.clockline, self.latchline, self.dataline, self.enableline), GPIO.OUT)
        GPIO.output((self.clockline, self.latchline, self.dataline), 0)
        GPIO.output(self.enableline, 0)  # active low

    def bitloop(self):
        print("Start loop")
        clock_time = (13000 / 400) / 1000000

        def pulsePin(pin, clock_time):
            GPIO.output(pin, 1)
            GPIO.output(pin, 0)
            time.sleep(clock_time)


        def outputValue(value,data,clock,latch):
            # print(f"Outputting: {value}")
            for bit in reversed(value):
                GPIO.output(data, 1 if bit == 1 else 0)
                pulsePin(clock, clock_time)
            pulsePin(latch, clock_time)


        def update(obj):
            outputValue(obj.bitstate, obj.dataline, obj.clockline, obj.latchline)
            if obj.run:
                obj.scheduler.enter(clock_time, 1, update, (obj,))

        update(self)
        update_thread = threading.Thread(target=lambda x: x.run(), args=(self.scheduler,), daemon=True)
        update_thread.start()

    def on(self, index):
        print(f"Turning on {index}")
        self.bitstate[index] = 1

    def off(self, index):
        print(f"Turning off {index}")
        if index == -1:
            for i in range(8):
                self.bitstate[i] = 0
        else:
            self.bitstate[index] = 0



if __name__ == '__main__':
    controller = PumpController(None)

    run = True

    def end_me(sig, frame):
        global run
        run = False

    signal.signal(signal.SIGINT, end_me)

    print("Entering test loop")
    while run:
        for i in range(8):
            controller.on(i)
            time.sleep(.5)
            controller.off(i)
            time.sleep(.5)
        for i in range(8):
            controller.on(i)
            time.sleep(.5)
        time.sleep(2)
        controller.off(0)
    controller.off(-1)
    sys.exit(0)
