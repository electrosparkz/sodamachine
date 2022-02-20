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

# Calculate the zero offset
print("Calculating the zero offset...")
scale.calculateZeroOffset()
print("The zero offset is : {0}\n".format(scale.getZeroOffset()))

print("Put a known mass on the scale.")
cal = float(input("Mass in kg? "))

# Calculate the calibration factor
print("Calculating the calibration factor...")
scale.calculateCalibrationFactor(cal)
print("The calibration factor is : {0:0.3f}\n".format(scale.getCalibrationFactor()))

input("Press [Enter] to measure a mass. ")
while  True:
    print("Mass is {0:0.3f} kg".format(scale.getWeight()))
