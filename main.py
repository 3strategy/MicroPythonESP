# ESP32 servo example.
from machine import Pin, PWM
import time

class Servo:
    min = 36
    max = 120

    def __init__(self, pinNum, debug=False):
        self.pwm = PWM(Pin(pinNum), freq=50)
        self.debug=debug
    def move(self, target):
        if target>Servo.max:
            target = Servo.max
        elif target <Servo.min:
            target =Servo.min
        if self.debug:
            print("move to ", target)
        self.pwm.duty(target)
#class ends here.

# almost the same servo example, written OOP:
# Pin setup: Servo red to +5V (VIN),  black to Ground, signal (white or yellow) to GPIO23

servo1 = Servo(23)  # Servo(23,True) create a servo instance.

for i in range(29, 140, 7):  # To rotate the servo from 0 to 180 degrees
    servo1.move(i) #servo(pwm1, i)  # 7 is a 10 degrees increment
    time.sleep(0.5)
