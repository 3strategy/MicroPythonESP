# ESP32 servo example.
# Pin setup: Servo red to +5V (VIN),  black to Ground, signal (white or yellow) to GPIO23
from machine import Pin, PWM
import time

p23 = Pin(23, Pin.OUT)  # Create a regular p23 GPIO object
pwm = PWM(p23)  # Create another object named pwm by attaching the pwm driver to pin 23

pwm.freq(50)  # Set the pulse every 20ms
s_min,s_max,step=36,120,7 # here minimum of 36 and not 20 is required for the duty cycle.

def servo(pin, angle): # turns the servo to input angle.
    print('angle', angle)
    pin.duty(angle)
    time.sleep(0.5)

for i in range(s_min, s_max, step):  # To rotate the servo from 0 to 180 degrees
    servo(pwm, i)  # 7 is a 10 degrees increment
for i in range(s_max, s_min, -step): servo(pwm, i)

