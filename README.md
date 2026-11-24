# Incubyte Data Engineer Technical Assessment

## Overview

This repository contains a Python-based data processing solution and a Snowflake SQL design for the Incubyte Data Engineer technical assessment.

The solution ingests the supplied member workbooks for India, the United States, and Australia, standardizes their differing schemas, applies data-quality checks, derives member attributes, and produces country-specific outputs. It also demonstrates how redemption events in the supplied JSON feed can be flattened into transaction-level records.

## Solution Components

| Component | Description |
|---|---|
| `data/` | Source Excel workbooks and the sample redemption JSON feed |
| `src/process.py` | Python ingestion, schema standardization, validation, derivation, and output generation |
| `sql/snowflake.sql` | Snowflake DDL and representative transformation SQL |
| `tests/test_process.py` | Unit tests for key processing and parsing logic |
| `output/` | Generated CSV outputs from the supplied assessment data |
| `requirements.txt` | Python dependencies |

## Processing Flow

1. **Ingest** the three country workbooks.
2. **Standardize** source-specific column names and date formats into a common member structure.
3. **Validate** mandatory fields and data consistency. Invalid records are separated from accepted records.
4. **Derive** age from date of birth and identify stale members based on the flight date.
5. **Separate** accepted member records into country-specific outputs.
6. **Flatten** the redemption JSON feed into transaction-level records for downstream integration.

## Data Quality and Transformation Rules

- Member ID, member name, and enrollment date are treated as mandatory fields.
- Source date formats are normalized before validation.
- Records with invalid mandatory dates are rejected and written to the rejected-record output.
- Age is derived from date of birth when a valid date of birth is available.
- A member is marked as stale when the number of days since the flight date is greater than 90.
- Redemption events are flattened into individual transaction records using the transaction-level attributes in the JSON feed.

## Running the Solution

### Prerequisites

- Python 3.10 or later
- `pip`

### Setup

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Install dependencies and run the pipeline:

```bash
python -m pip install -r requirements.txt
python -m src.process
```

The generated CSV files are written to the `output/` directory.

### Run Tests

```bash
python -m pytest -v
```

The current test suite contains four tests covering age derivation, compact date parsing, invalid date handling, and redemption JSON flattening.

## Sample Execution Results

Using the supplied assessment workbooks and the assessment run date of **24 November 2026**, the local processing run produced:

| Result | Count |
|---|---:|
| Accepted member records | 8 |
| Rejected member records | 1 |
| Flattened redemption transactions | 2 |

The rejected record contains an invalid enrollment date (`2021-13-13`). Records with a missing date of birth are retained because date of birth is not treated as a mandatory field in this implementation.

## Snowflake Design

The `sql/snowflake.sql` file provides a Snowflake-oriented design covering:

- Raw, staging, and country-specific target table structures
- Derived member attributes
- Country-level member selection
- Latest-record selection using `ROW_NUMBER()`
- Redemption JSON parsing with `LATERAL FLATTEN`
- A join pattern between redemption transactions and member records
- Representative data-quality checks

The SQL is provided as the warehouse implementation design. The Python pipeline and its tests were executed locally; the Snowflake SQL has not been run against a live Snowflake account as part of this submission.

## Design Considerations and Assumptions

### Cross-country member movement

The supplied workbooks reuse member IDs across countries and do not provide a source update timestamp or a globally unique member identifier. Therefore, the sample data does not establish whether records with the same ID in different countries represent the same person or different people.

For the local sample processing, records are identified using the combination of country code and member ID. In a production implementation, reliable latest-record-wins handling for a member moving between countries requires:

- A globally unique member identifier shared across country sources
- A trustworthy source update timestamp or equivalent change sequence
- A deterministic rule to select the latest record for each member
- A controlled process to update the previous and current country assignments

These source attributes are required to implement cross-country movement accurately; they cannot be inferred safely from the supplied sample files.

### Redemption-to-member relationship

The redemption feed contains `member_id` and transaction details. The intended integration is to flatten each redemption event into a transaction record and join it to the member profile using the member identifier. The production join depends on the member identifier being consistent between the feed and the member data.

## Repository Structure

```text
.
├── data/
├── output/
├── sql/
│   └── snowflake.sql
├── src/
│   └── process.py
├── tests/
│   └── test_process.py
├── README.md
└── requirements.txt
```
