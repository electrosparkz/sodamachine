import time
import threading

import smbus2
import PyNAU7802
import RPi.GPIO as GPIO

from apds9930 import APDS9930

GPIO.setmode(GPIO.BCM)


class Sensors(object):
	def __init__(self, controller):
		self.controller = controller

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

		GPIO.setup(self.detectpin, GPIO.IN)
		GPIO.add_event_detect(self.detectpin, GPIO.BOTH, callback=self.update_bottle_state)

	def setup_scale(self):
		if self.scale.begin(self.bus):
			print("Found scale")
		self.scale.setZeroOffset(self.controller.conf.scale_cal_values['zero_cal']['empty'])
		self.scale.setCalibrationFactor(self.controller.conf.scale_cal_values['cal_value']['empty'])
		time.sleep(1)
		weight = self.scale.getWeight() * 1000
		if (weight > 5):
			print("Scale does not seem empty")
		else:
			print(f"Scale is empty: {weight}g")

	def setup_temp_sensor(self):
		config = [0x08, 0x00]
		self.bus.write_i2c_block_data(0x38, 0xE1, config)
		time.sleep(0.5)
		byt = self.bus.read_byte(0x38)
		print(byt)

	def setup_prox_sensor(self):
		# self.prox_sensor.proximity_gain = 1
		self.prox_sensor.enable_proximity_sensor()

	def update_bottle_state(self, channel):
		val = GPIO.input(self.detectpin)
		print(f"Pin state changed: {val}")
		self.bottle_present = val

	@property
	def proximity(self):
		self.i2c_access_lock.acquire()
		prox_val = self.prox_sensor.proximity
		self.i2c_access_lock.release()
		return prox_val

	def update_temp(self):
		measure_cmd = [0x33, 0x00]
		self.i2c_access_lock.acquire()
		self.bus.write_i2c_block_data(0x38, 0xAC, measure_cmd)
		time.sleep(0.5)
		data = self.bus.read_i2c_block_data(0x38,0x00)
		self.i2c_access_lock.release()
		temp = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
		ctemp = ((temp*200) / 1048576) - 50
		ftemp = (ctemp * 9/5) + 32

		self.temp = ftemp