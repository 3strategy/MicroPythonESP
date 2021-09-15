# This code is for ESP32
from machine import Pin
import time

led = Pin(2, Pin.OUT)  # this is the internal ESP32 blue led.
sw = Pin(0, Pin.IN)  # accessing the internal boot-select button.

# non-blocking operation of the led.

start_time = time.ticks_ms()
interval = 500  # 500ms
led_state = 0

while True:
    if time.ticks_ms() - start_time >= interval:
        start_time = time.ticks_ms()
        if led_state == 1:
            led_state = 0
        else:
            led_state = 1

    if sw.value() == 0:  # this loop is not blocked by sleep
        # so even a quick press on the switch will output tons of prints
        print('g4', time.ticks_ms())
        led.value(1)
    else:
        led.value(led_state)