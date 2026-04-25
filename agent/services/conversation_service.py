from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ChannelDecision:
    stage: str
    allow_sms_send: bool
    cal_link: str
    reason: str


def choose_channel_stage(has_replied_email: bool, prefers_sms: bool) -> str:
    if has_replied_email and prefers_sms:
        return "sms_warm_followup"
    return "email_primary"


def decide_handoff_state(
    *,
    lead_id: str,
    has_replied_email: bool,
    prefers_sms: bool,
    cal_base_url: str = "https://cal.com/tenacious/discovery",
) -> ChannelDecision:
    """
    Centralized handoff/state-machine logic to avoid channel routing decisions
    being scattered across handlers.
    """
    stage = choose_channel_stage(has_replied_email=has_replied_email, prefers_sms=prefers_sms)
    cal_link = f"{cal_base_url}?lead_id={lead_id}"
    if stage == "sms_warm_followup":
        return ChannelDecision(stage=stage, allow_sms_send=True, cal_link=cal_link, reason="email_reply_present")
    return ChannelDecision(stage=stage, allow_sms_send=False, cal_link=cal_link, reason="email_first_required")
