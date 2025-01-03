from gpiozero import Servo
from time import sleep

# Set the GPIO pin for the servo
servo = Servo(14)

# Move the servo to different positions
try:
    while True:
        print("Moving to -1 (min position)")
        servo.min()  # Move to the minimum position
        sleep(2)  # Wait for 2 seconds

        print("Moving to 0 (middle position)")
        servo.mid()  # Move to the middle position
        sleep(2)  # Wait for 2 seconds

        print("Moving to 1 (max position)")
        servo.max()  # Move to the maximum position
        sleep(2)  # Wait for 2 seconds

except KeyboardInterrupt:
    print("Program stopped")