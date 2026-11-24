"""Small local implementation of the Incubyte SkyPoints assessment."""
from datetime import date, datetime
from pathlib import Path
import json
import re
import pandas as pd

FILES = {"IND": "IND.xlsx", "USA": "USA.xlsx", "AUS": "AUS.xlsx"}

# Source workbook header -> common target field
COLUMN_MAP = {
    "ID": "member_id", "Unique ID": "member_id",
    "Name": "member_name", "Member Name": "member_name",
    "DOB": "dob", "Date of Birth": "dob",
    "TierCode": "tier_code", "Tier Type": "tier_code",
    "EnrollmentDate": "enrollment_date", "Date of Enrollment": "enrollment_date",
    "Flight Date": "last_flight_date", "FlightDate": "last_flight_date",
    "Date of Flight": "last_flight_date",
    "Individual or Corporate": "member_type",
}

def parse_date(value):
    """Parse Excel dates, ISO dates and USA MDDYYYY/MMDDYYYY strings."""
    if pd.isna(value) or str(value).strip() == "":
        return None
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.date()
    raw = str(value).strip()
    if re.fullmatch(r"\d{7,8}", raw):
        try:
            return datetime.strptime(raw.zfill(8), "%m%d%Y").date()
        except ValueError:
            return None
    parsed = pd.to_datetime(raw, errors="coerce")
    return None if pd.isna(parsed) else parsed.date()

def read_country_file(path, country):
    raw = pd.read_excel(path, dtype=object)
    rows = pd.DataFrame()
    for source_col, target_col in COLUMN_MAP.items():
        if source_col in raw.columns and target_col not in rows.columns:
            rows[target_col] = raw[source_col]
    for col in ["member_id", "member_name", "tier_code", "member_type"]:
        if col not in rows:
            rows[col] = None
        rows[col] = rows[col].map(lambda x: None if pd.isna(x) else str(x).strip())
    for col in ["dob", "enrollment_date", "last_flight_date"]:
        if col not in rows:
            rows[col] = None
        rows[col] = rows[col].map(parse_date)
    rows["country_code"] = country
    rows["source_file"] = Path(path).name
    return rows

def age_on(dob, today):
    if dob is None or dob > today:
        return None
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def process_profiles(data_dir="data", output_dir="output", today=None):
    today = today or date.today()
    data_dir, output_dir = Path(data_dir), Path(output_dir)
    frames = [read_country_file(data_dir / file, country) for country, file in FILES.items()]
    members = pd.concat(frames, ignore_index=True)
    errors = []
    for _, row in members.iterrows():
        issue = []
        for field in ["member_id", "member_name", "enrollment_date"]:
            if row[field] is None or pd.isna(row[field]) or str(row[field]).strip() == "":
                issue.append("MISSING_" + field.upper())
        if row["enrollment_date"] and row["enrollment_date"] > today:
            issue.append("ENROLLMENT_DATE_IN_FUTURE")
        if row["dob"] and row["dob"] > today:
            issue.append("DOB_IN_FUTURE")
        if row["last_flight_date"] and row["last_flight_date"] > today:
            issue.append("FLIGHT_DATE_IN_FUTURE")
        if row["dob"] and row["enrollment_date"] and row["dob"] > row["enrollment_date"]:
            issue.append("DOB_AFTER_ENROLLMENT")
        errors.append(issue)
    members["validation_errors"] = errors
    members["age"] = members["dob"].map(lambda x: age_on(x, today))
    members["stale_member"] = members["last_flight_date"].map(
        lambda x: None if x is None else (today - x).days > 90
    )
    # The supplied sample IDs repeat in each country, so the safe sample key is country + ID.
    dup = members.duplicated(["country_code", "member_id"], keep=False) & members["member_id"].notna()
    members.loc[dup, "validation_errors"] = members.loc[dup, "validation_errors"].map(
        lambda x: x + ["DUPLICATE_MEMBER_ID_IN_COUNTRY"]
    )
    rejected = members[members["validation_errors"].map(bool)].copy()
    valid = members[~members["validation_errors"].map(bool)].copy()

    # Keep one current record per member within its country for these sample files.
    valid = valid.drop_duplicates(["country_code", "member_id"], keep="last")

    output_dir.mkdir(parents=True, exist_ok=True)
    valid.to_csv(output_dir / "staging_members.csv", index=False)
    rejected.to_csv(output_dir / "rejected_members.csv", index=False)
    for country, table_name in [("IND", "members_india.csv"), ("USA", "members_usa.csv"), ("AUS", "members_australia.csv")]:
        valid[valid.country_code == country].to_csv(output_dir / table_name, index=False)
    return valid, rejected

def flatten_redemptions(input_file="data/redemptions.json", output_file="output/redemptions.csv"):
    payload = json.loads(Path(input_file).read_text(encoding="utf-8"))
    batches = payload if isinstance(payload, list) else [payload]
    rows = []
    for batch in batches:
        for item in batch.get("redemptions", []):
            rows.append({
                "member_id": str(batch["member_id"]),
                "feed_date": parse_date(batch.get("feed_date")),
                "txn_id": item["txn_id"],
                "txn_date": parse_date(item.get("txn_date")),
                "partner": item.get("partner"),
                "miles_redeemed": int(item["miles_redeemed"]),
                "status": item.get("status"),
            })
    result = pd.DataFrame(rows).drop_duplicates(["txn_id"], keep="last")
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_file, index=False)
    return result

if __name__ == "__main__":
    valid, rejected = process_profiles(today=date(2026, 11, 24))
    redemptions = flatten_redemptions()
    print(f"Valid members: {len(valid)}")
    print(f"Rejected members: {len(rejected)}")
    print(f"Redemption transactions: {len(redemptions)}")
    print("CSV output created in ./output")
