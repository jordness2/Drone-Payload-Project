import RPi.GPIO as GPIO
import time


# speed% = (<time_ns>-1.5)*100
# speed setting: <time_ns>/((1/50)*1000*1000)*100
# min value: 2 = Reverse/Up (max speed) -> 6.5
# max value: 12 = Forward/Down (max speed) -> 7.5
NOMINAL=7 # the 'zero' PWM %age
RANGE=5   # maximum variation above/below NOMINAL
MODIFIER=3# the value to change by, must be smaller than RANGE
#TIME=5    # time in seconds to keep motor on
CYCLES=18 # number of cycles to perform

class servo:
    def __init__(self):
        self.p = None
        

    def start(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(4, GPIO.OUT, initial=False)
        self.p = GPIO.PWM(4,50)
        self.p.start(NOMINAL)

    # 0 = off, 1 = down, -1 = up
    def motor_change(self, mode):
        p = self.p
        if mode > 0:
            # Extend tube down
            #p.ChangeDutyCycle(NOMINAL+MODIFIER)
            #time.sleep(TIME)
            for x in range(CYCLES):
                p.ChangeDutyCycle(NOMINAL+5)
                time.sleep(1)
                p.ChangeDutyCycle(NOMINAL-1)
                time.sleep(0.25)
                p.ChangeDutyCycle(NOMINAL)
                time.sleep(0.25)
        elif mode < 0:
            # Bring tube up
            #p.ChangeDutyCycle(NOMINAL-MODIFIER)
            #time.sleep(TIME)
            for x in range(CYCLES):
                p.ChangeDutyCycle(NOMINAL-5)
                time.sleep(1)
                p.ChangeDutyCycle(NOMINAL+1)
                time.sleep(0.25)
                p.ChangeDutyCycle(NOMINAL)
                time.sleep(0.25)
        p.ChangeDutyCycle(NOMINAL)
        
    def cleanUp(self):
        GPIO.cleanup()

