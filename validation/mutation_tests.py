#!/usr/bin/env python3
"""Mutationstests der Paketprüfung (§19.3, Test T-PKG-MUT-001).

Jede Mutation aus validation/mutation_catalog.json wird auf eine frische Kopie des Pakets angewandt; danach laufen die genannten Phasen von
validation/validate_package.py (mit --calc-mode hash). Eine Mutation gilt als erkannt, wenn die Prüfung scheitert und eine Fehlermeldung das
erwartete Muster enthält. Vorher müssen dieselben Phasen auf einer unveränderten Kopie bestehen (Grundlauf); sonst ist der Befund ungültig.

Aufruf:  python validation/mutation_tests.py --root . [--only MUT-01,MUT-02] [--jobs 4] [--report validation/mutation_report.json]
Exitcode 0 nur, wenn alle Mutationen erkannt sind und mindestens 40 Mutationen laufen.

Im Belegzyklus (§19.4) läuft dieser Test nach dem Mehrversionslauf: Das Ausführungsprotokoll muss zum aktuellen Paketstand gehören; der
Mutationsbericht und der Prüfbericht vor dem Packen entstehen erst und werden der Paketprüfung als --pending-evidence genannt.
Der Bericht trägt den Paketstand (lib/pkgstate.py), auf dem er entstanden ist. Zitierte Nutzlasten (unbekannte Kennungen, Platzhalter, Adressen,
Schlüssel, Pfade) stehen im Bericht wie im Katalog mit dem Entschärfungszeichen.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.dont_write_bytecode = True
MIN_MUTATIONS = 40
PENDING = "validation/mutation_report.json,validation/validation_report.json"


def _resolve(doc, pointer: str):
    """Liefert (Elternobjekt, Schlüssel) für einen JSON-Pointer mit Auswahlsegmenten [id=WERT]."""
    parts = [p for p in pointer.split("/") if p != ""]
    cur = doc
    for i, part in enumerate(parts):
        last = i == len(parts) - 1
        m = re.fullmatch(r"\[id=(.+)\]", part)
        if m:
            idx = next((k for k, x in enumerate(cur) if isinstance(x, dict) and x.get("id") == m.group(1)), None)
            if idx is None:
                raise KeyError(f"kein Element mit id={m.group(1)}")
            key = idx
        elif isinstance(cur, list):
            key = int(part)
        else:
            key = part.replace("~1", "/").replace("~0", "~")
        if last:
            return cur, key
        cur = cur[key]
    raise KeyError("leerer Zeiger")


def apply(root: Path, mu: dict) -> None:
    path = root / mu["file"]
    op = mu["op"]
    if op == "file_delete":
        path.unlink()
        return
    if op in ("text_replace", "text_append"):
        text = path.read_text(encoding="utf-8")
        if op == "text_append":
            text += mu["text"]
        elif mu.get("regex"):
            new, n = re.subn(mu["find"], mu["replace"], text, count=1)
            if n == 0:
                raise KeyError(f"Muster nicht gefunden: {mu['find'][:60]}")
            text = new
        else:
            if mu["find"] not in text:
                raise KeyError(f"Text nicht gefunden: {mu['find'][:60]}")
            text = text.replace(mu["find"], mu["replace"], 1)
        path.write_text(text, encoding="utf-8")
        return
    doc = json.loads(path.read_text(encoding="utf-8"))
    for step in [{"pointer": mu["pointer"], "value": mu.get("value")}] + mu.get("also", []):
        parent, key = _resolve(doc, step["pointer"])
        if op == "json_set":
            parent[key] = step["value"]
        elif op == "json_delete":
            del parent[key]
        elif op == "json_append":
            parent[key].append(step["value"])
        else:
            raise ValueError(f"unbekannte Operation {op}")
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def undefuse(x, marker: str):
    """Entfernt das Entschärfungszeichen des Katalogs aus allen Zeichenketten einer Mutation."""
    if isinstance(x, str):
        return x.replace(marker, "")
    if isinstance(x, list):
        return [undefuse(v, marker) for v in x]
    if isinstance(x, dict):
        return {k: undefuse(v, marker) for k, v in x.items()}
    return x


def refuse(x, entry: dict, marker: str):
    """Setzt das Entschärfungszeichen in Berichtstexte wieder ein, wo sie Nutzlasten der Mutation zitieren (Hygiene P05, P11).

    Für jede entschärfte Stelle des Katalogeintrags (Zeichen links und rechts des Zeichens) wird dieselbe Zeichenfolge im Bericht
    wieder getrennt, damit der Bericht weder unbekannte Kennungen noch Platzhalter, Adressen, Schlüssel oder Pfade im Klartext enthält.
    """
    pairs = set()

    def collect(v):
        if isinstance(v, str):
            parts = v.split(marker)
            for left, right in zip(parts[:-1], parts[1:], strict=True):
                lt = re.search(r"[\w./-]{0,3}$", left).group(0)
                rh = re.match(r"[\w@]{0,3}", right).group(0)
                if lt + rh:
                    pairs.add((lt, rh))
        elif isinstance(v, list):
            for w in v:
                collect(w)
        elif isinstance(v, dict):
            for w in v.values():
                collect(w)
    collect(entry)

    def fix(v):
        if isinstance(v, str):
            for lt, rh in sorted(pairs):
                v = v.replace(lt + rh, lt + marker + rh)
            return v
        if isinstance(v, list):
            return [fix(w) for w in v]
        if isinstance(v, dict):
            return {k: (w if k == "id" else fix(w)) for k, w in v.items()}
        return v
    return fix(x)


def copy_pkg(src: Path, base: Path, name: str) -> Path:
    dst = base / name / src.name
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "mutation_report.json"))
    return dst


def run_phases(root: Path, phases) -> tuple[int, str]:
    r = subprocess.run([sys.executable, "-W", "error", "validation/validate_package.py", "--root", ".", "--only", ",".join(phases), "--calc-mode", "hash",
                        "--pending-evidence", PENDING],
                       cwd=root, capture_output=True, text=True, timeout=1800,
                       env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin:/usr/local/bin", "PYTHONHASHSEED": "0", "PYTHONIOENCODING": "utf-8"})
    return r.returncode, r.stdout + r.stderr


def phase_errors(out: str, phases) -> list:
    errs, cur = [], None
    for ln in out.splitlines():
        m = re.match(r"^(P\d\d) (\S+)", ln)
        if m:
            cur = m.group(1)
            continue
        if cur in phases and ln.strip().startswith("FEHLER"):
            errs.append(f"{cur}: {ln.strip()[6:].strip()}")
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--report", default="")
    a = ap.parse_args(argv)
    src = Path(a.root).resolve()
    sys.path.insert(0, str(src))
    from lib.pkgstate import state_hash  # noqa: PLC0415
    state = state_hash(src)
    cat = json.loads((src / "validation/mutation_catalog.json").read_text(encoding="utf-8"))
    raw = {x["id"]: x for x in cat["mutations"]}
    muts = [undefuse(x, cat["defuse_marker"]) for x in cat["mutations"] if not a.only or x["id"] in a.only.split(",")]
    base = Path(tempfile.mkdtemp(prefix="mut_"))
    try:
        # Grundlauf je Phasenmenge auf unveränderter Kopie
        sets = sorted({tuple(x["phases"]) for x in muts})
        clean = copy_pkg(src, base, "grundlauf")

        def baseline(ph):
            rc, out = run_phases(clean, ph)
            return ph, rc, phase_errors(out, ph)
        with ThreadPoolExecutor(max_workers=a.jobs) as ex:
            base_res = {ph: (rc, errs) for ph, rc, errs in ex.map(baseline, sets)}

        def one(mu):
            ph = tuple(mu["phases"])
            rc0, errs0 = base_res[ph]
            if rc0 != 0:
                return {"id": mu["id"], "title": mu["title"], "detected": False, "status": "GRUNDLAUF_SCHEITERT", "detail": errs0[:3]}
            root = copy_pkg(src, base, mu["id"])
            try:
                apply(root, mu)
            except (KeyError, ValueError, IndexError, OSError) as e:
                return {"id": mu["id"], "title": mu["title"], "detected": False, "status": "NICHT_ANWENDBAR", "detail": [str(e)]}
            rc, out = run_phases(root, ph)
            errs = phase_errors(out, ph)
            hit = [e for e in errs if re.search(mu["expect"], e)]
            shutil.rmtree(root.parent, ignore_errors=True)
            return {"id": mu["id"], "title": mu["title"], "category": mu["category"], "phases": list(ph), "detected": rc != 0 and bool(hit),
                    "status": "ERKANNT" if rc != 0 and hit else "NICHT_ERKANNT", "detail": (hit or errs)[:2]}
        with ThreadPoolExecutor(max_workers=a.jobs) as ex:
            res = list(ex.map(one, muts))
    finally:
        shutil.rmtree(base, ignore_errors=True)
    det = sum(1 for r in res if r["detected"])
    ok = det == len(res) and len(res) >= MIN_MUTATIONS
    for r in res:
        print(f"{r['id']} {r['status']:<20} {r['title']}")
        if not r["detected"]:
            for d in r["detail"]:
                print(f"    {d[:200]}")
    print("MUTATIONEN", "PASS" if ok else "FAIL", f"{det}/{len(res)} erkannt")
    if a.report:
        if state_hash(src) != state:
            print("ABBRUCH: Paketstand hat sich während des Laufs geändert; kein Bericht geschrieben")
            return 1
        rep = {"document": "Bericht der Mutationstests", "catalog": "validation/mutation_catalog.json", "as_of": cat["as_of"],
               "package_state": state, "python": sys.version.split()[0], "total": len(res),
               "detected": det, "minimum": MIN_MUTATIONS, "required_by_19_3": sorted(x["id"] for x in muts if x.get("required")),
               "result": "PASS" if ok else "FAIL", "mutations": [refuse(r, raw[r["id"]], cat["defuse_marker"]) for r in res]}
        (src / a.report).write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
