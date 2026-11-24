# Submission walkthrough

## 1. Create a GitHub repository
1. Sign in to GitHub.
2. Click the `+` icon, then `New repository`.
3. Name it `incubyte-data-engineer-assessment`.
4. Choose Public (the recruiter asks for a public repository).
5. Do not initialize with README, because this folder already has one.
6. Create repository and copy its HTTPS URL.

## 2. Upload the project
### Easiest method: GitHub website
1. Extract the ZIP.
2. Open the new GitHub repository.
3. Select `Add file` -> `Upload files`.
4. Drag the contents of the extracted project folder into the browser (not the parent folder itself).
5. Add commit message: `Add initial assessment solution`.
6. Click `Commit changes`.

### Git command method
Run from inside the extracted project folder:
```bash
git init
git add .
git commit -m "Add initial assessment solution"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/incubyte-data-engineer-assessment.git
git push -u origin main
```
Replace the URL with your actual repository URL.

## 3. Run and verify locally
```bash
pip install -r requirements.txt
python -m src.process
pytest -v
```
Check the `output` folder. It should contain staging_members.csv, rejected_members.csv, three country CSVs and redemptions.csv.

## 4. Snowflake limitation
No account is required to run the Python solution. The Snowflake DDL and query examples are in `sql/snowflake.sql`. Explain honestly that you could not execute the SQL in a live Snowflake account, but have supplied the Snowflake implementation and validated the transformation behavior locally.

## 5. Review before submitting
- Open README.md and confirm it explains how to run the code.
- Open `sql/snowflake.sql` and be ready to explain table creation, age, stale flag, country split, deduplication and JSON flattening.
- Confirm no passwords or private credentials are in the repository.
- Confirm the three supplied Excel files are included.
- Confirm tests pass.
- Copy the public repository URL.

## 6. Submit
Open the Google Form from the recruiter email:
https://forms.gle/6SBSgzNT7mnv2LTQ9
Paste the public GitHub repository URL and submit.

## 7. Simple interview explanation
"I used Python to read the three country workbooks because their column names and date formats differ. I standardized them into one member schema, validated mandatory fields and dates, calculated age and whether the last flight was more than 90 days ago, and separated invalid rows into a reject file. I then wrote country-specific CSV outputs. I flattened each redemption in the JSON array into one transaction row and joined it to members by member ID. I included Snowflake DDL and SQL for the database implementation. I could not execute Snowflake SQL because I did not have an account, so I demonstrated the processing locally and ran unit tests."

## Important caveat
The attached workbooks repeat IDs 1, 2 and 3 in each country. They do not contain a global member identifier or source update timestamp. A real country move cannot be reliably inferred from these files. Explain that production latest-record-wins needs a global member ID and source modification timestamp.
