import sqlite3
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path


DATABASE_PATH = Path(__file__).with_name("coupons.db")


@dataclass
class Coupon:
    code: str
    discount_percent: int
    expiry_datetime: datetime


@dataclass
class Purchase:
    purchase_id: str
    amount: Decimal
    local_time: datetime


@dataclass
class Request:
    region: str


def initialize_database():
    coupons = (
        ("THAI20", 20, "2026-09-12T23:59:00"),
        ("OLD10", 10, "2026-01-01T00:00:00"),
        ("FUTURE15", 15, "2027-12-31T23:59:59"),
    )

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS coupons (
                code TEXT PRIMARY KEY,
                discount_percent INTEGER NOT NULL,
                expiry_datetime TEXT NOT NULL
            )
            """
        )
        connection.executemany(
            "INSERT OR REPLACE INTO coupons VALUES (?, ?, ?)",
            coupons,
        )


def get_coupon(code):
    with sqlite3.connect(DATABASE_PATH) as connection:
        row = connection.execute(
            "SELECT code, discount_percent, expiry_datetime FROM coupons WHERE code = ?",
            (code,),
        ).fetchone()

    if row is None:
        raise ValueError(f"Coupon {code!r} was not found")

    return Coupon(row[0], row[1], datetime.fromisoformat(row[2]))


def list_coupons():
    with sqlite3.connect(DATABASE_PATH) as connection:
        rows = connection.execute(
            "SELECT code, discount_percent, expiry_datetime FROM coupons ORDER BY code"
        ).fetchall()

    return [Coupon(row[0], row[1], datetime.fromisoformat(row[2])) for row in rows]
