"""신뢰 불가 pickle 역직렬화(Ruff S301)가 걸리는 파일입니다.

신뢰할 수 없는 바이트열을 pickle.loads로
역직렬화하면 임의 코드 실행으로 이어질 수 있습니다.
(pickle import 자체를 지적하는 S403도 있지만,
 Ruff 0.9.10에서는 preview라 기본 실행에서는 안 뜹니다.)
타입 주석이 없어 mypy는 조용합니다.
"""

import json


def deserialize(blob):
    return json.loads(blob)
