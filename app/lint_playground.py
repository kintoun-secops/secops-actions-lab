"""Ruff 린트 규칙을 모아 둔 연습 파일입니다.

보안(S) 패턴은 넣지 않았습니다. 여기서는 아래 '위생' 규칙만 걸립니다.
None 비교(E711), 미사용 import(F401), import 미정렬(I001),
구식 타입 표기(UP006), 폐기된 import(UP035),
가변 기본 인자(B006), 중첩 if(SIM102).
clamp_values는 타입이 정확해 mypy는 조용합니다.
"""


def clamp_values(numbers: list[int]) -> list[int]:
    # 중첩 if는 하나로 합칠 수 있음 (SIM102)
    result: list[int] = []
    for value in numbers:
        if value > 0 and value < 100:
            result.append(value)
    return result


def find_missing(value, items=None):
    # 가변 기본값 (B006) / None 비교 (E711)
    if items is None:
        items = []
    if value is None:
        return items
    items.append(value)
