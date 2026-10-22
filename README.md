# CodeRefine

**AI Code Reviewer & Refactor Assistant** — a beginner-friendly Flask app for reviewing Python source code with syntax checks, Ruff style checks, Bandit security checks, and simple TODO/possible-secret pattern detection.

> Important: despite the project title, this version uses static-analysis tools and simple pattern checks. It does not call an AI/LLM or automatically refactor code. Findings are suggestions to inspect, not proof that code is broken or vulnerable.

## Features

- Upload a Python `.py` file (up to 1 MB HTTP upload limit; source text limited to 100 KB).
- Check Python syntax.
- Run Ruff and Bandit when installed.
- Detect TODO/FIXME comments and possible hardcoded secrets.
- Show an indicative score and findings.
- Download a plain-text review report.

## Requirements

- Python 3.10 or newer
- pip

## Run on Windows (PowerShell)

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser. Keep the terminal open while using the site. Stop it with `Ctrl+C`.

## Project structure

```text
CodeRefine/
├── app.py
├── requirements.txt
├── README.md
├── test.py
└── templates/
    └── index.html
```

## Upload to GitHub

Upload the files and the `templates` folder to your repository. Do not upload a virtual environment, passwords, API keys, or private data.

## Limitations

- Static analysis can produce false positives and miss real problems.
- The score is an illustrative heuristic, not a formal security rating.
- The report is not a guarantee that code is correct or secure.
- The app runs uploaded code through static-analysis tools only; it does not execute the uploaded source.
- For public deployment, add authentication, rate limiting, request protections, and production hosting configuration before exposing it to untrusted users.
