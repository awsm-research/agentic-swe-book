# security_review.py
import subprocess
import sys


def run_bandit(path: str) -> tuple[str, int]:
    result = subprocess.run(
        ["bandit", path, "-f", "text", "-l", "-ii"],
        capture_output=True,
        text=True,
    )
    return result.stdout or result.stderr, result.returncode


def run_semgrep(path: str) -> tuple[str, int]:
    result = subprocess.run(
        ["semgrep", "--config", "p/python", "--config", "p/owasp-top-ten", path],
        capture_output=True,
        text=True,
    )
    return result.stdout or result.stderr, result.returncode


def review_file(path: str) -> int:
    print(f"\n{'=' * 60}")
    print(f"SECURITY REVIEW: {path}")
    print("=" * 60)
    exit_code = 0

    print("\n--- Bandit ---")
    bandit_out, bandit_rc = run_bandit(path)
    print(bandit_out if bandit_out.strip() else "No issues found.")
    if bandit_rc != 0:
        exit_code = 1

    print("\n--- Semgrep ---")
    semgrep_out, semgrep_rc = run_semgrep(path)
    print(semgrep_out if semgrep_out.strip() else "No issues found.")
    if semgrep_rc != 0:
        exit_code = 1

    return exit_code


if __name__ == "__main__":
    paths = sys.argv[1:]
    if not paths:
        print("Usage: python security_review.py <file1.py> [file2.py ...]")
        sys.exit(1)
    overall = 0
    for path in paths:
        overall |= review_file(path)
    sys.exit(overall)
