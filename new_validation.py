import sentry_sdk

from old_validation import validate_coupon


def apply_coupon(coupon, local_time, request):
    result = validate_coupon(coupon, local_time)

    if not result["valid"]:
        sentry_sdk.set_tag("server_region", request.region)
        sentry_sdk.set_tag("environment", "testing")

        sentry_sdk.set_context(
            "coupon_check",
            {
                "coupon_code": coupon.code,
                "current_time": str(local_time),
                "expires_at": str(coupon.expiry_datetime),
                "validation_reason": result["reason"],
            },
        )

        sentry_sdk.capture_message(
            "Coupon validation failed",
            level="warning",
        )

    return result
