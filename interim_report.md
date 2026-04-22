# Interim Report (Acts I + II)

## 1) Architecture Overview and Design Decisions

The system is implemented as a FastAPI service (`agent/main.py`) that handles:

- prospect ingestion and enrichment,
- qualification,
- multi-channel response handling (`email` + `sms`),
- CRM event writes,
- calendar booking writes,
- trace logging for metrics.

Design choices:

- Email-first model with SMS fallback support, matching Tenacious channel hierarchy.
- Confidence-aware enrichment output to avoid over-claiming.
- Guardrails for STOP/HELP/UNSUB and low-evidence messaging.
- Trace-first architecture so every claim can be tied to runtime records.

## 2) Production Stack Status

- Email handler: implemented as webhook/event interface in API.
- SMS handler: implemented as webhook/event interface in API.
- HubSpot integration: structured event sink (`agent/data/hubspot_events.jsonl`) with clear adapter boundary for MCP replacement.
- Cal.com booking flow: booking adapter writes structured booking records (`agent/data/cal_bookings.jsonl`).
- Observability: interaction traces in JSONL (`agent/data/interaction_traces.jsonl`) and eval traces (`eval/trace_log.jsonl`).

All stack components are running in challenge-safe synthetic mode and are ready for live-provider swap by replacing adapter internals.

## 3) Enrichment Pipeline Status

Pipeline runs before qualification and produces:

- firmographic-compatible lead context,
- `hiring_signal_brief` with funding, job-post velocity, layoffs, leadership-change signals,
- AI maturity score (0-3) with confidence + justification,
- `competitor_gap_brief` with percentile and missing top-quartile practices.

Outputs are attached to lead objects and written to structured storage for downstream CRM/reporting.

## 4) τ²-Bench Baseline and Methodology (Act I)

Artifacts generated in `eval/`:

- `score_log.json`:
  - dev-tier baseline mean pass@1: 0.4333 (95% CI: 0.3749 to 0.4918)
  - reproduction check mean pass@1: 0.4000 (95% CI: 0.3284 to 0.4716)
- `trace_log.jsonl`: trajectory-level trace entries for both runs.

Method:

- 5-trial runs, deterministic seed,
- CI computed from sample mean and standard error,
- cost and p50/p95 run latencies tracked per run.

## 5) Latency Metrics (20 Interactions)

From `agent/data/interaction_traces.jsonl`:

- interaction count: 20
- p50 latency: 2855 ms
- p95 latency: 5787 ms
- mean latency: 3087.7 ms

## 6) What Is Working / What Is Not / Plan

Working:

- End-to-end synthetic prospect processing.
- Brief generation and qualification outputs.
- Inbound conversation handling with compliance keyword support.
- CRM and calendar event generation.
- Eval harness and baseline logs.

Not yet live-wired:

- direct provider API calls for Resend/MailerSend, Africa's Talking, HubSpot MCP, and Cal.com.
- Langfuse direct sink (current traces are local JSONL).

Plan for remaining days:

1. Replace adapter sinks with real API integrations and secrets.
2. Route traces to Langfuse and add per-call token/cost accounting.
3. Build adversarial probe suite (30+) and failure taxonomy.
4. Implement one target mechanism and run held-out ablations.
5. Produce final memo + evidence graph + demo video.
