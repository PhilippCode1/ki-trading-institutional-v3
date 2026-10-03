"""Paketstand: SHA-256 über alle Inhaltsdateien des Pakets (§19.4).

Laufbelege (Ausführungsprotokoll, Mutationsbericht, Prüfbericht) und Auslieferungsdaten (Manifest, Prüfsummen) zählen nicht zum Paketstand;
sie tragen den Stand, auf dem sie entstanden sind. Die Paketprüfung (P13) vergleicht diesen Stand mit dem aktuellen und erkennt so Belege,
die zu einer älteren Fassung gehören.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

EVIDENCE_FILES = ("validation/execution_log.txt", "validation/mutation_report.json", "validation/validation_report.json",
                  "PACKAGE_MANIFEST.json", "CHECKSUMS.sha256")
SKIP_PARTS = {"__pycache__", ".ruff_cache"}


def content_files(root) -> list:
    root = Path(root)
    out = []
    for f in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = f.relative_to(root)
        if rel.as_posix() in EVIDENCE_FILES or SKIP_PARTS.intersection(rel.parts) or f.suffix == ".pyc":
            continue
        out.append(f)
    return out


def state_hash(root) -> str:
    """Hash über (relativer Pfad, SHA-256 des Inhalts) aller Inhaltsdateien in sortierter Reihenfolge."""
    root = Path(root)
    h = hashlib.sha256()
    for f in content_files(root):
        h.update(f.relative_to(root).as_posix().encode("utf-8") + b"\0" + hashlib.sha256(f.read_bytes()).hexdigest().encode("ascii") + b"\n")
    return h.hexdigest()
