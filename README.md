# Sentry Coupon Monitoring Demo

This small Python project demonstrates how Sentry exposes a hidden timezone
pattern in existing coupon validation. The monitored version intentionally
does not fix the validation logic.

The demo runs six coupon attempts. All three Thailand attempts succeed. Of the
three Malaysia attempts, one succeeds and two are incorrectly rejected because
the validation compares local clock values. The monitored run sends those two
rejections to Sentry.

## Run the demonstration

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Show the SQLite coupon records:

```bash
python demo.py coupons
```

Run the existing validation without monitoring:

```bash
python demo.py old
```

Run the same validation with Sentry monitoring:

```bash
python demo.py new
```

The monitored run sends a warning named `Coupon validation failed` to Sentry.
Open the Sentry **Issues** page to inspect its tags and `coupon_check` context.
