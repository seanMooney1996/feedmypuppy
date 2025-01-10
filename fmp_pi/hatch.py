from gpiozero import Servo
from time import sleep


class Hatch:
    def __init__(self):
        servo_pin1 = 14 
        servo_pin2 = 15          
        self.servo1 = Servo(
            servo_pin1,
            min_pulse_width=0.5/1000,  
            max_pulse_width=2.4/1000, 
            frame_width=20/1000  
        )
        self.servo2  = Servo(
            servo_pin2,
            min_pulse_width=0.5/1000,
            max_pulse_width=2.4/1000,
            frame_width=20/1000
        )


    def angle_to_value(self,angle):
        return -1.0 + (2.0 * angle / 180.0)
        
        
    def open_hatch(self):
            self.servo1.value = self.angle_to_value(180)
            self.servo2.value = self.angle_to_value(0)

        
    def close_hatch(self):
            self.servo1.value = self.angle_to_value(90)
            self.servo2.value = self.angle_to_value(90)


    def drop_food_sequence(self):
            self.servo1.value =  self.angle_to_value(130)
            self.servo2.value =  self.angle_to_value(50)
            sleep(1)
            self.servo1.value =  self.angle_to_value(90)
            self.servo2.value =  self.angle_to_value(90)
              


