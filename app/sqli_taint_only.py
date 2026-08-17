"""Semgrep 커스텀 taint 규칙만 잡는 '센터피스'입니다.

사용자 입력이 문자열 조립을 거쳐 execute까지
흐르지만, SQL 키워드 리터럴이 '조립 지점'에
없어 문자열 조립 SQL(Ruff S608)은 이 파일을 놓칩니다.
  - prefix는 보간 없는 순수 리터럴 대입이라
    S608이 검사하지 않습니다.
  - prefix + q + "%'"의 유일한 리터럴은 "%'"라
    SQL 키워드가 없어 매칭에 실패합니다.
이 흐름은 데이터 흐름을 추적하는 Semgrep taint(lab-taint-sql-concat)가 잡습니다.
타입 주석이 없어 mypy도 조용합니다.
자세한 설명은 README의 "패턴 매칭과 taint 분석의 검출 범위 차이" 절에 있습니다.
"""

import flask
from flask import request

app = flask.Flask(__name__)


def search(cur):
    q = request.args.get("q")
    prefix = "SELECT * FROM users WHERE name LIKE '%"
    query = prefix + q + "%'"
    cur.execute(query)
