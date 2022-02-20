import time
import PyNAU7802
import smbus2

# Create the bus
bus = smbus2.SMBus(1)

# Create the scale and initialize it
scale = PyNAU7802.NAU7802()
if scale.begin(bus):
    print("Connected!\n")
else:
    print("Can't find the scale, exiting ...\n")
    exit()

input("Press enter to start zero offset average no bottle")
empty_values = []

for i in range(10):
    scale.calculateZeroOffset()
    offset = scale.getZeroOffset()
    empty_values.append(offset)
    print(f"Last offset: {offset}")
    time.sleep(.5)

print(f"Averaged zero offset no bottle: {sum(empty_values)/len(empty_values)}")

scale.setZeroOffset(float(sum(empty_values)/len(empty_values)))

known_mass = float(input("Add known mass: "))

empty_cals = []

for i in range(10):
    scale.calculateCalibrationFactor(known_mass)
    cal = scale.getCalibrationFactor()
    empty_cals.append(cal)
    print(f"Last cal: {cal}")
    time.sleep(.5)

print(f"Averaged cal no bottle: {sum(empty_cals)/len(empty_cals)}")

input("Place empty small bottle and press enter to start")
small_values = []

for i in range(10):
    scale.calculateZeroOffset()
    offset = scale.getZeroOffset()
    small_values.append(offset)
    print(f"Last offset: {offset}")
    time.sleep(.5)

print(f"Averaged zero offset small bottle: {sum(small_values)/len(small_values)}")

scale.setZeroOffset(float(sum(small_values)/len(small_values)))

known_mass = float(input("Add known mass: "))

small_cals = []

for i in range(10):
    scale.calculateCalibrationFactor(known_mass)
    cal = scale.getCalibrationFactor()
    small_cals.append(cal)
    print(f"Last cal: {cal}")
    time.sleep(.5)

print(f"Averaged cal small bottle: {sum(small_cals)/len(small_cals)}")

input("Place empty large bottle and press enter to start")
large_values = []

for i in range(10):
    scale.calculateZeroOffset()
    offset = scale.getZeroOffset()
    large_values.append(offset)
    print(f"Last offset: {offset}")
    time.sleep(.5)

print(f"Averaged zero offset large bottle: {sum(large_values)/len(large_values)}")

scale.setZeroOffset(float(sum(large_values)/len(large_values)))

known_mass = float(input("Add known mass: "))

large_cals = []

for i in range(10):
    scale.calculateCalibrationFactor(known_mass)
    cal = scale.getCalibrationFactor()
    small_cals.append(cal)
    print(f"Last cal: {cal}")
    time.sleep(.5)

print(f"Averaged cal large bottle: {sum(large_cals)/len(large_cals)}")

