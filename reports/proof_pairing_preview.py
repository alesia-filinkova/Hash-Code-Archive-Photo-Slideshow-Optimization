#!/usr/bin/env python3
import argparse, json
from pathlib import Path
'''Uruchomienie: python3 proof_pairing_preview.py \
  --out ../out.txt \
  --h_json ../data/horizontal_photos.json \
  --v_json ../data/vertical_photos.json \
  --k 30 \
  --report ../reports/proof_preview.txt'''

def build_orient_map(h_path: Path, v_path: Path) -> dict[int, str]:
    m = {}
    H = json.load(open(h_path, "r", encoding="utf-8"))
    V = json.load(open(v_path, "r", encoding="utf-8"))
    for p in H:
        m[int(p["id"])] = "H"
    for p in V:
        m[int(p["id"])] = "V"
    return m

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--h_json", required=True)
    ap.add_argument("--v_json", required=True)
    ap.add_argument("--k", type=int, default=30)
    ap.add_argument("--report", default="reports/proof_preview.txt")
    args = ap.parse_args()

    out_path = Path(args.out)
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    orient = build_orient_map(Path(args.h_json), Path(args.v_json))

    with open(out_path, "r", encoding="utf-8") as f:
        declared = int(f.readline().strip())
        lines = [ln.strip() for ln in f if ln.strip()]

    k = min(args.k, len(lines))

    with open(report_path, "w", encoding="utf-8") as r:
        r.write(f"PREVIEW: pierwsze {k} slajdów (nagłówek={declared})\n")
        for i in range(k):
            parts = lines[i].split()
            ids = list(map(int, parts))
            if len(ids) == 1:
                pid = ids[0]
                r.write(f"{i+1:02d}. H  {pid}   (w danych: {orient.get(pid,'?')})\n")
            elif len(ids) == 2:
                a, b = ids
                r.write(f"{i+1:02d}. V  {a} {b}   (w danych: {orient.get(a,'?')},{orient.get(b,'?')})\n")
            else:
                r.write(f"{i+1:02d}. ??? {lines[i]}\n")

    print(f"Zapisano: {report_path}")

if __name__ == "__main__":
    main()
