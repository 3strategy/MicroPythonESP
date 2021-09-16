# Bluetooth Low Energy with Servo.
# Pin setup: Servo red to +5V (VIN),  black to Ground, signal (white or yellow) to D15
from machine import Pin, PWM
from time import sleep_ms
from servosguy import Servo
from esp32_ble import ESP32_BLE

led = Pin(2, Pin.OUT)
but = Pin(0, Pin.IN)
ble = ESP32_BLE("ESP32BLE")
servo1 = Servo(15, True)  # Servo(15, True,28,120,True)  # Servo(23, True) create a servo instance.


def buttons_irq(pin):
    toggle_led()


def toggle_led():
    led.value(not led.value())
    if led.value():
        s = ' On'
    else:
        s = ' Off'
    s = 'LED turned ' + s
    ble.send(s)
    print(s)


but.irq(trigger=Pin.IRQ_FALLING, handler=buttons_irq)

while True:
    bmsg = ble.msg
    ble.msg = ""  # this way we will not repeat acting on the message multiple times.
    if bmsg == 'read_LED':
        print(bmsg)
        print('LED is ON.' if led.value() else 'LED is OFF')
        ble.send('LED is ON.' if led.value() else 'LED is OFF')
    elif bmsg == 'servo_R':
        servo1.right(7)
    elif bmsg == 'servo_L':
        servo1.left(7)
    elif bmsg == 'tog_led':
        toggle_led()
    sleep_ms(100)  # Blocking code
