import spidev
import RPi.GPIO as GPIO
import time
import datetime
import requests

#### 초기화 시작 ####
# 루프 딜레이 시간
interval = 15

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

print('### GPIO 및 SPI 초기화 완료 ###')
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
    distance = elapsedTime * 34300 / 2
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
    
    requests.post(url, json=data)

def getLastHydration():
    url = baseURL + '/api/hydration/last'
    response = requests.get(url)
    responseDict = response.json()

    hydratedTimeStr = responseDict['result']['created']
    hydratedTime = datetime.datetime.strptime(hydratedTimeStr, '%Y-%m-%d %H:%M:%S')
    hydratedVolume = responseDict['result']['value_differ'] * -1
    return hydratedTime, hydratedVolume

def getLastTds():
    url = baseURL + '/api/tds?size=1&page=0'
    response = requests.get(url)
    responseDict = response.json()

    tdsValue = responseDict['result'][0]['value_tds']
    return tdsValue

def log(msg, color='orginal'):
    COLORS = {
        'black': 30,
        'red': 31,
        'green': 32,
        'yellow': 33,
        'blue': 34,
        'magenta': 32,
        'cyan': 96,
        'white': 34,
        'orginal': 0
    }

    print(f'\033[{COLORS[color]}m' + msg + '\033[0m')

def main():
    try:
        while True:
            # 작업 시작 시간 기록
            currentTimeObj = datetime.datetime.now()
            currentTime = currentTimeObj.strftime("%Y-%m-%d %H:%M:%S")
            
            log('\n──────────────────────────────────────────────────')
            log(f'[{currentTime}] 새로운 작업이 시작되었습니다.', color='green')

            # 센서로부터 값 읽고 서버에 전송
            distance = getDistance(trigPin, echoPin)
            currentVolume = round(convertDistanceToVolume(distance))

            rawValue = getAnalogRead(0)
            currentTds = round(convertRawValueToTds(rawValue))

            log('# 센서로부터 새로운 데이터를 읽어들였습니다.', color='yellow')
            log(f'* 현재 물 용량: {currentVolume}ml ', color='cyan')
            log(f'* TDS 수치: {currentTds} mg/L(ppm)\n', color='cyan')

            try:
                sendData('volume', currentTime, currentVolume)
                sendData('tds', currentTime, currentTds)
                log('# 데이터를 서버에 전송하였습니다.\n', color='yellow')
            except Exception as e:
                log('# 서버에 데이터 전송 중 오류 발생\n' + str(e), color='magenta')
            
            # 서버에서 최근 데이터를 받아와 LED 조작
            hydratedTime, hydratedVolume = getLastHydration()
            elapsedTime = currentTimeObj - hydratedTime
            lastTdsValue = getLastTds()
            log('# 서버로부터 최근 데이터를 가져왔습니다.', color='yellow')
            log(f'* 마지막 수분 섭취 시간: {hydratedTime}\n\t\t\t({elapsedTime} 경과)', color='cyan')
            log(f'* 마지막 수분 섭취 용량: {hydratedVolume} ml', color='cyan')
            log(f'* 최근 TDS 수치: {lastTdsValue} mg/L(ppm)', color='cyan')
            log('* LED 상태: ', color='cyan')
            if elapsedTime > datetime.timedelta(hours=1):
                GPIO.output(blueLedPin, GPIO.HIGH)
                log("\t<BLUE LED ON> 수분을 섭취한 시간으로부터 1시간 이상 경과", color='blue')
            else:
                log("\t<BLUE LED OFF> 수분을 섭취한 시간으로부터 1시간 이내")
                GPIO.output(blueLedPin, GPIO.LOW)

            if lastTdsValue > 1000:
                GPIO.output(redLedPin, GPIO.HIGH)
                log("\t<RED  LED ON> TDS 수치가 1000mg/L 초과", color='red')
            else:
                GPIO.output(redLedPin, GPIO.LOW)
                log("\t<RED  LED OFF> TDS 수치가 1000mg/L 이하")
            
            log('──────────────────────────────────────────────────\n')
            time.sleep(interval)

    except KeyboardInterrupt:
        return 0

if __name__ == '__main__':
    main()
    GPIO.cleanup()
    spi.close()
