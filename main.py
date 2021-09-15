# Tested working on esp32-20210902-v1.17.bin
# to work with this example you need to have the "Serial Bluetooh" android app installed.
# You Do Not Need to Pair the device!!!
# once the code is running on the device, the led blinks rapidly.
# you should see on your thonny terminal (if cable is connected), the initial output:
#    MPY: soft reboot
#    bytearray(b'\x02\x01\x02\t\tESP32BLE')
#    (  not the REPL >>>  we are used to work with. If you have REPL press Ctrl+D to soft boot)

# on your phone:

#    open the Serial Bluetooth app,
#    press the app menu and select devices.
#    press the luetooth LE tab.
#    you should see ESP32BLE. Select it.
# the led should stop blinking (this is to show you are connected).
# now you can use the phone terminal to query the status of the LED.
# to do this, you need program the M4 macro on the terminal. Long press it to access the editing mode.
#   change the name to read_LED
#   change the Value to read_LED. No need to change anything else.
# press V to confirm.
# you can now Press read_LED.
# this is a bidirectional command, so you get a status on your Phone, but you also see in the terminal
# that the device received this command from your phone.
# each time you toggle the led on the device (pressing the boot button) the phone will get a message about it.

from machine import Pin
from machine import Timer
from time import sleep_ms
import ubluetooth

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


def buttons_irq(pin):
    led.value(not led.value())
    ble.send('LED state will be toggled.')
    print('LED state will be toggled.')


but.irq(trigger=Pin.IRQ_FALLING, handler=buttons_irq)

while True:
    if ble_msg == 'read_LED':
        print(ble_msg)
        ble_msg = ""
        print('LED is ON.' if led.value() else 'LED is OFF')
        ble.send('LED is ON.' if led.value() else 'LED is OFF')
    sleep_ms(100)
