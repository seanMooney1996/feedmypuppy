from gpiozero import DigitalInputDevice, DigitalOutputDevice
import time

class HX711:
    def __init__(self, dout_pin, pd_sck_pin):
        self.dout = DigitalInputDevice(dout_pin)
        self.pd_sck = DigitalOutputDevice(pd_sck_pin)
        self.is_initialized = self.test_connection()

    def test_connection(self):
        """
        Check if the HX711 is connected properly by testing its output pin state.
        """
        if self.dout.value:
            print("HX711 detected. DOUT pin is HIGH (waiting for data).")
            return True
        else:
            print("Error: HX711 not detected. Check wiring!")
            return False

# Pin configuration for Raspberry Pi 5
DOUT_PIN = 5   # GPIO 5 (Pin 29)
PD_SCK_PIN = 6 # GPIO 6 (Pin 31)

# Initialize HX711
hx711 = HX711(DOUT_PIN, PD_SCK_PIN)

if hx711.is_initialized:
    print("HX711 is connected properly.")
    print("Try applying pressure to the load cell to ensure it is responsive.")
else:
    print("HX711 is not connected properly. Please check the wiring.")

try:
    while hx711.is_initialized:
        if hx711.dout.value:
            print("HX711 DOUT pin is HIGH (ready to send data).")
        else:
            print("HX711 DOUT pin is LOW (busy).")
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
