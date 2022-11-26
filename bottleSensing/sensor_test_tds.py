import spidev
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1000000

vref = 5.0

def analogRead(ch):
        buf = [(1<<2)|(1<<1)|(ch&4)>>2,(ch&3)<<6,0]
        buf = spi.xfer(buf)
        adcValue = ((buf[1]&0xF)<<8)|buf[2]
        return adcValue

def convertRawValueToTds(rawValue):
        voltage = rawValue * vref / 1024.0
        tdsValue = (133.42 * voltage * voltage * voltage - 255.86 * voltage * voltage + 857.39 * voltage) * 0.5
        return tdsValue


try:
        while 1:
                rawValue = analogRead(0)
                tdsValue = convertRawValueToTds(rawValue)

                print(tdsValue, 'ppm (mg/L)')
                time.sleep(1)


except KeyboardInterrupt:
        pass

GPIO.cleanup()
spi.close()
