def validate_coupon(coupon, local_time):
    expiry_time = coupon.expiry_datetime

    if local_time >= expiry_time:
        return {"valid": False, "reason": "expired"}

    return {"valid": True, "reason": "accepted"}
