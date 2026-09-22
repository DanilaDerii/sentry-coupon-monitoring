from datetime import datetime

import sentry_sdk

from coupon import Coupon, Request
from new_validation import apply_coupon


def test_new_validation_rejects_coupon_and_reports_it(monkeypatch):
    coupon = Coupon("THAI20", 20, datetime(2026, 9, 22, 17, 0))
    request = Request(region="Malaysia")
    captured_messages = []
    monkeypatch.setattr(sentry_sdk, "set_tag", lambda *args: None)
    monkeypatch.setattr(sentry_sdk, "set_context", lambda *args: None)
    monkeypatch.setattr(
        sentry_sdk,
        "capture_message",
        lambda message, level: captured_messages.append((message, level)),
    )

    result = apply_coupon(coupon, datetime(2026, 9, 22, 17, 30), request)

    assert result == {"valid": False, "reason": "expired"}
    assert captured_messages == [("Coupon validation failed", "warning")]
