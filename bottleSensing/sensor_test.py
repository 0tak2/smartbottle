import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

trigPin = 23
echoPin = 24

GPIO.setup(trigPin, GPIO.OUT)
GPIO.setup(echoPin, GPIO.IN)

GPIO.output(trigPin, GPIO.LOW)
print("HC-SR04 OUTPUT INITIALIZED")

try:
    while True:
        GPIO.output(trigPin, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(trigPin, GPIO.LOW)

        while GPIO.input(echoPin) == GPIO.LOW:
            start = time.time()

        while GPIO.input(echoPin) == GPIO.HIGH:
            stop = time.time()

        elapsedTime = stop - start
        distance = elapsedTime * 34300 /2
        print("Distance: %.1f cm" % distance)
        time.sleep(0.4)

except KeyboardInterrupt:
    GPIO.cleanup()

if (__name__ == '__main__'):
    print('hi')
