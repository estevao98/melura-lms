#!/usr/bin/env python3
"""Repository-only deployment readiness documentation check."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = [
    "docs/deployment/00-overview.md",
    "docs/deployment/01-environments.md",
    "docs/deployment/02-production-checklist.md",
    "docs/deployment/03-vps-setup-notes.md",
    "docs/deployment/04-environment-and-secrets.md",
    "docs/deployment/05-services-workers-scheduler.md",
    "docs/deployment/06-nginx-domain-https.md",
    "docs/deployment/07-deployment-runbook.md",
    "docs/deployment/08-logs-monitoring.md",
    "docs/deployment/09-go-live-checklist.md",
]

KEY_TERMS = {
    "secrets": ["secret", "secrets", "segredos"],
    "Redis": ["redis"],
    "workers": ["worker", "workers"],
    "scheduler": ["scheduler"],
    "backup": ["backup", "backups"],
    "restore": ["restore"],
    "HTTPS": ["https"],
    "rollback": ["rollback"],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").lower()


def main() -> int:
    print("Melura LMS deployment readiness documentation check")
    print("=" * 56)

    missing_docs = []
    combined = []

    for relative_path in REQUIRED_DOCS:
        path = ROOT / relative_path
        if path.exists():
            text = read_text(path)
            combined.append(text)
            print(f"[ok] {relative_path}")
        else:
            missing_docs.append(relative_path)
            print(f"[missing] {relative_path}")

    print()

    combined_text = "\n".join(combined)
    missing_terms = []

    for label, terms in KEY_TERMS.items():
        found = any(term.lower() in combined_text for term in terms)
        status = "ok" if found else "warn"
        print(f"[{status}] mentions {label}")
        if not found:
            missing_terms.append(label)

    if missing_terms:
        print()
        print("Warnings: expected deployment topics were not found:")
        for label in missing_terms:
            print(f"- {label}")

    if missing_docs:
        print()
        print("Required deployment docs are missing:")
        for relative_path in missing_docs:
            print(f"- {relative_path}")
        return 1

    print()
    print("All required deployment docs exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
