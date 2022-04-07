import sched, time, signal, sys
from copy import deepcopy


class PumpController(object):
    def __init__(self, controller, smbus):
        self.controller = controller
        self.bus = smbus

        self.pump_address = 8

        self.last_dispense = 0

    def pump_start(self, channel, direction, steps, ml):
        command = []
        command.append(channel)
        if direction == "F":
            command.append(0x01)
        elif direction == "R":
            command.append(0x02)
        step_bytes = int(steps).to_bytes(2, "big")
        command.append(step_bytes[0])
        command.append(step_bytes[1])
        ml_bytes = int(ml).to_bytes(2, "big")
        command.append(ml_bytes[0])
        command.append(ml_bytes[1])
        with self.controller.i2c_lock:
            self.bus.write_i2c_block_data(self.pump_address, 0, command)

    def pump_stop(self, channel):
        command = []
        command.append(channel)
        command.extend([0x00] * 5)
        with self.controller.i2c_lock:
            self.bus.write_i2c_block_data(self.pump_address, 0, command)

    @property
    def status(self):
        with self.controller.i2c_lock:
            status = self.bus.read_i2c_block_data(self.pump_address, 0, 3)
            dispensed = int.from_bytes(bytes(status[1:]), "big")
            if dispensed != 0:
                self.last_dispense = dispensed
            return status[0], self.last_dispense


# class PumpController(object):
#     def __init__(self, controller, gpio):
#         self.controller = controller
#         self.gpio = gpio
#         self.scheduler = sched.scheduler(time.time, time.sleep)

#         self.clockline = 17
#         self.latchline = 27
#         self.dataline = 22

#         self.clock = None
#         self.latch = None
#         self.data = None

#         self.bitstate = [0, 0, 0, 0, 0, 0, 0, 0]

#         self.setup()

#         self.run = True

#         self.bitloop()

#     def setup(self):
#         print("Setup pins")
#         self.clock = self.gpio.DigitalOutputDevice(self.clockline)
#         self.latch = self.gpio.DigitalOutputDevice(self.latchline)
#         self.data = self.gpio.DigitalOutputDevice(self.dataline)

#     def bitloop(self):
#         print("Start loop")
#         clock_time = (13000 / 400) / 1000000

#         def pulsePin(pin, clock_time):
#             pin.on()
#             pin.off()
#             time.sleep(clock_time)

#         def outputValue(value,data,clock,latch):
#             # print(f"Outputting: {value}")
#             for bit in reversed(value):
#                 if bit:
#                     data.on()
#                 else:
#                     data.off()
#                 pulsePin(clock, clock_time)
#             pulsePin(latch, clock_time)


#         def update(obj):
#             outputValue(obj.bitstate, obj.data, obj.clock, obj.latch)
#             if obj.run:
#                 obj.scheduler.enter(clock_time, 1, update, (obj,))

#         update(self)
#         update_thread = threading.Thread(target=lambda x: x.run(), args=(self.scheduler,), daemon=True)
#         update_thread.start()

#     def on(self, index):
#         print(f"Turning on {index}")
#         self.bitstate[index] = 1

#     def off(self, index):
#         print(f"Turning off {index}")
#         if index == -1:
#             for i in range(8):
#                 self.bitstate[i] = 0
#         else:
#             self.bitstate[index] = 0



if __name__ == '__main__':
    controller = PumpController(None)

    run = True

    def end_me(sig, frame):
        global run
        run = False

    signal.signal(signal.SIGINT, end_me)


    sys.exit(0)
