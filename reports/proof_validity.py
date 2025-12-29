#!/usr/bin/env python3
import argparse, json
from pathlib import Path
'''Uruchominie: python3 proof_validity.py \
  --out ../out.txt \
  --h_json ../data/horizontal_photos.json \
  --v_json ../data/vertical_photos.json \
  --report ../reports/proof_validity.txt'''

def load_ids(path: Path) -> set[int]:
    with open(path, "r", encoding="utf-8") as f:
        return {int(x["id"]) for x in json.load(f)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--h_json", required=True)
    ap.add_argument("--v_json", required=True)
    ap.add_argument("--report", default="reports/proof_validity.txt")
    args = ap.parse_args()

    out_path = Path(args.out)
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    H = load_ids(Path(args.h_json))
    V = load_ids(Path(args.v_json))
    all_ids = H | V

    with open(out_path, "r", encoding="utf-8") as f:
        declared = int(f.readline().strip())
        lines = [ln.strip() for ln in f if ln.strip()]

    bad_len = bad_H = bad_VV = dup = unknown = 0
    used = set()
    singles = pairs = 0

    for ln in lines:
        parts = ln.split()
        if len(parts) not in (1, 2):
            bad_len += 1
            continue

        ids = list(map(int, parts))
        for pid in ids:
            if pid not in all_ids:
                unknown += 1
            if pid in used:
                dup += 1
            used.add(pid)

        if len(ids) == 1:
            singles += 1
            if ids[0] not in H:
                bad_H += 1
        else:
            pairs += 1
            if ids[0] not in V or ids[1] not in V:
                bad_VV += 1

    ok = (declared == len(lines) and bad_len == 0 and dup == 0 and unknown == 0 and bad_H == 0 and bad_VV == 0)

    with open(report_path, "w", encoding="utf-8") as r:
        r.write("PROOF: poprawność out.txt\n")
        r.write(f"Slajdy: nagłówek={declared}, linie={len(lines)}\n")
        r.write(f"Slajdy 1-ID (H): {singles}\n")
        r.write(f"Slajdy 2-ID (V+V): {pairs}\n")
        r.write(f"Użyte unikalne zdjęcia: {len(used)}\n")
        r.write("\nBłędy:\n")
        r.write(f"- złe długości linii: {bad_len}\n")
        r.write(f"- duplikaty ID: {dup}\n")
        r.write(f"- nieznane ID: {unknown}\n")
        r.write(f"- 1-ID ale nie H: {bad_H}\n")
        r.write(f"- 2-ID ale nie V+V: {bad_VV}\n")
        r.write("\nWYNIK: " + ("OK" if ok else "NIE OK") + "\n")

    print(f"Zapisano: {report_path}")

if __name__ == "__main__":
    main()
