#This code is for ESP32
from machine import Pin
import time

led = Pin(2, Pin.OUT)  # this is the internal ESP32 blue led.
sw = Pin(0, Pin.IN)  # accessing the internal boot-select button.

# another example of blinking the internal led.

while True:
    led(1)
    time.sleep(0.6)  # this sleep code better resembles the more traditional MCU c code
    led(0)
    time.sleep(0.1)
    print(sw.value(), 'gg2')
