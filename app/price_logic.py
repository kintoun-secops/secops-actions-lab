"""pytest가 잡는 파일입니다.

타입도 맞고(mypy clean) 보안 패턴도 없어(Ruff clean)
다른 도구는 전부 통과합니다. '동작'에만 경계값 버그가
하나 있고, tests/test_price_logic.py가 그것을 드러냅니다.
아래 docstring의 사양과 코드가 어긋난 지점이 버그입니다.
"""


def order_total(quantity: int, unit_price: int = 1000) -> int:
    """수량에 따른 주문 총액을 계산합니다.

    사양: 수량이 10개 '이상'이면 대량 구매로 보고
          개당 100원을 깎아 줍니다. 미만이면 기본
          단가(unit_price)를 그대로 씁니다.
    """
    if quantity >= 10:
        unit_price = unit_price - 100
    return quantity * unit_price
