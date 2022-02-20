import time
import threading

import smbus2
import PyNAU7802

from apds9930 import APDS9930


class Sensors(object):
    def __init__(self, controller, gpio):
        self.controller = controller
        self.gpio = gpio

        self.i2c_access_lock = threading.Lock()

        self.bus = smbus2.SMBus(1)

        self.scale = PyNAU7802.NAU7802()
        self.setup_scale()

        self.setup_temp_sensor()
        self.temp = None
        self.update_temp()

        self.prox_sensor = APDS9930(1)
        self.setup_prox_sensor()

        self.detectpin = 23

        self.bottle_present = False

        self.bottle_switch = None

        self.setup_bottle_switch()
        # self._button_thread()

        self._bottle_size = None


    def setup_bottle_switch(self):
        bottle_switch_thread = threading.Thread(target=lambda x: x._button_thread(), args=(self,),  daemon=True)
        bottle_switch_thread.start()

    def _button_thread(self):
        self.bottle_switch = self.gpio.Button(self.detectpin, pull_up=False, bounce_time=.5)
        print(dir(self.bottle_switch))
        self.bottle_switch.when_activated = self.update_bottle_state
        self.bottle_switch.when_deactivated = self.update_bottle_state
        while True:
            pass


    def setup_scale(self):
        if self.scale.begin(self.bus):
            print("Found scale")
        self.scale.setZeroOffset(self.controller.conf.scale_cal_values['zero_cal']['empty'])
        self.scale.setCalibrationFactor(self.controller.conf.scale_cal_values['cal_value']['empty'])
        time.sleep(1)
        weight = self.scale.getWeight() * 1000
        if (weight > 5):
            print(f"Scale does not seem empty: {weight}g")
        else:
            print("Scale is empty")

    def setup_temp_sensor(self):
        config = [0x08, 0x00]
        self.bus.write_i2c_block_data(0x38, 0xE1, config)
        time.sleep(0.5)
        byt = self.bus.read_byte(0x38)
        print(byt)

    def setup_prox_sensor(self):
        self.prox_sensor.enable_proximity_sensor()
        self.prox_sensor.proximity_gain = 1 

    def update_bottle_state(self, channel):
        time.sleep(.2)
        start_time = time.time()
        val = self.bottle_switch.is_active
        print(f"Pin state changed: {val}")
        if val:
            time.sleep(2)
            print(f"Size: {self.get_bottle_size()} - fill: {self.bottle_fill}")
        self.bottle_present = val
        print(f"Took: {time.time() - start_time}")

    @property
    def proximity(self):
        self.i2c_access_lock.acquire()
        prox_val = self.prox_sensor.proximity
        self.i2c_access_lock.release()
        return prox_val

    @property
    def bottle_fill(self):
        try:
            bottle_size = self.get_bottle_size(fresh=True)
            self.scale.setZeroOffset(self.controller.conf.scale_cal_values['zero_cal'][bottle_size])
            self.scale.setCalibrationFactor(self.controller.conf.scale_cal_values['cal_value'][bottle_size])
            print(f"Set calibration values for {bottle_size}")
        except:
            print("Unknown bottle size")

        weight_values = []
        for x in range(10):
            weight_values.append(self.scale.getWeight() * 1000)
        avg_weight = sum(weight_values)/len(weight_values)
        print(avg_weight)
        return avg_weight

    def get_bottle_size(self, fresh=False):
        if (not self._bottle_size or fresh):
            prox_values = []
            for x in range(20):
                val = self.proximity
                prox_values.append(val)
                print(f"Raw prox value: {val}")
            avg_prox = sum(prox_values)/len(prox_values)
            print(f"Average proximity: {avg_prox}")

            if (avg_prox < 45):
                self._bottle_size = "small"
            elif (48 < avg_prox):
                self._bottle_size = "large"
            else:
                self._bottle_size = "unknown"

        return self._bottle_size

    def update_temp(self):
        measure_cmd = [0x33, 0x00]
        self.i2c_access_lock.acquire()
        self.bus.read_byte(0x38)
        self.bus.write_i2c_block_data(0x38, 0xAC, measure_cmd)
        time.sleep(0.5)
        data = self.bus.read_i2c_block_data(0x38, 0x00, length=8)
        self.i2c_access_lock.release()
        temp = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
        ctemp = ((temp*200) / 1048576) - 50
        ftemp = (ctemp * 9/5) + 32

        self.temp = ftemp
