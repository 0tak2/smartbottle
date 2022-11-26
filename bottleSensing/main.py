import spidev
import RPi.GPIO as GPIO
import time
import datetime
import requests

#### 초기화 시작 ####
# GPIO 초기화
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

trigPin = 23
echoPin = 24
blueLedPin = 2
redLedPin = 3

GPIO.setup(trigPin, GPIO.OUT)
GPIO.setup(echoPin, GPIO.IN)
GPIO.setup(blueLedPin, GPIO.OUT)
GPIO.setup(redLedPin, GPIO.OUT)

GPIO.output(blueLedPin, GPIO.LOW)
GPIO.output(redLedPin, GPIO.LOW)
GPIO.output(trigPin, GPIO.LOW)


# SPI(-> ADC 연결 인터페이스) 초기화
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1000000
vref = 5.0

# Flask 서버 URL 지정
baseURL = 'http://127.0.0.1:5000'
#### 초기화 끝 ####


def getDistance(trigPin, echoPin):
    GPIO.output(trigPin, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trigPin, GPIO.LOW)

    while GPIO.input(echoPin) == GPIO.LOW:
        start = time.time()

    while GPIO.input(echoPin) == GPIO.HIGH:
        stop = time.time()

    elapsedTime = stop - start
    distance = elapsedTime * 34300 /2
    return distance

def convertDistanceToVolume(distance):
    return -35 * distance + 441

def getAnalogRead(ch):
    buf = [(1<<2)|(1<<1)|(ch&4)>>2,(ch&3)<<6,0]
    buf = spi.xfer(buf)
    adcValue = ((buf[1]&0xF)<<8)|buf[2]
    return adcValue

def convertRawValueToTds(rawValue):
    voltage = rawValue * vref / 1024.0
    tdsValue = (133.42 * voltage * voltage * voltage - 255.86 * voltage * voltage + 857.39 * voltage) * 0.5
    return tdsValue

def sendData(type, time, value):
    data = {
        "time": time,
        "value": value
    }

    url = None
    if type == 'volume':
        url = baseURL + '/api/hydration'
    elif type == 'tds':
        url = baseURL + '/api/tds'
    else:
        raise Exception('잘못된 데이터 타입입니다.')
    
    requests.post(url, json={"key": "value"})

def getLastHydration():
    url = baseURL + '/api/hydration/last'
    response = requests.get(url)
    responseDict = response.json()

    hydratedTimeStr = responseDict['result']['time']
    hydratedTime = datetime.datetime.strptime(hydratedTimeStr, '%Y-%m-%d %H:%M:%S')
    hydratedVolume = responseDict['result']['value_differ'] * -1
    return hydratedTime, hydratedVolume

def getLastTds():
    url = baseURL + '/api/tds?size=1&page=0'
    response = requests.get(url)
    responseDict = response.json()

    tdsValue = responseDict['result'][0]['value_differ'] * -1
    return tdsValue

def main():
    try:
        while True:
            # 센서로부터 값 읽고 서버에 전송
            currentTimeObj = datetime.datetime.now()
            currentTime = currentTimeObj.strftime("%Y-%m-%d %H:%M:%S")

            distance = getDistance(trigPin, echoPin)
            currentVolume = round(convertDistanceToVolume(distance))

            rawValue = getAnalogRead(0)
            currentTds = round(convertRawValueToTds(rawValue))

            print(f'[{currentTime}] 센서로부터 새로운 데이터를 읽어들였습니다.')
            print('현재 물 용량: ', currentVolume, 'ml')
            print('TDS 수치: ', currentTds, 'mg/L(ppm)\n')

            try:
                sendData('volume', currentTime, currentVolume)
                sendData('tds', currentTime, currentTds)
                print('데이터를 서버에 전송하였습니다.\n')
            except Exception as e:
                print('서버에 데이터 전송 중 오류 발생\n', e)
            
            # 서버에서 최근 데이터를 받아와 LED 조작
            hydratedTime, hydratedVolume = getLastHydration()
            elapsedTime = currentTime - hydratedTime
            lastTdsValue = getLastTds()
            print(f'[{currentTime}] 서버로부터 최근 데이터를 가져왔습니다.')
            print(f'마지막 수분 섭취 시간: {hydratedTime}({elapsedTime} 경과)')
            print('마지막 수분 섭취 용량: ', hydratedVolume, 'ml')
            print('최근 TDS 수치: ', lastTdsValue, 'mg/L(ppm)\n')

            if currentTime - hydratedTime > datetime.timedelta(hours=1):
                GPIO.output(blueLedPin, GPIO.HIGH)
                print("수분을 섭취한 시간으로부터 1시간이 넘게 경과하여 파란색 LED를 켰습니다.")
            else:
                print("수분을 섭취한 시간으로부터 1시간 경과하지 않아 파란색 LED는 켜지지 않습니다.")
                GPIO.output(blueLedPin, GPIO.LOW)

            if lastTdsValue > 500:
                GPIO.output(blueLedPin, GPIO.HIGH)
                print("TDS 수치가 500 mg/L를 초과하여 빨간색 LED를 켰습니다.")
            else:
                GPIO.output(blueLedPin, GPIO.LOW)
                print("TDS 수치가 500 mg/L 이하여서 빨간색 LED는 켜지지 않습니다.")
            time.sleep(10)

    except KeyboardInterrupt:
        return 0

if __name__ == '__main__':
    main()
    GPIO.cleanup()
    spi.close()
