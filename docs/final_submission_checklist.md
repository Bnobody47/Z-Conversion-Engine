# Final Submission Checklist

Use this list during recording and screenshot collection so every rubric item is backed by evidence.

## 1) Environment + startup

- [ ] Screenshot: `.env` with non-sensitive settings visible (mask all real keys/tokens).
- [ ] Screenshot: app boot command in terminal (`uvicorn agent.main:app --host 0.0.0.0 --port 8010`) and successful startup logs.
- [ ] Screenshot: `GET /health` response showing API is up.

## 2) Outbound email handler (Mastered evidence)

- [ ] Screenshot: email provider settings in `.env` (`EMAIL_PROVIDER`, `EMAIL_FROM`).
- [ ] Screenshot: successful `POST /outbound/email` response.
- [ ] Screenshot: `POST /webhooks/resend` inbound reply payload and `200` response.
- [ ] Screenshot: bounce event payload (`email.bounced`) accepted and logged.
- [ ] Screenshot: `agent/data/webhook_errors.jsonl` or related log proving malformed/failed payload handling path exists.

## 3) SMS handler (Mastered evidence)

- [ ] Screenshot: successful `POST /outbound/sms` response for warm lead.
- [ ] Screenshot: blocked SMS send before email reply (shows gating / warm-lead logic).
- [ ] Screenshot: `POST /webhooks/africastalking` inbound message and downstream route response.
- [ ] Screenshot: STOP/UNSUBSCRIBE example message and compliant handling response.

## 4) CRM + calendar integration (Mastered evidence)

- [ ] Screenshot: HubSpot auth check success (contacts endpoint `200`).
- [ ] Screenshot: lead write/create with enrichment fields (segment, signals, timestamp) in logs or payload.
- [ ] Screenshot: Cal.com booking webhook (`POST /webhooks/cal`) success.
- [ ] Screenshot: booking-triggered HubSpot update referencing same lead/prospect id/email.

## 5) Signal enrichment pipeline (Mastered evidence)

- [ ] Screenshot: lead processing output showing all sources merged:
  - Crunchbase signal
  - Job posts via Playwright
  - layoffs.fyi signal
  - Leadership change signal
- [ ] Screenshot: per-signal confidence values (`signal_confidence`, `confidence_score`, `confidence_label`).
- [ ] Screenshot: output artifact saved in `agent/data/leads.jsonl` or equivalent structured store.

## 6) Final deterministic smoke test artifact

- [ ] Run: `python scripts/final_smoke_test.py`
- [ ] Screenshot: terminal output with pass summary.
- [ ] Screenshot: generated `docs/final_smoke_test_output.json`.
- [ ] Confirm: `pass_summary` booleans show expected green checks.

## 7) Submission package hygiene

- [ ] `README.md` includes architecture, setup, endpoint map, and handoff notes.
- [ ] `interim_report.md` aligns with mastered rubric criteria.
- [ ] `render.yaml` present and valid for free-tier deployment.
- [ ] No real secrets committed to repository.
- [ ] Record a short demo walkthrough using the same flow above.
