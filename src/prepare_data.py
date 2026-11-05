"""Swiss-Prot data collection.

  python src/prepare_data.py download --out data/raw/swissprot.tsv.gz            # full (~570k entries)
  python src/prepare_data.py download --out data/raw/sample.tsv.gz --limit 500   # quick test
  python src/prepare_data.py cluster  --tsv data/raw/swissprot.tsv.gz --out data/interim   # optional, needs mmseqs

TODO: build step (annotations -> QA jsonl, train/val/test split) to be added later.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://rest.uniprot.org/uniprotkb"
FIELDS = ["accession", "protein_name", "organism_name", "length", "sequence",
          "cc_function", "cc_subcellular_location", "ec"]


def download(out: str, limit: int | None, query: str):
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    params = {"query": query, "format": "tsv", "fields": ",".join(FIELDS)}
    if limit:
        url = f"{API}/search?" + urllib.parse.urlencode({**params, "size": limit})
    else:
        url = f"{API}/stream?" + urllib.parse.urlencode({**params, "compressed": "true"})
    print("GET", url)
    req = urllib.request.Request(url, headers={"Accept-Encoding": "identity"})
    for attempt in range(1, 6):   # the stream endpoint can be slow to start or return 429/5xx
        try:
            with urllib.request.urlopen(req, timeout=600) as r, open(out, "wb") as fh:
                if limit:   # search endpoint returns plain text -> gzip it ourselves
                    with gzip.GzipFile(fileobj=fh, mode="wb") as gz:
                        shutil.copyfileobj(r, gz)
                else:
                    shutil.copyfileobj(r, fh)
            break
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            wait = 30 * attempt
            print(f"attempt {attempt} failed ({e}); retrying in {wait}s")
            time.sleep(wait)
    else:
        sys.exit("download failed after 5 attempts")
    print("saved", out, f"{Path(out).stat().st_size / 1e6:.1f} MB")


def read_tsv(path: str):
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        yield from csv.DictReader(fh, delimiter="\t")


def cluster(tsv: str, out: str, min_id: float):
    if not shutil.which("mmseqs"):
        sys.exit("mmseqs not found. Install: conda install -c bioconda mmseqs2  (or apt/brew)")
    Path(out).mkdir(parents=True, exist_ok=True)
    fasta = Path(out) / "seqs.fasta"
    with open(fasta, "w") as fh:
        for r in read_tsv(tsv):
            fh.write(f">{r['Entry']}\n{r['Sequence']}\n")
    prefix, tmp = Path(out) / "clusters", tempfile.mkdtemp()   # tmp on local disk (Drive is slow for mmseqs)
    subprocess.run(["mmseqs", "easy-cluster", str(fasta), str(prefix), tmp,
                    "--min-seq-id", str(min_id), "-c", "0.8", "--cov-mode", "1"], check=True)
    print("cluster file:", f"{prefix}_cluster.tsv")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("download")
    d.add_argument("--out", default="data/raw/swissprot.tsv.gz")
    d.add_argument("--limit", type=int, default=None, help="small sample for testing")
    d.add_argument("--query", default="reviewed:true")
    c = sub.add_parser("cluster")
    c.add_argument("--tsv", required=True)
    c.add_argument("--out", default="data/interim")
    c.add_argument("--min-id", type=float, default=0.3)
    a = ap.parse_args()
    if a.cmd == "download":
        download(a.out, a.limit, a.query)
    else:
        cluster(a.tsv, a.out, a.min_id)


if __name__ == "__main__":
    main()
