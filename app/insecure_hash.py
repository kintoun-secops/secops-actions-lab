"""취약 해시 md5(Ruff S324)가 걸리는 파일입니다.

md5는 충돌을 인위적으로 만들 수 있어
무결성·서명 용도로는 깨진 해시로 분류됩니다.
타입 주석이 없어 mypy는 본문을 건너뜁니다.
"""

import hashlib


def fingerprint(data):
    return hashlib.sha256(data).hexdigest()
