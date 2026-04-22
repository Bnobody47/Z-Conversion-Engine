## Baseline Reproduction (Act I)

I set up a local evaluation harness in `eval/run_tau2_baseline.py` to generate reproducible score and trace artifacts for the τ²-Bench-style retail baseline workflow required in Act I.

Two tracked runs are recorded in `eval/score_log.json`:

- `dev_tier_baseline`: mean pass@1 `0.4333`, 95% CI `[0.3749, 0.4918]`
- `reproduction_check`: mean pass@1 `0.4000`, 95% CI `[0.3284, 0.4716]`

Each run contains:

- trial count (`n=5`)
- cost-per-eval estimate
- p50/p95 latency
- update timestamp

Trajectory-level records were written to `eval/trace_log.jsonl` and include trace IDs, domain labels, task IDs, pass/fail outcome, and run labels for auditability.

Observed behavior:

1. Reproduction score stays close to the baseline run and remains within expected variance at this sample size.
2. CI width is still relatively broad because the trial count is small (5); this is acceptable for interim but should be tightened in final by increasing run count.
3. Logging format is stable and can be plugged into Langfuse/OpenTelemetry with minimal changes.

Estimated run economics were kept low (about `$1.37` to `$1.42` per run), consistent with a dev-tier budget target.

For final submission, this harness should be pointed to pinned model settings and sealed held-out slices, then extended with formal statistical testing used in Act IV.
