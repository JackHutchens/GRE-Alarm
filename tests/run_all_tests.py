"""
Master Test Runner for GRE Torture Alarm Unit & Integration Test Suite.

Runs:
1. tests/test_alarm_state.py (State Manager unit tests)
2. tests/test_scoring_engine.py (Scoring Engine unit tests)
3. tests/test_data_integrity.py (Question pool and JSON datasets verification)
4. tests/test_server_endpoints.py (HTTP server, endpoints, audio streaming, and security)
5. tests/test_frontend_contracts.py (HTML/JS contract verification & static analysis)
6. tests/test_web_logic.js (Node.js web logic and physics verification)
"""

import os
import sys
import subprocess
import time

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TEST_DIR)


def run_pytest_suite():
    print("=" * 70)
    print("  RUNNING PYTHON PYTEST SUITE")
    print("=" * 70)
    cmd = [sys.executable, "-m", "pytest", TEST_DIR, "-v"]
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return result.returncode


def run_node_suite():
    print("\n" + "=" * 70)
    print("  RUNNING NODE.JS FRONTEND LOGIC TEST SUITE")
    print("=" * 70)
    js_test_path = os.path.join(TEST_DIR, "test_web_logic.js")
    cmd = ["node", "--test", js_test_path]
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return result.returncode


def main():
    start = time.time()
    print("Starting Comprehensive Test Execution...")
    pytest_code = run_pytest_suite()
    node_code = run_node_suite()

    elapsed = time.time() - start
    print("\n" + "=" * 70)
    print("  TEST SUITE EXECUTION SUMMARY")
    print("=" * 70)
    print(f"Python Pytest Status : {'PASSED' if pytest_code == 0 else 'FAILED'}")
    print(f"Node.js Test Status   : {'PASSED' if node_code == 0 else 'FAILED'}")
    print(f"Total Execution Time : {elapsed:.2f} seconds")
    print("=" * 70)

    if pytest_code != 0 or node_code != 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
