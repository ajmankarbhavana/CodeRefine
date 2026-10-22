from flask import Flask, render_template, request, send_file
from pathlib import Path
from tempfile import NamedTemporaryFile
import ast
import io
import os
import re
import subprocess
import sys
from datetime import datetime

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB upload limit

MAX_SOURCE_CHARS = 100_000


def run_tool(command, source_path):
    """Run an optional static-analysis tool and return its text output."""
    try:
        result = subprocess.run(
            command + [str(source_path)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return (result.stdout + result.stderr).strip()
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return f"Tool unavailable or timed out: {exc}"


def review_source(filename, source):
    findings = []
    score = 100
    lines = source.splitlines()

    # Syntax check
    try:
        ast.parse(source)
        syntax_ok = True
    except SyntaxError as exc:
        syntax_ok = False
        findings.append({
            "tool": "Python syntax",
            "code": "SyntaxError",
            "message": exc.msg,
            "line": exc.lineno or 1,
            "severity": "High",
        })
        score -= 30

    # Basic TODO and common secret-pattern checks
    todo_lines = []
    secret_lines = []
    secret_pattern = re.compile(
        r"""(?i)(password|api[_-]?key|secret|token)\s*=\s*['"][^'"]{3,}['"]"""
    )
    for number, line in enumerate(lines, start=1):
        if "TODO" in line or "FIXME" in line:
            todo_lines.append(number)
        if secret_pattern.search(line):
            secret_lines.append(number)
            findings.append({
                "tool": "Secret pattern check",
                "code": "Possible hardcoded secret",
                "message": "Possible hardcoded password, token, or key. Check whether this value is sensitive.",
                "line": number,
                "severity": "Medium",
            })
            score -= 5

    # Ruff and Bandit are optional tools installed from requirements.txt
    with NamedTemporaryFile("w", suffix=".py", encoding="utf-8", delete=False) as handle:
        handle.write(source)
        temp_path = Path(handle.name)

    try:
        ruff_output = run_tool([sys.executable, "-m", "ruff", "check", "--output-format", "concise"], temp_path)
        bandit_output = run_tool([sys.executable, "-m", "bandit", "-q", "-f", "txt"], temp_path)

        if ruff_output and "All checks passed" not in ruff_output and "Tool unavailable" not in ruff_output:
            for row in ruff_output.splitlines():
                match = re.search(r":(\d+):\d+:\s*([A-Z]\d+)\s+(.+)", row)
                if match:
                    findings.append({
                        "tool": "Ruff",
                        "code": match.group(2),
                        "message": match.group(3),
                        "line": int(match.group(1)),
                        "severity": "Low",
                    })
                    score -= 2

        if bandit_output and "Tool unavailable" not in bandit_output and "No issues identified" not in bandit_output:
            for row in bandit_output.splitlines():
                match = re.search(r"\[([A-Z]\d+):([^\]]+)\]\s*(.*?)(?:\s+at\s+.*?:(\d+))?$", row)
                if match:
                    line_no = int(match.group(4) or 1)
                    findings.append({
                        "tool": "Bandit",
                        "code": f"{match.group(1)}: {match.group(2)}",
                        "message": match.group(3).strip() or "Potential security concern detected.",
                        "line": line_no,
                        "severity": "Low",
                    })
                    score -= 3
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass

    score = max(0, min(100, score))
    # Remove exact duplicate entries while preserving order.
    unique_findings = []
    seen = set()
    for item in findings:
        key = (item["tool"], item["code"], item["message"], item["line"])
        if key not in seen:
            seen.add(key)
            unique_findings.append(item)

    return {
        "filename": filename,
        "score": score,
        "lines_of_code": sum(1 for line in lines if line.strip()),
        "findings": unique_findings,
        "syntax_ok": syntax_ok,
        "todo_lines": todo_lines,
        "secret_lines": secret_lines,
        "source": source,
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


@app.route("/", methods=["GET", "POST"])
def index():
    report = None
    error = None
    if request.method == "POST":
        uploaded = request.files.get("code_file")
        if not uploaded or not uploaded.filename:
            error = "Please choose a Python (.py) file to review."
        elif not uploaded.filename.lower().endswith(".py"):
            error = "Please upload a Python (.py) file."
        else:
            try:
                source = uploaded.read().decode("utf-8")
                if len(source) > MAX_SOURCE_CHARS:
                    error = "The file is too large. Please upload a file under 100 KB of text."
                else:
                    report = review_source(Path(uploaded.filename).name, source)
                    # Keep the most recent report in this process for the download route.
                    app.config["LAST_REPORT"] = report
            except UnicodeDecodeError:
                error = "The file must be a UTF-8 encoded Python file."
    return render_template("index.html", report=report, error=error)


@app.route("/download-report")
def download_report():
    report = app.config.get("LAST_REPORT")
    if not report:
        return "Please review a Python file first.", 400

    lines = [
        "CodeRefine - AI Code Reviewer & Refactor Assistant",
        f"File: {report['filename']}",
        f"Generated: {report['generated']}",
        f"Indicative score: {report['score']}/100",
        f"Distinct findings: {len(report['findings'])}",
        "",
        "Findings:",
    ]
    if not report["findings"]:
        lines.append("- No findings detected by the configured checks.")
    for finding in report["findings"]:
        lines.append(
            f"- [{finding['severity']}] {finding['tool']} - {finding['code']} "
            f"(Line {finding['line']}): {finding['message']}"
        )
    lines += [
        "",
        "Note: This is a static-analysis report, not a guarantee that code is correct or secure.",
    ]
    data = "\n".join(lines).encode("utf-8")
    return send_file(
        io.BytesIO(data),
        mimetype="text/plain",
        as_attachment=True,
        download_name="coderefine-review-report.txt",
    )


if __name__ == "__main__":
    app.run(debug=False)
