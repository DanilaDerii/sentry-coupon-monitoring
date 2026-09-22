import argparse
import os
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import sentry_sdk
from dotenv import load_dotenv

from coupon import Request, Purchase, get_coupon, initialize_database, list_coupons


ATTEMPTS = (
    ("TH-1", "Thailand", "Asia/Bangkok", "2026-09-12T20:00:00"),
    ("TH-2", "Thailand", "Asia/Bangkok", "2026-09-12T22:00:00"),
    ("TH-3", "Thailand", "Asia/Bangkok", "2026-09-12T23:30:00"),
    ("MY-1", "Malaysia", "Asia/Kuala_Lumpur", "2026-09-12T22:30:00"),
    ("MY-2", "Malaysia", "Asia/Kuala_Lumpur", "2026-09-13T00:15:00"),
    ("MY-3", "Malaysia", "Asia/Kuala_Lumpur", "2026-09-13T00:45:00"),
)


def show_coupons():
    print("CODE       DISCOUNT  EXPIRY")
    for coupon in list_coupons():
        print(f"{coupon.code:<10} {coupon.discount_percent:>3}%      {coupon.expiry_datetime}")


def thailand_time(local_time, timezone):
    return (
        local_time.replace(tzinfo=ZoneInfo(timezone))
        .astimezone(ZoneInfo("Asia/Bangkok"))
        .replace(tzinfo=None)
    )


def configure_sentry():
    load_dotenv()
    dsn = os.getenv("SENTRY_DSN")

    if not dsn:
        raise RuntimeError("SENTRY_DSN is missing from the .env file")

    sentry_sdk.init(
        dsn=dsn,
        environment="testing",
        release="coupon-monitoring@1.0.0",
        attach_stacktrace=True,
        send_default_pii=False,
    )


def run_demo(version):
    coupon = get_coupon("THAI20")

    if version == "old":
        from old_validation import validate_coupon
    else:
        from new_validation import apply_coupon

        configure_sentry()

    print(f"\n{version.upper()} VALIDATION")
    print(f"Coupon {coupon.code} expires at {coupon.expiry_datetime} Thailand time.\n")
    print(
        f"{'ID':<5} {'REGION':<10} {'LOCAL ATTEMPT':<17} "
        f"{'THAILAND TIME':<17} {'EXPECTED':<10} {'ACTUAL':<9} {'SENTRY'}"
    )
    print("-" * 91)

    accepted = 0
    rejected = 0
    sentry_events = 0

    for purchase_id, region, timezone, time_text in ATTEMPTS:
        purchase = Purchase(
            purchase_id=purchase_id,
            amount=Decimal("1000.00"),
            local_time=datetime.fromisoformat(time_text),
        )
        request = Request(region=region)
        time_in_thailand = thailand_time(purchase.local_time, timezone)
        expected = "accepted" if time_in_thailand < coupon.expiry_datetime else "expired"

        if version == "old":
            result = validate_coupon(coupon, purchase.local_time)
            sentry_status = "-"
        else:
            result = apply_coupon(coupon, purchase.local_time, request)
            sentry_status = "sent" if not result["valid"] else "-"
            sentry_events += int(not result["valid"])

        accepted += int(result["valid"])
        rejected += int(not result["valid"])

        print(
            f"{purchase_id:<5} {region:<10} "
            f"{purchase.local_time:%m-%d %H:%M}       "
            f"{time_in_thailand:%m-%d %H:%M}       "
            f"{expected:<10} {result['reason']:<9} {sentry_status}"
        )

    print("-" * 91)
    print(f"Summary: {accepted} accepted, {rejected} rejected", end="")

    if version == "new":
        sentry_sdk.flush(timeout=5)
        print(f", {sentry_events} Sentry warnings sent")
        print(f"Last Sentry event ID: {sentry_sdk.last_event_id()}")
    else:
        print(", no monitoring")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("coupons", "old", "new"))
    args = parser.parse_args()

    initialize_database()

    if args.mode == "coupons":
        show_coupons()
    else:
        run_demo(args.mode)


if __name__ == "__main__":
    main()
