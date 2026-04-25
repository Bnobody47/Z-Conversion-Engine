# Target Failure Mode (Act III -> Act IV)

## Selected failure mode

**Bench over-commitment during qualification and objection handling** (`P-007`, `P-008`, `P-009`).

## Why this wins on ROI

This failure combines high business impact with moderate frequency:

- Aggregate trigger rate: `0.273`
- Average estimated cost per occurrence:
  - `(22500 + 15200 + 11800) / 3 = 16,500 USD`
- Expected weekly cost exposure over 120 qualified conversations:
  - `120 * 0.273 * 16,500 = 540,540 USD exposure-equivalent`

This is a large risk because over-commitment creates immediate trust break, escalates SDR cleanup burden, and can poison future outreach in the same network.

## Alternatives considered

1. **Tone drift** (`P-010` to `P-012`)
   - Aggregate rate higher (`0.303`) but average per-event cost lower (`~10,400 USD`).
   - Exposure-equivalent: `120 * 0.303 * 10,400 = 378,144 USD`.
2. **Signal over-claiming** (`P-004` to `P-006`)
   - Aggregate rate lower (`0.213`) and lower average cost (`~7,467 USD`).
   - Exposure-equivalent: `120 * 0.213 * 7,467 = 190,824 USD`.

Bench over-commitment is selected because it yields the highest dollar-adjusted risk reduction opportunity while being tractable via policy + state constraints.

## Expected cost reduction

Assuming mechanism lowers trigger rate from `0.273` to `0.10`:

- Weekly reduction:
  - `120 * (0.273 - 0.10) * 16,500 = 342,540 USD exposure-equivalent avoided`

## Mechanism to test in Act IV

**Bench-Gated Commitment Policy**

- Hard-check required stack against `seed/bench_summary.json` before any capacity promise.
- If unavailable or insufficient:
  - offer phased ramp with explicit limits, or
  - route to human delivery lead immediately.
- Couple with confidence-aware phrasing to avoid assertive staffing claims under weak evidence.
