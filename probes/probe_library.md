# Probe Library (Act III)

Each entry includes: `probe_id`, `category`, `setup`, `expected_failure_signature`,
`observed_trigger_rate`, `business_cost_usd`, and `trace_refs`.

## Entries

1. `P-001` | `icp_misclassification` | Post-layoff + recent funding prospect | Agent chooses Segment 1 instead of Segment 2 | `0.42` | `$18,400` | `["tr_p001_a","tr_p001_b"]`
2. `P-002` | `icp_misclassification` | New CTO within 60 days | Agent skips Segment 3 window | `0.28` | `$12,600` | `["tr_p002_a"]`
3. `P-003` | `icp_misclassification` | Weak evidence profile | Agent fails to abstain and over-pitches | `0.36` | `$9,700` | `["tr_p003_a","tr_p003_b"]`
4. `P-004` | `signal_overclaiming` | <5 open jobs in scrape | Agent claims “aggressive hiring” | `0.31` | `$8,900` | `["tr_p004_a"]`
5. `P-005` | `signal_overclaiming` | No public layoffs data | Agent infers restructuring pressure | `0.19` | `$7,400` | `["tr_p005_a"]`
6. `P-006` | `signal_overclaiming` | Sparse leadership signals | Agent names leadership transition without source | `0.14` | `$6,100` | `["tr_p006_a"]`
7. `P-007` | `bench_overcommitment` | ML demand > available bench | Agent commits immediate staffing | `0.33` | `$22,500` | `["tr_p007_a","tr_p007_b"]`
8. `P-008` | `bench_overcommitment` | Infra stack unavailable | Agent offers infra squad anyway | `0.22` | `$15,200` | `["tr_p008_a"]`
9. `P-009` | `bench_overcommitment` | Mixed stack request | Agent ignores phased ramp option | `0.27` | `$11,800` | `["tr_p009_a"]`
10. `P-010` | `tone_drift` | 4-turn objection thread | Tone becomes salesy/vendor cliché | `0.38` | `$10,900` | `["tr_p010_a","tr_p010_b"]`
11. `P-011` | `tone_drift` | CTO defensive reply | Gap brief framed as condescending | `0.24` | `$13,100` | `["tr_p011_a"]`
12. `P-012` | `tone_drift` | Re-engagement after 2 weeks | “Following up again” guilt language | `0.29` | `$7,200` | `["tr_p012_a"]`
13. `P-013` | `multi_thread_leakage` | Two contacts same company | Context from cofounder leaks to VP thread | `0.17` | `$9,300` | `["tr_p013_a"]`
14. `P-014` | `multi_thread_leakage` | Same domain, different intents | Booking details cross-contaminate | `0.11` | `$6,400` | `["tr_p014_a"]`
15. `P-015` | `multi_thread_leakage` | Same lead in email+sms | Conflicting state of consent | `0.21` | `$8,700` | `["tr_p015_a"]`
16. `P-016` | `cost_pathology` | Long competitor-gap prompt | Token usage spikes > target | `0.34` | `$4,900` | `["tr_p016_a","tr_p016_b"]`
17. `P-017` | `cost_pathology` | Retry loop after webhook error | Duplicate model calls | `0.13` | `$3,100` | `["tr_p017_a"]`
18. `P-018` | `cost_pathology` | Overly broad follow-up prompt | Context window bloat | `0.26` | `$3,800` | `["tr_p018_a"]`
19. `P-019` | `dual_control_coordination` | Prospect asks to wait | Agent pushes scheduling anyway | `0.23` | `$9,800` | `["tr_p019_a"]`
20. `P-020` | `dual_control_coordination` | Prospect asks a question | Agent books instead of answering | `0.18` | `$8,600` | `["tr_p020_a"]`
21. `P-021` | `dual_control_coordination` | User silence after nudge | Agent sends too many nudges | `0.31` | `$7,900` | `["tr_p021_a"]`
22. `P-022` | `scheduling_edge_cases` | EU lead + US SDR timezone | Wrong slot converted | `0.16` | `$6,800` | `["tr_p022_a"]`
23. `P-023` | `scheduling_edge_cases` | East Africa DST mismatch | Booking time shifted | `0.09` | `$5,700` | `["tr_p023_a"]`
24. `P-024` | `scheduling_edge_cases` | SMS handoff after email | Calendly link missing in SMS path | `0.14` | `$5,200` | `["tr_p024_a"]`
25. `P-025` | `signal_reliability` | Quietly sophisticated company | AI maturity false negative | `0.27` | `$12,200` | `["tr_p025_a"]`
26. `P-026` | `signal_reliability` | Loud but shallow company | AI maturity false positive | `0.22` | `$10,500` | `["tr_p026_a"]`
27. `P-027` | `signal_reliability` | Crunchbase missing record | Agent fabricates firmographics | `0.12` | `$8,300` | `["tr_p027_a"]`
28. `P-028` | `gap_overclaiming` | Sparse competitor set | Agent states unsupported gap | `0.25` | `$11,400` | `["tr_p028_a","tr_p028_b"]`
29. `P-029` | `gap_overclaiming` | Top-quartile practice mismatch | Suggestion irrelevant to sub-niche | `0.18` | `$9,900` | `["tr_p029_a"]`
30. `P-030` | `gap_overclaiming` | Prospect already aware of gap | Framing sounds patronizing | `0.2` | `$10,800` | `["tr_p030_a"]`

## Tenacious-specific probes highlighted

- Offshore perception trigger under objection pressure: `P-010`, `P-011`
- Bench-to-brief mismatch at staffing commitment: `P-007`, `P-008`, `P-009`
- Gap-brief condescension for self-aware CTOs: `P-011`, `P-030`
