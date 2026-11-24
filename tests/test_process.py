from datetime import date
import json
import pandas as pd
from src.process import age_on, parse_date, flatten_redemptions

def test_age():
    assert age_on(date(2000, 12, 1), date(2026, 11, 24)) == 25

def test_compact_usa_date():
    assert parse_date("6152022") == date(2022, 6, 15)

def test_invalid_date_returns_none():
    assert parse_date("2021-13-13") is None

def test_flatten_redemptions(tmp_path):
    source = tmp_path / "feed.json"
    output = tmp_path / "out.csv"
    source.write_text(json.dumps({"member_id":"7","feed_date":"20240115","redemptions":[
        {"txn_id":"R1","txn_date":"20240110","partner":"P","miles_redeemed":100,"status":"COMPLETED"}
    ]}))
    result = flatten_redemptions(str(source), str(output))
    assert len(result) == 1
    assert result.iloc[0]["member_id"] == "7"
