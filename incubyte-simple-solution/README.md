# Incubyte Data Engineer Assessment - Minimal Working Solution

This is a small Python solution that runs locally without a Snowflake account. It reads the three supplied Excel workbooks, standardizes their different column names, validates records, derives age/stale-member fields, splits accepted records by country, and flattens the example redemption JSON.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m src.process
```

Expected result for the supplied files using assessment date 2026-11-24:
- 8 accepted member rows
- 1 rejected member row (AUS enrollment date `2021-13-13`)
- 2 flattened redemption transactions

Output is written to `output/`.

Run tests:

```bash
pytest -v
```

## Why no Snowflake account is needed

The assessment asks for Snowflake DDL and transformation logic, not proof that the candidate owns a Snowflake subscription. The Python program demonstrates the data processing locally and creates CSV outputs. `sql/snowflake.sql` contains the Snowflake table definitions and representative SQL for derived columns, country splitting, latest-row selection and JSON flattening. In an interview, explain that the SQL is ready to execute in a Snowflake environment, but live execution was not possible because no account was supplied.

Do not claim that Snowflake SQL was executed. Show the local Python run and tests instead.

## Source-data observations

- IND uses `ID`, `Name`, `DOB`, `TierCode`, `EnrollmentDate`, `Individual or Corporate`, `Flight Date`.
- USA uses `ID`, `Name`, `TierCode`, `EnrollmentDate`, `FlightDate`. DOB is absent. Dates are compact month/day/year strings.
- AUS uses `Unique ID`, `Member Name`, `Tier Type`, `Date of Birth`, `Date of Enrollment`, `Date of Flight`. One enrollment date is invalid (`2021-13-13`) and is rejected because enrollment date is mandatory.
- DOB is optional, so the AUS row with missing DOB is accepted.

## Key assumption to explain

The sample files reuse IDs 1, 2 and 3 in every country and do not contain a source-updated timestamp. We cannot safely tell whether same-numbered IDs across countries are the same member or separate people. The local solution therefore identifies a sample row using country + member ID. For true cross-country movement in production, the source must provide a globally unique member ID and source update timestamp. Then select the latest record per member and update the old and new country tables.

## Submission files

- `src/process.py`: complete local processing.
- `sql/snowflake.sql`: Snowflake DDL and SQL examples.
- `tests/test_process.py`: basic tests.
- `data/`: original three Excel files and sample JSON from the assessment PDF.
