# Project Report — File Integrity Monitor
**Student:** Samuvel A  
**Roll Number:** 727823TUCY040  
**Project Name:** SKCT_727823TUCY040_FileIntegrityMonitor  
**Date:** 2026-03-29  

---

## 1. Tool Description

The File Integrity Monitor (FIM) is a command-line Python application that detects unauthorised changes to files by comparing their cryptographic hashes and metadata against a previously recorded **baseline**. It is a foundational security tool used in real-world environments — antivirus software, intrusion detection systems (IDS), and compliance frameworks (PCI-DSS, NIST) all rely on FIM principles.

**Core Architecture:**

The tool is built entirely using the Python standard library — `hashlib`, `sqlite3`, `os`, `json`, `datetime`, and `time` — with no external dependencies. This makes it portable across any Python 3.8+ environment without pip installation.

**Hash Computation:** For every monitored file, the tool reads the file in 8 KB chunks and feeds each chunk into a `hashlib` digest object. Three algorithms are supported: SHA-256 (primary, 256-bit, collision-resistant), MD5 (32-bit, legacy compatibility), and SHA-1 (40-bit, secondary check). Using chunked reading means even large files (gigabytes) can be hashed without loading the entire file into memory.

**Baseline Storage:** The first time a file is monitored, its hash (SHA-256 and MD5), file size, Unix permissions (octal), and last-modification timestamp are stored in a SQLite database table called `baseline`. The `filepath` column has a `UNIQUE` constraint, so re-baselining a file performs an `INSERT OR REPLACE` — updating the record atomically.

**Integrity Checking:** On each subsequent check, the tool recomputes the file's SHA-256 hash and compares it to the stored baseline. If the hash differs, a `HASH_CHANGED` alert is raised. If the file does not exist on disk, a `FILE_DELETED` alert is raised. Size and permission changes produce their own typed alerts. All alerts are inserted into a second SQLite table called `alerts` with a timestamp, enabling full forensic audit history.

**Pipeline Structure:** The project is divided into three pipeline scripts: `setup_lab.py` verifies the Python environment and initialises the database; `run_tool.py` executes all five test cases and saves structured results to a JSON file; `analyze_results.py` reads the JSON, prints a formatted summary table, queries the alerts database, and writes a full analysis report.

---

## 2. Test Results Table

| Test ID | Description | Input | Expected Output | Actual Result | Status |
|---------|-------------|-------|-----------------|---------------|--------|
| TC1 | Baseline & integrity check — no tampering | tc1_727823.txt (unmodified) | No changes detected | 0 changes, no alerts raised | ✅ PASS |
| TC2 | Detect content modification | tc2_727823.py (tampered content) | HASH_CHANGED + SIZE_CHANGED alerts | Both alerts raised and stored in DB | ✅ PASS |
| TC3 | Detect file deletion | tc3_727823.cfg (deleted) | FILE_DELETED alert | Alert raised, None returned for hash | ✅ PASS |
| TC4 | Multi-algorithm hash verification | tc4_727823.sh | SHA256 (64 chars), MD5 (32 chars), SHA1 (40 chars) | All three computed with correct lengths | ✅ PASS |
| TC5 | Multi-file monitoring & JSON export | 3 files baselined | baseline_727823TUCY040.json created | JSON created with 3 file records | ✅ PASS |

**Pass Rate: 5/5 (100%)**

---

## 3. Analysis of Findings

**TC1** confirmed that when a file is unmodified, the FIM produces zero false positives. The SHA-256 hash of the file read at check time matched the stored baseline exactly, and the metadata (size, permissions) was unchanged.

**TC2** demonstrated the core detection capability. When the content of `tc2_727823.py` was replaced with a simulated malicious payload (a reverse shell command), both the SHA-256 hash and the file size changed. The tool raised `HASH_CHANGED` and `SIZE_CHANGED` alerts immediately. This is the most critical test case — it mirrors real-world scenarios where an attacker replaces a legitimate script with a backdoor.

**TC3** tested deletion detection. After `os.remove()` was called, `compute_hash()` returned `None` (caught `FileNotFoundError`), which the `check_file()` function correctly mapped to a `FILE_DELETED` alert. File deletion is a common attacker tactic to remove audit logs or replace system binaries.

**TC4** verified that all three hash algorithms produce outputs of the correct length and are mutually independent. SHA-256 always produces 64 hexadecimal characters, MD5 produces 32, and SHA-1 produces 40. Having multiple algorithms provides defence in depth — even if MD5 collisions were exploited, SHA-256 would still detect the tampering.

**TC5** confirmed that the baseline export feature works correctly. The exported JSON file contained one entry per monitored file, with all metadata fields populated. This enables offline auditing and comparison between system states, which is useful for compliance reporting.

**Overall Assessment:** The FIM correctly handles the three most common integrity violation scenarios: modification, deletion, and multi-file monitoring. Its use of SQLite for both baseline and alert storage means all events are persistently recorded and queryable. A production enhancement would be to add real-time directory watching using `inotify` (Linux) or `watchdog`, and to add HMAC signing of the baseline database to prevent an attacker from also tampering with the baseline itself.

---

## 4. Real Error Encountered

During development, the following error was encountered when running `run_tool.py` before `setup_lab.py` had been executed to initialise the database:

```
Traceback (most recent call last):
  File "run_tool.py", line 78, in run_test_case_1
    record_baseline("tc1_727823.txt")
  File "/home/kali/SKCT_727823TUCY040_FileIntegrityMonitor/tool_main.py", line 62, in record_baseline
    c.execute(
sqlite3.OperationalError: no such table: baseline
```

This occurred because `run_tool.py` imports and calls `record_baseline()` from `tool_main.py`, but the SQLite database file `fim_727823TUCY040.db` did not yet have the `baseline` table created — it had not been initialised by `init_db()`. The script was calling `record_baseline()` before `init_db()` in the `__main__` block. The fix was to add an explicit `init_db()` call at the top of `run_tool.py`'s `__main__` block, before any test case runs. Additionally, `clear_db()` was added to DELETE all rows from both tables at the start of each pipeline run, ensuring clean, reproducible test results without residual data from previous executions. This error affected TC1 through TC5 initially since all test cases depend on the `baseline` table existing.

---

*Report prepared by Samuvel A | Roll No: 727823TUCY040 | SKCT | 2026-03-29*
