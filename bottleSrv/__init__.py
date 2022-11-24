import os
from flask import Flask, render_template
from flask_restful import Resource, Api

# 플라스크 인스턴스를 생성하고 반환
# (터미널에서 flask run 커맨드 사용하여 반환된 인스턴스 실행)
def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'data.sqlite'), # 데이터베이스 경로 지정
    )

    # 앱 인스턴스 패스 없으면 생성
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 데이터베이스 초기화
    from . import db
    db.init_app(app)

    # REST API 라우팅 (flask의 blueprint 기능)
    from .api import hydration
    app.register_blueprint(hydration.api_bp)

    from .api import tds
    app.register_blueprint(tds.api_bp)

    # 인덱스 페이지 라우팅 -> 프론트엔드
    @app.route("/")
    def index():
        return render_template('index.html') # templates/index.html

    return app