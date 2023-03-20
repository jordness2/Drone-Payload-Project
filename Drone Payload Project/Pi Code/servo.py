import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT, initial=False)
p = GPIO.PWM(4,50)

# speed% = (<time_ns>-1.5)*100
# speed setting: <time_ns>/((1/50)*1000*1000)*100
# min value: 2 = Reverse/Up (max speed) -> 6.5
# max value: 12 = Forward/Down (max speed) -> 7.5
NOMINAL=7 # the 'zero' PWM %age
RANGE=5   # maximum variation above/below NOMINAL

p.start(7)

print("start")
p.ChangeDutyCycle(10)
time.sleep(5)

print("done")
p.ChangeDutyCycle(NOMINAL)
time.sleep(0.1)
GPIO.cleanup()