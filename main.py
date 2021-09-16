# Bluetooth Low Energy with Servo.
# Pin setup: Servo red to +5V (VIN),  black to Ground, signal (white or yellow) to GPIO15
# note that these are 3 adjacent pins so you can swap servo wire to use the original servo
# connector directly to +3.3v, GND, D15 (3.3v will also work for very small servos).
# large servos should always be powered externally.
from machine import Pin, PWM
from machine import Timer
from time import sleep_ms
import ubluetooth
import math
from servosguy import Servo

ble_msg = ""


class ESP32_BLE():
    def __init__(self, name):
        # Create internal objects for the onboard LED
        # blinking when no BLE device is connected
        # stable ON when connected
        self.led = Pin(2, Pin.OUT)
        self.timer1 = Timer(0)

        self.name = name
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.disconnected()
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()

    def connected(self):
        self.led.value(1)
        self.timer1.deinit()

    def disconnected(self):
        self.timer1.init(period=100, mode=Timer.PERIODIC, callback=lambda t: self.led.value(not self.led.value()))

    def ble_irq(self, event, data):
        global ble_msg

        if event == 1:  # _IRQ_CENTRAL_CONNECT:
            # A central has connected to this peripheral
            self.connected()

        elif event == 2:  # _IRQ_CENTRAL_DISCONNECT:
            # A central has disconnected from this peripheral.
            self.advertiser()
            self.disconnected()

        elif event == 3:  # _IRQ_GATTS_WRITE:
            # A client has written to this characteristic or descriptor.
            buffer = self.ble.gatts_read(self.rx)
            ble_msg = buffer.decode('UTF-8').strip()

    def register(self):
        # Nordic UART Service (NUS)
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'

        BLE_NUS = ubluetooth.UUID(NUS_UUID)
        BLE_RX = (ubluetooth.UUID(RX_UUID), ubluetooth.FLAG_WRITE)
        BLE_TX = (ubluetooth.UUID(TX_UUID), ubluetooth.FLAG_NOTIFY)

        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART,)
        ((self.tx, self.rx,),) = self.ble.gatts_register_services(SERVICES)

    def send(self, data):
        self.ble.gatts_notify(0, self.tx, data + '\n')

    def advertiser(self):
        name = bytes(self.name, 'UTF-8')
        adv_data = bytearray('\x02\x01\x02') + bytearray((len(name) + 1, 0x09)) + name
        self.ble.gap_advertise(100, adv_data)
        print(adv_data)
        print("\r\n")
        # adv_data
        # raw: 0x02010209094553503332424C45
        # b'\x02\x01\x02\t\tESP32BLE'
        #
        # 0x02 - General discoverable mode
        # 0x01 - AD Type = 0x01
        # 0x02 - value = 0x02

        # https://jimmywongiot.com/2019/08/13/advertising-payload-format-on-ble/
        # https://docs.silabs.com/bluetooth/latest/general/adv-and-scanning/bluetooth-adv-data-basics


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
    bmsg = ble_msg
    ble_msg = ""  # this way we will not repeat acting on the message multiple times.
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
