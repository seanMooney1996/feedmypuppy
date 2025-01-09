from gpiozero import DigitalOutputDevice, DigitalInputDevice
import time

dout = DigitalInputDevice(26)  # GPIO 26
sck = DigitalOutputDevice(19)  # GPIO 19

try:
    print("Toggling SCK pin...")
    while True:
        sck.on()
        time.sleep(0.5)
        sck.off()
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Exiting...")
