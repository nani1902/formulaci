"""Build all bench sets into ``data/bench/`` (and a versioned snapshot in ``formulaci/bench/sets/``)."""
from __future__ import annotations

import json
import shutil
import time
from collections import Counter
from pathlib import Path

from . import lacast, mutate
from .sets import known_good_records, write_jsonl

SNAPSHOT_DIR = Path(__file__).parent / "sets"


def build(out_dir: str | Path = "data/bench", jobs: int | None = None, seed: int = 0, snapshot: bool = True) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    good, rejected = known_good_records(jobs=jobs)
    write_jsonl(out / "known_good.jsonl", good)
    t1 = time.time()
    mstats = mutate.run(out / "known_good.jsonl", out / "mutated.jsonl", seed=seed, jobs=jobs)
    t2 = time.time()
    lac = lacast.records()
    write_jsonl(out / "lacast_benchmark.jsonl", lac)
    stats = {
        "known_good": {"n": len(good), "rejected_by_oracle": rejected,
                       "per_category": dict(Counter(r["bench"]["category"] for r in good)),
                       "seconds": round(t1 - t0, 1)},
        "mutated": {**mstats, "seconds": round(t2 - t1, 1)},
        "lacast": {"n": len(lac), "source": "https://github.com/gipplab/LaCASt misc/Results/Wikipedia (MIT)"},
        "seed": seed,
    }
    (out / "build_stats.json").write_text(json.dumps(stats, indent=1, ensure_ascii=False) + "\n")
    if snapshot:
        SNAPSHOT_DIR.mkdir(exist_ok=True)
        for name in ("known_good.jsonl", "mutated.jsonl", "lacast_benchmark.jsonl", "build_stats.json"):
            shutil.copy(out / name, SNAPSHOT_DIR / name)
    return stats
