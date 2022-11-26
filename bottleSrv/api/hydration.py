from flask import Blueprint
from flask_restful import Api, Resource, reqparse
from datetime import datetime
from ..db import get_db
from ..export import hydrationDataToExcel

api_bp = Blueprint('hydration', __name__, url_prefix='/api/hydration')
api = Api(api_bp)

class Hydration(Resource): # /api/hydration
    def get(self):
        # 요청 URI에서 page 값 읽기
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=str, required=True, location='args')
        parser.add_argument('size', type=str, required=True, location='args')
        parser.add_argument('start_time', type=str, location='args')
        parser.add_argument('end_time', type=str, location='args')
        parser.add_argument('export', type=bool, location='args')

        args = parser.parse_args()
        page, size, start_time, end_time, export = args.values()

        # 데이터베이스에서 값 읽기
        db = get_db()
        cursor = db.cursor()
        error = None
        try:
            offset = int(page) * int(size)

            if start_time == None or end_time == None:
                raw_data = cursor.execute(
                    "SELECT * FROM hydration ORDER BY id DESC LIMIT ? OFFSET ?",
                    (size, offset)
                ).fetchall()
            else:
                start_time_obj = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                end_time_obj = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
                start_time_str = start_time_obj.strftime('%Y-%m-%d %H:%M:%S')
                end_time_str = end_time_obj.strftime('%Y-%m-%d %H:%M:%S')
                raw_data = cursor.execute(
                    "SELECT * FROM hydration WHERE created BETWEEN ? AND ? ORDER BY id DESC LIMIT ? OFFSET ?",
                    (start_time_str, end_time_str, size, offset)
                ).fetchall()

            hydration_data = list(map(lambda x: {
                'type': 'hydration',
                'id': x[0],
                'created': x[1],
                'value_differ': x[2],
                'value_volume': x[3],
            }, raw_data))
        except Exception as e:
            print(e)
            error = e

        if error == None:
            if export == None:
                return {
                    'success': True,
                    'result': hydration_data
                }, 200
            else:
                url = hydrationDataToExcel(raw_data)
                return {
                    'success': True,
                    'result': {
                        'url': url
                    }
                }
        else:
            return {
                'success': False,
                'error': str(error)
            }, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('time', type=str, required=True, location='json')
        parser.add_argument('value', type=str, required=True, location='json')

        args = parser.parse_args()
        time, value = args.values()

        try:
            time_obj = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            error = '형식에 맞지 않는 시간입니다. 올바른 형태: %Y-%m-%d %H:%M:%S'
            return {
                'success': False,
                'payload': {
                    'type': 'hydration',
                    'time': time,
                    'value': value
                },
                'error': str(error)
            }, 400
        time_str = time_obj.strftime("%Y-%m-%d %H:%M:%S")

        print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] New Volume data (time="{time_str}" value={value})')

        # 우선 데이터베이스에서 이전 볼륨 값을 읽는다
        db = get_db()
        cursor = db.cursor()
        try:
            _, _, _, prev_vol = cursor.execute("SELECT * FROM hydration ORDER BY id DESC").fetchone()
        except Exception as e:
            error = '이전 값을 불러오는 중 오류가 발생했습니다.'
            print(error + str(e))
            return {
                'success': False,
                'payload': {
                    'type': 'hydration',
                    'time': time,
                    'value': value
                },
                'error': str(error)
            }, 500

        # 데이터베이스에 값 추가 인서트
        error = None
        try:
            db.execute(
                "INSERT INTO hydration (created, differ, current_vol) VALUES (?, ?, ?)",
                (time_str, int(value) - prev_vol, int(value)),
            )
            db.commit()
        except Exception as e:
            print(e)
            error = e

        if error == None:
            return {
                'success': True,
                'payload': {
                    'type': 'tds',
                    'time': time,
                    'value': value
                }
            }, 200
        else:
            return {
                'success': False,
                'payload': {
                    'type': 'tds',
                    'time': time,
                    'value': value
                },
                'error': str(error)
            }, 500

class LastHydration(Resource): # /api/hydration/last
    def get(self):
        # 데이터베이스에서 값 읽기
        db = get_db()
        cursor = db.cursor()
        error = None
        try:
            raw_data = cursor.execute(
                "SELECT * FROM hydration WHERE differ < -20 ORDER BY id DESC LIMIT 1",
            ).fetchone()

            hydration_data = {
                'type': 'hydration',
                'id': raw_data[0],
                'created': raw_data[1],
                'value_differ': raw_data[2],
                'value_volume': raw_data[3],
            }
        except Exception as e:
            print(e)
            error = e

        if error == None:
            return {
                'success': True,
                'result': hydration_data
            }, 200
        else:
            return {
                'success': False,
                'error': str(error)
            }, 500

api.add_resource(Hydration, '')
api.add_resource(LastHydration, '/last')