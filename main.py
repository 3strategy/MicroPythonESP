# Bluetooth Low Energy with Servo.
# Pin setup: Servo IS DISCONNECTED HERE.    red to +5V (VIN),  black to Ground, signal (white or yellow) to D15
# Pin setup hc-sr04.py red-vcc->3.3v, black-gnd->gnd, white-Trig->D13, brown-Echo-> D12
from machine import Pin, PWM
from time import sleep_ms
from servosguy import Servo
from esp32_ble import ESP32_BLE
from hcsr04 import HCSR04
from machine import Pin, I2C

led = Pin(2, Pin.OUT)
but = Pin(0, Pin.IN)
ble = ESP32_BLE("ESP32BLE")
servo1 = Servo(15, True, True, 72, 28, 120)  # create a servo instance.
dist_sensor = HCSR04(trigger_pin=13, echo_pin=12, echo_timeout_us=1000000)  # red=5v, black=gnd, D13, D12
print('main program start after boot. with BLE Stop support')

def buttons_irq(pin):
    toggle_led()


def toggle_led():  # this shows Android can control your device.
    led.value(not led.value())
    if led.value():
        s = ' On'
    else:
        s = ' Off'
    s = 'LED turned ' + s
    ble.send(s)
    print(s)


but.irq(trigger=Pin.IRQ_FALLING, handler=buttons_irq)
try:
  while True:
    bmsg = ble.msg
    ble.msg = ""  # this way we will not repeat acting on the message multiple times.
    if bmsg == 'read_LED':  # phone is trying to read the Led state.
        print(bmsg)
        print('LED is ON.' if led.value() else 'LED is OFF')
        ble.send('LED is ON.' if led.value() else 'LED is OFF')
    # servo section.
    elif bmsg == 'servo_R':
        servo1.right(7)
    elif bmsg == 'servo_L':
        servo1.left(7)
    elif bmsg == 'tog_led':  # phone is trying to toggle the led
        toggle_led()
    # ultrasonic section
    elif bmsg == 'get_dist':  # phone requests distance
        ble.send(f'distance is: {round(dist_sensor.distance_cm(), 1)}')
    # enable program close
    elif bmsg == 'stop':
        ble.send('stopping main loop')
        ble.ble.active(False)  # without this BLE would still function and accept connections
        # even after main loop is exited.
        break  # this effectively exits the main program loop.
        # but is the program really stopped? It's not!!!
    sleep_ms(50)  # Blocking code

except KeyboardInterrupt:
  pass
