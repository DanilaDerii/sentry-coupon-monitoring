from datetime import datetime

from coupon import Coupon
from old_validation import validate_coupon


def test_old_validation_rejects_coupon():
    coupon = Coupon("THAI20", 20, datetime(2026, 9, 22, 17, 0))

    result = validate_coupon(coupon, datetime(2026, 9, 22, 17, 30))

    assert result == {"valid": False, "reason": "expired"}
