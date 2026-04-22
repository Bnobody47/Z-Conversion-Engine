from __future__ import annotations

import json
import random
import uuid
from datetime import datetime, timezone
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
TRACE_FILE = DATA_DIR / "interaction_traces.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> None:
    random.seed(42)
    leads = [f"lead_{uuid.uuid4().hex[:8]}" for _ in range(20)]
    rows = []
    for lead_id in leads:
        rows.append(
            {
                "trace_id": f"tr_{uuid.uuid4().hex[:10]}",
                "lead_id": lead_id,
                "channel": random.choice(["email", "sms"]),
                "latency_ms": random.randint(950, 6100),
                "timestamp": _now(),
                "metadata": {"stage": random.choice(["initial_enrichment", "nurture_reply", "booking"])},
            }
        )

    with TRACE_FILE.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=True) + "\n")
    print(f"Wrote {len(rows)} traces to {TRACE_FILE}")


if __name__ == "__main__":
    main()
