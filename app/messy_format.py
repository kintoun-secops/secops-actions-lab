"""포매터(ruff format)만 잡는 파일입니다.

린트(E/F/I/UP/B/SIM/S)도 타입도 깨끗한데, 문자열이 홑따옴표라
`ruff format`의 기본 스타일(겹따옴표)과 어긋납니다. `ruff check`는
따옴표 스타일을 보지 않아 조용하고, 포매터만 이 파일을 잡습니다.

포매터의 역할은 결함 검출이 아니라 스타일 통일입니다. 스타일이
한 가지로 고정되면 diff에 로직 변경만 남아 리뷰와 이력 추적이
깔끔해집니다. 수리 루프에서는 `ruff format app/` 한 번이면 정리됩니다.
"""


def build_label(name: str, count: int) -> str:
    unit = "items" if count != 1 else "item"
    return f"{name}: {count} {unit}"
