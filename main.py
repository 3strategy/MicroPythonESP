# Bluetooth Low Energy with Servo.
# Pin setup: Servo IS DISCONNECTED HERE.    red to +5V (VIN),  black to Ground, signal (white or yellow) to D15
# Pin setup hc-sr04.py red-vcc->3.3v, black-gnd->gnd, white-Trig->D13, brown-Echo-> D12
from machine import Pin, PWM
from time import sleep_ms
from servosguy import Servo
from esp32_ble import ESP32_BLE
from hcsr04 import HCSR04
from machine import Pin, I2C, TouchPad
import sys

touch5 = TouchPad(Pin(32))
led = Pin(2, Pin.OUT)
but = Pin(0, Pin.IN)
ble = ESP32_BLE("ESP32BLE")
debug = True
debug_to_ble = True

def maindebug(str):
    if debug:
        print(str)
        if debug_to_ble and ble.is_connected:
            ble.send(str)

servo1 = Servo(15, True, maindebug, 72, 28, 120)  # create a servo instance.
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
    maindebug(s)

def toggle_debug():
    global debug_to_ble
    if debug_to_ble:
        maindebug(f'set debug to : {not debug_to_ble}')
        debug_to_ble = not debug_to_ble
    else:
        debug_to_ble = not debug_to_ble
        maindebug(f'set debug to : {debug_to_ble}')

but.irq(trigger=Pin.IRQ_FALLING, handler=buttons_irq)
try:
  threshold5=[]
  for i in range(12): #This loop initializes the capacitive pin,
      #It creates an average which serves as benchmark for checking
      #whether or not the pin was touched.
      threshold5.append(touch5.read())
      sleep_ms(100)
  threshold5 = sum(threshold5)//len(threshold5)

  while True:
    bmsg = ble.msg
    touch5ratio = touch5.read()/threshold5  #read the pin and calculate ratio
    if 0.4 < touch5ratio <0.95:
        #this means a touch.
        ble.send("clementine")
    ble.msg = ""  # this way we will not repeat acting on the message multiple times.
    if bmsg == 'read_LED':  # phone is trying to read the Led state.
        maindebug('LED is ON.' if led.value() else 'LED is OFF')
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
    elif bmsg == 'debug':
        toggle_debug()
    # enable program close
    elif bmsg == 'stop':
        # even after main loop is exited.
        # How about the servo?
        # OPEN an REPL and notice how the servoe "alive" timer keeps printing.
        # So part of the program is still running.
        servo1.stoptimers()
        servo1 = None
        ble.send('stopping main loop')
        ble.ble.active(False)  # without this BLE would still function and accept connections
        sys.exit() # = None  # This will stop the servo
        break  # this effectively exits the main program loop.
        # but is the program really stopped? It's not!!!

    sleep_ms(50)  # Blocking code

except KeyboardInterrupt:
  pass
