from gpiozero import DigitalInputDevice, DigitalOutputDevice
import time


#chatgpt generated HX711 read_raw function
class Load_Cell:
    def __init__(self):
        DOUT_PIN = 26 
        SCK_PIN = 19         
        self.dout = DigitalInputDevice(DOUT_PIN)
        self.pd_sck = DigitalOutputDevice(SCK_PIN)
        self.scale_factor = 913.94966666666666
        self.no_load = 296262.8 + (1.6 * self.scale_factor)
        self.full_bowl = 33
        self.weight_tolerance = 0.5
        
        
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
    
    
    def get_weight_in_grams(self):
        raw_value = sum(self.read_raw() for _ in range(10)) / 10
        weight = (raw_value - self.no_load) / self.scale_factor
        print("weight in grams ",weight)
        return weight


    def is_within_tolerance(self, actual_weight, target_weight):
        difference = abs(actual_weight - target_weight)
        return difference <= self.weight_tolerance
    
    
    def is_full_bowl(self):
        weight_now = self.get_weight_in_grams()
        return self.is_within_tolerance(weight_now, self.full_bowl) or (weight_now >= self.full_bowl)


    def is_at_weight(self, weight):
        return self.is_within_tolerance(self.get_weight_in_grams(), weight)
    
    
    def is_empty(self):
        return self.is_within_tolerance(self.get_weight_in_grams(), self.no_load)





