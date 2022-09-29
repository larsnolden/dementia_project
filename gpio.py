import RPi.GPIO as GPIO
import time

# brush teeth
LED_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

def set_light(id, setOn):
    gpio_state = GPIO.LOW if setOn == True else GPIO.LOW
    GPIO.output(id, gpio_state)
    GPIO.cleanup()