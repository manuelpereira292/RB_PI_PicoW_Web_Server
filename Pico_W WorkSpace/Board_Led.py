from machine import Pin
from utime import sleep

# On Board Led
pin = Pin("LED", Pin.OUT, value=0)

# Led States
def led_blink():
    '''
    Led Blink
    '''
    for _n in range(2):
        pin.toggle()
        sleep(.5)

def led_on():
    '''
    Led On
    '''
    pin.on()
    sleep(1)

def led_off():
    '''
    Led Off
    '''
    pin.off()
    sleep(1)