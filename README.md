# AI Code Reviewer

A beginner-friendly Flask website that checks uploaded Python source code with static-analysis tools. It **does not execute uploaded programs**.

## Features

- Midnight-purple page (`#100F1D`) and deep-violet panels (`#1B1930`)
- Lavender buttons/headings (`#A78BFA`) and soft-lavender code (`#D8D4F5`)
- `.py` upload validation and 200 KB request limit
- Python syntax checking with `ast`
- Ruff style and quality diagnostics
- Bandit security diagnostics parsed from JSON, so one tool result is not counted once per output line
- TODO-comment detection and a simple hardcoded-secret heuristic
- Distinct finding cards, severity labels, line numbers and illustrative score
- Downloadable text report with tool statuses and findings
- Example clean and intentionally problematic Python files
- Basic automated route/report tests

## Requirements

Python 3.10 or newer is recommended. Install dependencies from `requirements.txt`.

## Run on Windows / PowerShell

1. Extract the ZIP.
2. Open the extracted `ai_code_reviewer_work` folder in VS Code.
3. Choose **Terminal → New Terminal**.
4. Install packages:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Start the website:

   ```powershell
   python app.py
   ```

6. Open http://127.0.0.1:5000 and keep the terminal open while testing.

Stop the server with `Ctrl+C` in the terminal.

## Final verification

### 1. Test the download report

Upload `issue_test.py`, click **Download Review Report**, and open the downloaded `code_review_report.txt`. Confirm it includes the file name, score, check statuses, findings, severity, and line numbers.

### 2. Test clean and problematic files

- Upload `clean_test.py`. Syntax should pass and it should normally produce few or no findings.
- Upload `issue_test.py`. The app should detect the sample hardcoded password and `os.system()` patterns. Ruff may report style issues depending on tool version.

### 3. Run automated tests

From the project folder, run:

```powershell
python -m unittest discover -s tests -v
```

These tests require the packages in `requirements.txt` to be installed first.

## Score explanation

The score is an illustrative demo metric. It starts at 100 and subtracts per-finding penalties (High: 20, Medium: 10, Low: 4, Info: 1), with a minimum of 0. It is not an official quality or security rating.

## Limitations

Static analysis can miss problems and can report false positives. Secret detection is a basic heuristic. A passing report does not prove code is secure. This is a local learning project, not a production security service. Before public deployment, add authentication, CSRF protection, rate limiting, and deployment hardening. Never upload real credentials or confidential code.
