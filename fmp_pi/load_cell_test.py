from gpiozero import DigitalInputDevice, DigitalOutputDevice
import time


#chatgpt generated HX711 read_raw function
class HX711:
    def __init__(self):
        DOUT_PIN = 26 
        SCK_PIN = 19         
        self.dout = DigitalInputDevice(DOUT_PIN)
        self.pd_sck = DigitalOutputDevice(SCK_PIN)

    def read_raw(self):
        while self.dout.value:
            pass
        count = 0
        for _ in range(24):
            self.pd_sck.on()
            count = count << 1 | self.dout.value
            self.pd_sck.off()
            
        self.pd_sck.on()
        self.pd_sck.off()
        if count & 0x800000: 
            count -= 1 << 24
        
        return count
 


#values worked out during calibration
#empty bowl raw number
#scale factor to grams
scale_factor = 913.94966666666666
no_load = 296262.8 + (1.6 * scale_factor)
#weight of bowl full of food
full_bowl = 33

hx711 = HX711()

def get_weight():
    global scale_factor,no_load,full_bowl
    raw_value = sum(hx711.read_raw() for _ in range(10)) / 10
    weight = (raw_value - no_load) / scale_factor
    return weight


try:
    while True:
        weight = get_weight()
        print(f"Weight: {weight:.2f} grams")
        time.sleep(1) 
except KeyboardInterrupt:
    print("\nExiting...")
