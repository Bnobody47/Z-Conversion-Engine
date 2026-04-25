# Method (Act IV)

## Mechanism name

**Bench-Gated Confidence Router (BGCR)**.

## Re-implementable design

1. Build `hiring_signal_brief` with segment/confidence and `bench_to_brief_match`.
2. Before generating channel response:
   - Evaluate `bench_to_brief_match.bench_available`.
   - Evaluate `segment_confidence`.
3. Route to one of three output policies:
   - **Policy A: Commit** (bench available + confidence >= threshold)
   - **Policy B: Phase-ramp** (bench partial or borderline confidence)
   - **Policy C: Human handoff** (bench gap or low confidence)
4. Apply tone-preservation scoring before send; regenerate if score below threshold.
5. Log routing decision and policy reason in trace metadata for ablation attribution.

## Root-cause rationale

Target failure (`bench over-commitment`) is caused by free-form generation that skips explicit capacity checks.
BGCR addresses root cause by forcing a deterministic gate before response composition, so the model cannot promise staffing that policy disallows.

## Hyperparameters and thresholds (actual values)

- `segment_confidence_commit_threshold = 0.70`
- `segment_confidence_phase_threshold = 0.60`
- `tone_preservation_min_score = 4/5`
- `max_followups_without_reply = 3`
- `handoff_on_bench_gap = true`
- `abstain_on_confidence_below = 0.60`
- `cost_guardrail_usd_per_interaction = 0.50`

## Ablation variants

### Ablation A: No Bench Gate

- Change: remove hard bench check, keep confidence router.
- Tests: whether observed lift is attributable to bench gating specifically.

### Ablation B: Bench Gate Without Confidence Router

- Change: keep bench gate, disable confidence-conditioned phrasing/routing.
- Tests: incremental value of confidence-aware language and abstention.

### Ablation C: Bench Gate + Confidence Router Without Tone Check

- Change: keep routing logic, disable tone-preservation regeneration.
- Tests: effect of tone-protection layer on conversion and brand-risk probes.

## Statistical test plan

- Comparison: `BGCR` vs `Day-1 baseline` on sealed held-out slice.
- Metric: pass@1 and failure-trigger-rate reduction on target probe category.
- Test: two-proportion z-test on success rate and bootstrap CI comparison.
- Acceptance criterion: `p < 0.05` and positive Delta A with non-overlapping 95% CI directionality.

## Expected impact

- **Delta A**: positive due to direct reduction in over-commitment failures.
- **Delta B**: competitive with automated optimization on same compute budget because policy gate adds deterministic control not reliant on additional model calls.
