"""price_logic.order_total 의 경계값 버그를 드러내는 실패 테스트입니다.

사양은 '수량 10개 이상이면 개당 100원 할인'입니다. 따라서 정확히 10개일 때
총액은 10 * 900 = 9000 이어야 합니다. 그러나 현재 코드는 `> 10`(초과)으로
비교해 10개를 할인에서 제외하므로 10000을 돌려줍니다 -> 이 테스트가 실패합니다.

수리 루프에서 order_total 의 비교를 `>= 10` 으로 고치면 초록불이 됩니다.
"""

from app.price_logic import order_total


def test_bulk_discount_applies_at_exactly_ten():
    assert order_total(10) == 9000
