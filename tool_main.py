# student_name: Samuvel A
# roll_number: 727823TUCY040
# project_name: File Integrity Monitor
# date: 2026-03-29

import os
import sys
import json
import hashlib
import datetime
import sqlite3
import time

ROLL_NUMBER = "727823TUCY040"
STUDENT_NAME = "Samuvel A"
PROJECT_NAME = "File Integrity Monitor"
DB_FILE = "fim_727823TUCY040.db"
LOG_FILE = "tool_output_727823TUCY040.log"
BASELINE_FILE = "baseline_727823TUCY040.json"


def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def compute_hash(filepath, algorithm="sha256"):
    """Compute hash of a file using the specified algorithm."""
    h = hashlib.new(algorithm)
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except FileNotFoundError:
        return None
    except PermissionError:
        return "PERMISSION_DENIED"


def get_file_metadata(filepath):
    """Return file size, modification time, and permissions."""
    try:
        stat = os.stat(filepath)
        return {
            "size": stat.st_size,
            "modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "permissions": oct(stat.st_mode)
        }
    except FileNotFoundError:
        return None


def init_db():
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


def record_baseline(filepath):
    """Record a file's hash and metadata as baseline."""
    sha256 = compute_hash(filepath, "sha256")
    md5 = compute_hash(filepath, "md5")
    meta = get_file_metadata(filepath)
    if sha256 is None or meta is None:
        log(f"[BASELINE] SKIP — File not found: {filepath}")
        return False
    recorded_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO baseline
        (filepath, sha256, md5, size, permissions, modified, recorded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (filepath, sha256, md5, meta["size"], meta["permissions"], meta["modified"], recorded_at))
    conn.commit()
    conn.close()
    log(f"[BASELINE] Recorded: {filepath} | SHA256={sha256[:16]}... | Size={meta['size']}B")
    return True


def check_file(filepath):
    """Compare current file state against baseline. Return list of changes."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT sha256, md5, size, permissions FROM baseline WHERE filepath=?", (filepath,))
    row = c.fetchone()
    conn.close()

    changes = []
    if row is None:
        log(f"[CHECK] No baseline for: {filepath} — treating as NEW file")
        changes.append(("NEW_FILE", None, filepath))
        return changes

    baseline_sha256, baseline_md5, baseline_size, baseline_perms = row
    current_sha256 = compute_hash(filepath, "sha256")
    current_md5 = compute_hash(filepath, "md5")
    meta = get_file_metadata(filepath)

    if current_sha256 is None:
        changes.append(("FILE_DELETED", filepath, None))
        log(f"[ALERT] FILE DELETED: {filepath}")
        return changes

    if current_sha256 != baseline_sha256:
        changes.append(("HASH_CHANGED", baseline_sha256[:16] + "...", current_sha256[:16] + "..."))
        log(f"[ALERT] HASH CHANGED: {filepath} | Old={baseline_sha256[:16]}... New={current_sha256[:16]}...")

    if current_md5 != baseline_md5:
        log(f"[ALERT] MD5 CHANGED: {filepath}")

    if meta and meta["size"] != baseline_size:
        changes.append(("SIZE_CHANGED", str(baseline_size), str(meta["size"])))
        log(f"[ALERT] SIZE CHANGED: {filepath} | Old={baseline_size}B New={meta['size']}B")

    if meta and meta["permissions"] != baseline_perms:
        changes.append(("PERMISSIONS_CHANGED", baseline_perms, meta["permissions"]))
        log(f"[ALERT] PERMISSIONS CHANGED: {filepath} | Old={baseline_perms} New={meta['permissions']}")

    if not changes:
        log(f"[OK] No changes detected: {filepath}")

    return changes


def record_alert(filepath, change_type, old_value, new_value):
    detected_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO alerts (filepath, change_type, old_value, new_value, detected_at)
        VALUES (?, ?, ?, ?, ?)
    """, (filepath, change_type, str(old_value), str(new_value), detected_at))
    conn.commit()
    conn.close()


def get_alerts():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT filepath, change_type, old_value, new_value, detected_at FROM alerts ORDER BY detected_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def export_baseline_json():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT filepath, sha256, md5, size, permissions, modified, recorded_at FROM baseline")
    rows = c.fetchall()
    conn.close()
    data = []
    for row in rows:
        data.append({
            "filepath": row[0], "sha256": row[1], "md5": row[2],
            "size": row[3], "permissions": row[4],
            "modified": row[5], "recorded_at": row[6]
        })
    with open(BASELINE_FILE, "w") as f:
        json.dump(data, f, indent=2)
    log(f"[EXPORT] Baseline exported to {BASELINE_FILE} ({len(data)} file(s))")


def print_banner():
    print("=" * 65)
    print(f"  File Integrity Monitor")
    print(f"  Student : {STUDENT_NAME}")
    print(f"  Roll No : {ROLL_NUMBER}")
    print(f"  Date    : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)


# ── Helper to create test files ──────────────────────────────
def create_test_file(path, content):
    with open(path, "w") as f:
        f.write(content)


if __name__ == "__main__":
    print_banner()
    init_db()
    log(f"Roll Number: {ROLL_NUMBER} | Tool started")

    # ── Test Case 1: Baseline & Integrity Check (No Tampering) ──
    log("=== TEST CASE 1: Baseline & Integrity Check — No Tampering ===")
    create_test_file("test_config_727823.txt", "server=localhost\nport=8080\nmode=production\n")
    record_baseline("test_config_727823.txt")
    changes = check_file("test_config_727823.txt")
    if not changes:
        log("TC1 RESULT: File is INTACT — no changes detected.")

    # ── Test Case 2: Detect Content Modification ─────────────
    log("=== TEST CASE 2: Detect File Content Modification ===")
    create_test_file("test_script_727823.py", "# Original script\nprint('hello world')\n")
    record_baseline("test_script_727823.py")
    # Simulate tampering
    time.sleep(1)
    create_test_file("test_script_727823.py", "# TAMPERED script\nimport os; os.system('whoami')\n")
    changes = check_file("test_script_727823.py")
    for change in changes:
        record_alert("test_script_727823.py", change[0], change[1], change[2])
    log(f"TC2 RESULT: {len(changes)} change(s) detected — {[c[0] for c in changes]}")

    # ── Test Case 3: Detect File Deletion ────────────────────
    log("=== TEST CASE 3: Detect File Deletion ===")
    create_test_file("test_delete_727823.txt", "This file will be deleted.\n")
    record_baseline("test_delete_727823.txt")
    os.remove("test_delete_727823.txt")
    changes = check_file("test_delete_727823.txt")
    for change in changes:
        record_alert("test_delete_727823.txt", change[0], change[1], change[2])
    log(f"TC3 RESULT: {len(changes)} change(s) detected — {[c[0] for c in changes]}")

    # ── Test Case 4: Multiple Hash Algorithms ────────────────
    log("=== TEST CASE 4: Multi-Algorithm Hash Verification ===")
    create_test_file("test_multi_727823.cfg", "key=value\ndebug=false\n")
    sha256_hash = compute_hash("test_multi_727823.cfg", "sha256")
    md5_hash = compute_hash("test_multi_727823.cfg", "md5")
    sha1_hash = compute_hash("test_multi_727823.cfg", "sha1")
    log(f"  SHA256 : {sha256_hash}")
    log(f"  MD5    : {md5_hash}")
    log(f"  SHA1   : {sha1_hash}")
    log(f"TC4 RESULT: All 3 hash algorithms computed successfully.")

    # ── Test Case 5: Export Baseline Report ──────────────────
    log("=== TEST CASE 5: Export Baseline to JSON ===")
    record_baseline("test_config_727823.txt")
    record_baseline("test_script_727823.py")
    record_baseline("test_multi_727823.cfg")
    export_baseline_json()
    alerts = get_alerts()
    log(f"TC5 RESULT: Baseline exported. Total alerts in DB: {len(alerts)}")

    log(f"Roll Number: {ROLL_NUMBER} | All test cases completed.")
    print("=" * 65)
    print(f"  Log saved to: {LOG_FILE}")
    print("=" * 65)
