"""mypy만 잡는 유일한 파일입니다(정확히 2건).

  - 반환 타입 오류(return-value): int * float는
    float인데 반환 타입이 int로 선언됨
  - 인자 타입 오류(arg-type): price(int) 자리에
    str "100"을 넘김 (모듈 레벨 호출은 항상 검사됨)
Ruff는 타입을 보지 않아 이 파일에 조용합니다.
"""


def apply_discount(price: int, rate: float) -> float:
    return price * rate


result = apply_discount(100, 0.1)
