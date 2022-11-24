from flask import Blueprint
from flask_restful import Api, Resource, url_for, reqparse
from datetime import datetime
from ..db import get_db
from ..export import tdsDataToExcel

api_bp = Blueprint('tds', __name__, url_prefix='/api/tds')
api = Api(api_bp)

class Tds(Resource): # /api/tds
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
                    "SELECT * FROM tds ORDER BY id DESC LIMIT ? OFFSET ?",
                    (size, offset)
                ).fetchall()
            else:
                start_time_obj = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                end_time_obj = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
                start_time_str = start_time_obj.strftime('%Y-%m-%d %H:%M:%S')
                end_time_str = end_time_obj.strftime('%Y-%m-%d %H:%M:%S')
                raw_data = cursor.execute(
                    "SELECT * FROM tds WHERE created BETWEEN ? AND ? ORDER BY id DESC LIMIT ? OFFSET ?",
                    (start_time_str, end_time_str, size, offset)
                ).fetchall()

            tds_data = list(map(lambda x: {
                'type': 'tds',
                'id': x[0],
                'created': x[1],
                'value_tds': x[2]
            }, raw_data))
        except Exception as e:
            print(e)
            error = e

        if error == None:
            if export == None:
                return {
                    'success': True,
                    'result': tds_data
                }, 200
            else:
                url = tdsDataToExcel(raw_data)
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
                    'type': 'tds',
                    'time': time,
                    'value': value
                },
                'error': str(error)
            }, 400
        time_str = time_obj.strftime("%Y-%m-%d %H:%M:%S")

        print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] New TDS data (time="{time_str}" value={value})')

        # 데이터베이스에 값 추가 인서트
        db = get_db()
        error = None
        try:
            db.execute(
                "INSERT INTO tds (created, tds) VALUES (?, ?)",
                (time_str, int(value)),
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

api.add_resource(Tds, '')