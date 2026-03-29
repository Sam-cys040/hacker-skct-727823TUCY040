# hacker-skct-727823TUCY040

**Project:** File Integrity Monitor  
**Student:** Samuvel A  
**Roll Number:** 727823TUCY040  
**Institution:** SKCT  
**Date:** 2026-03-29  

---

## 📌 Project Description

A command-line **File Integrity Monitor (FIM)** built in Python using only the standard library. It computes cryptographic hashes (SHA-256, MD5, SHA-1) of files and stores them as a **baseline** in a local SQLite database. On subsequent checks, it compares the current file state against the baseline and raises alerts for any changes — modified content, deleted files, size changes, or permission changes.

**Key Features:**
- SHA-256, MD5, SHA-1 hash computation per file
- SQLite-backed baseline storage with metadata (size, permissions, modification time)
- Tamper detection: content modification, file deletion, size change, permission change
- Alert logging to database for forensic review
- Baseline export to JSON for offline auditing
- Zero external dependencies — pure Python stdlib

---

## 📁 Project Folder

```
SKCT_727823TUCY040_FileIntegrityMonitor/
├── tool_main.py                     # Core FIM tool
├── setup_lab.py                     # Stage 1 — environment setup
├── run_tool.py                      # Stage 2 — run all test cases
├── analyze_results.py               # Stage 3 — analyze & report
├── pipeline_727823TUCY040.yml       # Pipeline definition
├── demo_notebook.ipynb              # Jupyter demo notebook
├── requirements.txt                 # No external deps
└── README.md                        # This file
```

---

## ⚙️ Setup & Run

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/hacker-skct-727823TUCY040.git
cd hacker-skct-727823TUCY040

# 2. No pip install needed — stdlib only

# 3. Run the full pipeline
python3 setup_lab.py
python3 run_tool.py
python3 analyze_results.py

# Or run the main tool directly
python3 tool_main.py
```

---

## 🧪 Test Cases

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| TC1 | Baseline & integrity check — no tampering | No changes detected |
| TC2 | Detect content modification (hash change) | HASH_CHANGED alert raised |
| TC3 | Detect file deletion | FILE_DELETED alert raised |
| TC4 | Multi-algorithm hash verification | SHA256, MD5, SHA1 all computed |
| TC5 | Multi-file monitoring & JSON export | Baseline JSON created with all files |

---

## 🔐 Hashing Details

| Algorithm | Output Length | Use |
|-----------|--------------|-----|
| SHA-256 | 64 hex chars | Primary integrity check |
| MD5 | 32 hex chars | Secondary / legacy check |
| SHA-1 | 40 hex chars | Additional verification |

---

## 📋 Output Files

| File | Description |
|------|-------------|
| `fim_727823TUCY040.db` | SQLite database (baseline + alerts) |
| `setup_log_727823TUCY040.log` | Setup stage log |
| `run_log_727823TUCY040.log` | Run stage log with timestamps |
| `results_727823TUCY040.json` | Structured test results |
| `baseline_727823TUCY040.json` | Exported baseline report |
| `analysis_report_727823TUCY040.txt` | Final analysis report |

---

## 💻 Environment

- OS: Kali Linux (VirtualBox VM)
- Python: 3.8+ (standard library only)
- Database: SQLite3 (local, no network)
- All testing performed on isolated VM

---

## ⚠️ Legal Notice

All testing was performed on files owned by the student within an isolated virtual machine. No external systems were targeted or monitored.

---

*Roll Number: 727823TUCY040 | SKCT*
