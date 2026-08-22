"""문자열 조립 SQL(Ruff S608)이 잡는 '대조군' 파일입니다.

f-string 조립 지점에 SQL 키워드 리터럴이
그대로 박혀 있어 패턴 매칭이 발화합니다.
sqli_taint_only.py와 나란히 두면 차이가 드러납니다.
타입 주석이 없어 mypy는 조용합니다.
"""


def find_user(cur, name):
    cur.execute("SELECT * FROM users WHERE name = ?", (name,))
