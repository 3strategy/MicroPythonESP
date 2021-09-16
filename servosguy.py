from machine import Pin, PWM
from machine import Timer
from time import sleep_ms
import math

class Servo:
    # note that center does not have to be average, center should be used for Trimming (fine tuning of the model centerpoint).
    def __init__(self, pinNum, fade=False, debug=False, center=72, min=28, max=120):
        self.pwm = PWM(Pin(pinNum), freq=50)
        self.min, self.max, self.center = min, max, center  # duty between about 40 and 115 (some take 28 to 120 and more).
        self.debug = debug
        self.position = self.pwm.duty()  # position will be a float for fading purposes.
        if self.position > max:
            self.position = self.center
            self.goto(self.center)  # sometimes initial duty is 512... ? ? !

        if fade:
            tim = Timer(-1)
            tim.init(period=100, mode=Timer.PERIODIC, callback=lambda t: self.fade())

    def goto(self, target):
        if target > self.max:
            target = self.max
        elif target < self.min:
            target = self.min

        self.position = target  # in case someone other than fade, moved the servo.
        target = int(round(target, 0))

        if self.debug:
            print('DUTY IS', self.pwm.duty(), 'move to ', target)
            sleep_ms(100)  # Blocking code
        self.pwm.duty(target)

    def fade(self):  # fades the servo back to center (called by timer)
        # duty = self.pwm.duty()
        prevpos = self.position  # for debugging
        self.position += 0.16 * (self.center - prevpos)  # self.center + 0.9*(self.center - prevpos)
        # step = int(0.11*(self.center - duty))
        if (math.fabs(self.position - self.center) > 0.35):  # we only want to make a move if it is meaningful.
            if self.debug:  # debug the servo fading numbers...
                print('fading', prevpos, ' to ', self.center, ' via ', self.position)
            self.goto(self.position)

    def right(self, step):
        self.goto(self.pwm.duty() + step)  # we can read the current servo position and use it

    def left(self, step):
        self.goto(self.pwm.duty() - step)
