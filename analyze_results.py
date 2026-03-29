# Samuvel A | 727823TUCY040
# student_name: Samuvel A
# roll_number: 727823TUCY040
# project_name: File Integrity Monitor
# date: 2026-03-29

import json
import os
import datetime
import sys
import sqlite3

ROLL_NUMBER = "727823TUCY040"
STUDENT_NAME = "Samuvel A"
RESULTS_FILE = "results_727823TUCY040.json"
DB_FILE = "fim_727823TUCY040.db"
ANALYSIS_LOG = "analysis_log_727823TUCY040.log"
REPORT_FILE = "analysis_report_727823TUCY040.txt"


def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(ANALYSIS_LOG, "a") as f:
        f.write(line + "\n")


def print_header():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("=" * 65)
    print(f"  ANALYZE RESULTS — File Integrity Monitor")
    print(f"  Roll Number : {ROLL_NUMBER}")
    print(f"  Timestamp   : {timestamp}")
    print(f"  Student     : {STUDENT_NAME}")
    print("=" * 65)


def load_results():
    if not os.path.isfile(RESULTS_FILE):
        log(f"ERROR: '{RESULTS_FILE}' not found. Run run_tool.py first.")
        sys.exit(1)
    with open(RESULTS_FILE) as f:
        data = json.load(f)
    log(f"Loaded {len(data)} test result(s) from {RESULTS_FILE}")
    return data


def load_alerts():
    if not os.path.isfile(DB_FILE):
        return []
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT filepath, change_type, old_value, new_value, detected_at FROM alerts ORDER BY detected_at")
    rows = c.fetchall()
    conn.close()
    return rows


def print_table(results):
    separator = "-" * 92
    header = f"{'Test ID':<8} {'Description':<48} {'Status':<6} {'Timestamp'}"
    print(separator)
    print(header)
    print(separator)
    lines = [separator, header, separator]
    for r in results:
        row = f"{r['test_id']:<8} {r['description'][:47]:<48} {r['status']:<6} {r['timestamp']}"
        print(row)
        lines.append(row)
    print(separator)
    lines.append(separator)
    return lines


def print_alerts_table(alerts):
    if not alerts:
        log("No alerts recorded in database.")
        return []
    separator = "-" * 90
    header = f"{'Filepath':<30} {'Change Type':<22} {'Detected At'}"
    print(separator)
    print("ALERTS RECORDED:")
    print(header)
    print(separator)
    lines = [separator, "ALERTS RECORDED:", header, separator]
    for a in alerts:
        filepath, change_type, old_val, new_val, detected_at = a
        row = f"{os.path.basename(filepath):<30} {change_type:<22} {detected_at}"
        print(row)
        lines.append(row)
    print(separator)
    lines.append(separator)
    return lines


def analyze(results):
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = total - passed
    pass_rate = (passed / total * 100) if total > 0 else 0
    log(f"Total Test Cases : {total}")
    log(f"Passed           : {passed}")
    log(f"Failed           : {failed}")
    log(f"Pass Rate        : {pass_rate:.1f}%")
    return total, passed, failed, pass_rate


def save_report(results, table_lines, alert_lines, total, passed, failed, pass_rate):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(REPORT_FILE, "w") as f:
        f.write("=" * 65 + "\n")
        f.write(f"  Analysis Report — File Integrity Monitor\n")
        f.write(f"  Student     : {STUDENT_NAME}\n")
        f.write(f"  Roll Number : {ROLL_NUMBER}\n")
        f.write(f"  Generated   : {timestamp}\n")
        f.write("=" * 65 + "\n\n")
        f.write("TEST RESULTS TABLE\n")
        f.write("\n".join(table_lines) + "\n\n")
        f.write("ALERTS TABLE\n")
        f.write("\n".join(alert_lines) + "\n\n")
        f.write("SUMMARY\n")
        f.write(f"  Total      : {total}\n")
        f.write(f"  Passed     : {passed}\n")
        f.write(f"  Failed     : {failed}\n")
        f.write(f"  Pass Rate  : {pass_rate:.1f}%\n\n")
        f.write("FINDINGS\n")
        f.write("  - SHA-256 hash changes reliably detect any content modification.\n")
        f.write("  - File deletion is correctly identified when hash returns None.\n")
        f.write("  - Multi-algorithm verification (SHA256, MD5, SHA1) confirms integrity.\n")
        f.write("  - Baseline export to JSON enables offline audit and comparison.\n")
        f.write("  - All alerts are stored in SQLite for forensic review.\n")
    log(f"Report saved to {REPORT_FILE}")


if __name__ == "__main__":
    print_header()
    log(f"Roll Number: {ROLL_NUMBER} | analyze_results.py started")

    results = load_results()
    alerts = load_alerts()

    print()
    log("=== TEST RESULTS TABLE ===")
    table_lines = print_table(results)

    print()
    log("=== ALERTS TABLE ===")
    alert_lines = print_alerts_table(alerts)

    print()
    total, passed, failed, pass_rate = analyze(results)

    save_report(results, table_lines, alert_lines, total, passed, failed, pass_rate)

    log(f"Roll Number: {ROLL_NUMBER} | Analysis complete. Pass rate: {pass_rate:.1f}%")
    print("=" * 65)
    print(f"  Report saved to: {REPORT_FILE}")
    print("=" * 65)
