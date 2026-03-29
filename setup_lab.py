# Samuvel A | 727823TUCY040
# student_name: Samuvel A
# roll_number: 727823TUCY040
# project_name: File Integrity Monitor
# date: 2026-03-29

import subprocess
import sys
import os
import datetime
import sqlite3

ROLL_NUMBER = "727823TUCY040"
STUDENT_NAME = "Samuvel A"
DB_FILE = "fim_727823TUCY040.db"
LOG_FILE = "setup_log_727823TUCY040.log"


def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def print_header():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("=" * 65)
    print(f"  SETUP LAB — File Integrity Monitor")
    print(f"  Roll Number : {ROLL_NUMBER}")
    print(f"  Timestamp   : {timestamp}")
    print(f"  Student     : {STUDENT_NAME}")
    print("=" * 65)


def verify_python_version():
    version = sys.version_info
    log(f"Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        log("  ✗ Python 3.8+ is required.")
        sys.exit(1)
    log("  ✓ Python version OK")


def install_dependencies():
    log("Checking required packages (File Integrity Monitor uses stdlib only)...")
    stdlib_modules = ["hashlib", "sqlite3", "json", "os", "sys", "datetime", "time"]
    for mod in stdlib_modules:
        try:
            __import__(mod)
            log(f"  ✓ {mod} — OK")
        except ImportError as e:
            log(f"  ✗ {mod} — MISSING: {e}")
            sys.exit(1)


def setup_database():
    log("Initializing SQLite database for FIM...")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS baseline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filepath TEXT NOT NULL UNIQUE,
            sha256 TEXT,
            md5 TEXT,
            size INTEGER,
            permissions TEXT,
            modified TEXT,
            recorded_at TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filepath TEXT NOT NULL,
            change_type TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            detected_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    log(f"  ✓ Database initialized: {DB_FILE}")


def setup_monitor_directory():
    log("Setting up test directory structure...")
    dirs = ["test_files_727823TUCY040", "logs_727823TUCY040"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        log(f"  ✓ Directory ready: {d}/")


def check_project_structure():
    log("Checking project folder structure...")
    required_files = [
        "tool_main.py",
        "setup_lab.py",
        "run_tool.py",
        "analyze_results.py",
        "requirements.txt",
        "pipeline_727823TUCY040.yml",
    ]
    for f in required_files:
        exists = os.path.isfile(f)
        status = "✓" if exists else "✗ MISSING"
        log(f"  {status} — {f}")


if __name__ == "__main__":
    print_header()
    log(f"Roll Number: {ROLL_NUMBER} | setup_lab.py started")

    verify_python_version()
    install_dependencies()
    setup_database()
    setup_monitor_directory()
    check_project_structure()

    log(f"Roll Number: {ROLL_NUMBER} | Lab setup completed successfully.")
    print("=" * 65)
    print(f"  Setup log saved to: {LOG_FILE}")
    print("=" * 65)
