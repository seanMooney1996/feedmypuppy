from gpiozero import Servo
from time import sleep

servo_pin1 = 14 
servo_pin2 = 15  

servo1 = Servo(
    servo_pin1,
    min_pulse_width=0.5/1000,  
    max_pulse_width=2.4/1000, 
    frame_width=20/1000  
)
servo2  = Servo(
    servo_pin2,
    min_pulse_width=0.5/1000,
    max_pulse_width=2.4/1000,
    frame_width=20/1000
)


def angle_to_value(angle):
    return -1.0 + (2.0 * angle / 180.0)


def shake_hatch():
        open_hatch()
        sleep(1)
        close_hatch()
        sleep(1)
        open_hatch()
        sleep(1)
        close_hatch()
        

def open_hatch():
        servo1.value = angle_to_value(180)
        servo2.value = angle_to_value(0)
        
        
def close_hatch():
        servo1.value = angle_to_value(90)
        servo2.value = angle_to_value(90)


def drop_food_sequence():
        servo1.value = angle_to_value(150)
        servo2.value = angle_to_value(30)
        sleep(1)
        servo1.value = angle_to_value(90)
        servo2.value = angle_to_value(90)
        
        
def main():
    print(" q to quit")
    while True:
        user_input = input("Enter command: ")
        if user_input in ["q", "quit", "exit"]:
            print("Exiting.")
            break
        elif user_input == "1":
            drop_food_sequence()
        elif user_input == "2":
            open_hatch() 
        elif user_input == "3":
            close_hatch()
        elif user_input == "4":
            shake_hatch()         


if __name__ == "__main__":
    main()
