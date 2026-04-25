"use client";

import { useMemo, useState } from "react";

type StepResult = {
  status_code: number;
  body: unknown;
};

type StepKey =
  | "health"
  | "leads_process"
  | "outbound_email"
  | "outbound_sms_before_reply"
  | "inbound_email_reply"
  | "outbound_sms_after_reply"
  | "resend_bounce"
  | "cal_booking"
  | "latency"
  | "smoke_artifact";

type StepMap = Partial<Record<StepKey, StepResult>>;

const DEFAULT_LEAD = {
  company_name: "Frontend Demo Prospect",
  website: "frontend-demo.co",
  email: "frontend-demo@example.com",
  phone: "+251911555556",
  synthetic: true,
};

async function apiRequest(baseUrl: string, endpoint: string, method = "GET", payload?: unknown): Promise<StepResult> {
  const response = await fetch(`${baseUrl}${endpoint}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: payload ? JSON.stringify(payload) : undefined,
  });
  let body: unknown;
  try {
    body = await response.json();
  } catch {
    body = await response.text();
  }
  return { status_code: response.status, body };
}

function pretty(data: unknown) {
  return JSON.stringify(data, null, 2);
}

export default function Page() {
  const [baseUrl, setBaseUrl] = useState("http://127.0.0.1:8010");
  const [leadId, setLeadId] = useState("");
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState<StepMap>({});
  const [error, setError] = useState("");

  const derivedLeadId = useMemo(() => {
    if (leadId) {
      return leadId;
    }
    const body = results.leads_process?.body as { lead_id?: string } | undefined;
    return body?.lead_id || "";
  }, [leadId, results.leads_process]);

  const runStep = async (step: StepKey) => {
    setError("");
    try {
      let result: StepResult;
      switch (step) {
        case "health":
          result = await apiRequest(baseUrl, "/health");
          break;
        case "leads_process":
          result = await apiRequest(baseUrl, "/leads/process", "POST", DEFAULT_LEAD);
          break;
        case "outbound_email":
          result = await apiRequest(baseUrl, "/outbound/email", "POST", {
            lead_id: derivedLeadId || "lead_unknown",
            to_email: DEFAULT_LEAD.email,
            subject: "Frontend demo email",
            body: "Requesting 15-minute discovery call.",
          });
          break;
        case "outbound_sms_before_reply":
          result = await apiRequest(baseUrl, "/outbound/sms", "POST", {
            lead_id: derivedLeadId || "lead_unknown",
            to_phone: DEFAULT_LEAD.phone,
            message: "Warm follow-up before email reply",
          });
          break;
        case "inbound_email_reply":
          result = await apiRequest(baseUrl, "/webhooks/inbound", "POST", {
            lead_id: derivedLeadId || "lead_unknown",
            channel: "email",
            message: "Yes, interested in a demo this week.",
          });
          break;
        case "outbound_sms_after_reply":
          result = await apiRequest(baseUrl, "/outbound/sms", "POST", {
            lead_id: derivedLeadId || "lead_unknown",
            to_phone: DEFAULT_LEAD.phone,
            message: "Warm follow-up after reply",
          });
          break;
        case "resend_bounce":
          result = await apiRequest(baseUrl, "/webhooks/resend", "POST", {
            type: "email.bounced",
            data: { to: [DEFAULT_LEAD.email], bounce: "hard_bounce" },
          });
          break;
        case "cal_booking":
          result = await apiRequest(baseUrl, "/webhooks/cal", "POST", {
            lead_id: derivedLeadId || "lead_unknown",
            triggerEvent: "BOOKING_CREATED",
            bookingId: "bk_frontend_ui",
          });
          break;
        case "latency":
          result = await apiRequest(baseUrl, "/metrics/latency");
          break;
        case "smoke_artifact":
          result = await apiRequest("", "/api/smoke-output");
          break;
        default:
          result = { status_code: 500, body: "Unknown step" };
      }
      setResults((prev) => ({ ...prev, [step]: result }));
      if (step === "leads_process") {
        const maybeLeadId = (result.body as { lead_id?: string } | undefined)?.lead_id;
        if (maybeLeadId) {
          setLeadId(maybeLeadId);
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unexpected error");
    }
  };

  const runFullFlow = async () => {
    setRunning(true);
    const order: StepKey[] = [
      "health",
      "leads_process",
      "outbound_email",
      "outbound_sms_before_reply",
      "inbound_email_reply",
      "outbound_sms_after_reply",
      "resend_bounce",
      "cal_booking",
      "latency",
      "smoke_artifact",
    ];
    for (const step of order) {
      await runStep(step);
    }
    setRunning(false);
  };

  const stepLabels: Record<StepKey, string> = {
    health: "1) Health Check",
    leads_process: "2) Process Lead + Enrichment",
    outbound_email: "3) Outbound Email",
    outbound_sms_before_reply: "4) SMS Before Reply (Should be gated)",
    inbound_email_reply: "5) Inbound Email Reply",
    outbound_sms_after_reply: "6) SMS After Reply",
    resend_bounce: "7) Resend Bounce Webhook",
    cal_booking: "8) Cal Booking Webhook",
    latency: "9) Latency Metrics",
    smoke_artifact: "10) Load Final Smoke Artifact",
  };

  return (
    <main className="container">
      <h1 className="title">Conversion Engine Frontend Demo</h1>
      <p className="subtitle">Run complete end-to-end tests from buttons and show each result clearly during your submission demo.</p>

      <section className="panel">
        <div className="row">
          <label htmlFor="baseUrl">Backend URL:</label>
          <input
            id="baseUrl"
            value={baseUrl}
            onChange={(e) => setBaseUrl(e.target.value.trim())}
            style={{ minWidth: 280 }}
          />
          <input
            value={leadId}
            onChange={(e) => setLeadId(e.target.value.trim())}
            placeholder="Optional manual lead_id"
            style={{ minWidth: 220 }}
          />
          <button onClick={runFullFlow} disabled={running}>
            {running ? "Running full flow..." : "Run Full Flow"}
          </button>
        </div>
        {derivedLeadId ? <p>Current lead id: <code>{derivedLeadId}</code></p> : <p>Lead id appears after step 2.</p>}
        {error ? <p className="err">Error: {error}</p> : null}
      </section>

      <section className="panel">
        <div className="row">
          {(Object.keys(stepLabels) as StepKey[]).map((step) => (
            <button key={step} onClick={() => runStep(step)} disabled={running}>
              {stepLabels[step]}
            </button>
          ))}
        </div>
      </section>

      <section className="grid">
        {(Object.keys(stepLabels) as StepKey[]).map((step) => {
          const result = results[step];
          const ok = result ? result.status_code < 400 : false;
          return (
            <article className="card" key={step}>
              <h3>{stepLabels[step]}</h3>
              {!result ? (
                <p>No result yet.</p>
              ) : (
                <>
                  <p>
                    Status: <span className={ok ? "ok" : "err"}>{result.status_code}</span>
                  </p>
                  <pre>{pretty(result.body)}</pre>
                </>
              )}
            </article>
          );
        })}
      </section>
    </main>
  );
}
