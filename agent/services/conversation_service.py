from __future__ import annotations


def choose_channel_stage(has_replied_email: bool, prefers_sms: bool) -> str:
    if has_replied_email and prefers_sms:
        return "sms_warm_followup"
    return "email_primary"
