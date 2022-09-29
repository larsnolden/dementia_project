import RPi.GPIO as GPIO
import time

# brush teeth

def set_light(id, setOn):
    # brush teeth
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(id, GPIO.OUT)

    gpio_state = GPIO.HIGH if setOn == True else GPIO.LOW
    GPIO.output(id, gpio_state)



def test():
    id = 11
    while True:
        set_light(id, True)
        time.sleep(2)
        set_light(id, False)
        time.sleep(2)


