#!/usr/bin/env python3
"""Repository-only backup and restore readiness documentation check."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = [
    "docs/backup-restore/00-overview.md",
    "docs/backup-restore/01-backup-policy.md",
    "docs/backup-restore/02-backup-runbook.md",
    "docs/backup-restore/03-restore-runbook.md",
    "docs/backup-restore/04-restore-test-plan.md",
    "docs/backup-restore/05-disaster-recovery-checklist.md",
    "docs/backup-restore/06-backup-security-and-retention.md",
]

KEY_TERMS = {
    "backup": ["backup", "backups"],
    "restore": ["restore", "restored", "restoration"],
    "staging/test": ["staging", "test", "non-production"],
    "retention": ["retention"],
    "encryption": ["encryption", "encrypted"],
    "secrets": ["secret", "secrets", "token", "api key"],
    "personal data": ["personal data", "student data", "lgpd"],
    "rollback": ["rollback"],
    "smoke tests": ["smoke test", "smoke tests"],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").lower()


def main() -> int:
    print("Melura LMS backup/restore readiness documentation check")
    print("=" * 60)

    missing_docs = []
    combined_text_parts = []

    for relative_path in REQUIRED_DOCS:
        path = ROOT / relative_path
        if path.exists():
            combined_text_parts.append(read_text(path))
            print(f"[ok] {relative_path}")
        else:
            missing_docs.append(relative_path)
            print(f"[missing] {relative_path}")

    print()

    combined_text = "\n".join(combined_text_parts)
    missing_terms = []

    for label, terms in KEY_TERMS.items():
        found = any(term.lower() in combined_text for term in terms)
        status = "ok" if found else "missing"
        print(f"[{status}] mentions {label}")
        if not found:
            missing_terms.append(label)

    if missing_docs:
        print()
        print("Required backup/restore docs are missing:")
        for relative_path in missing_docs:
            print(f"- {relative_path}")

    if missing_terms:
        print()
        print("Required backup/restore topics are missing:")
        for label in missing_terms:
            print(f"- {label}")

    if missing_docs or missing_terms:
        return 1

    print()
    print("All required backup/restore docs and topics are present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

