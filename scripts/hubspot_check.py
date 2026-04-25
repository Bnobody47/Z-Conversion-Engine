from __future__ import annotations

import json
from pathlib import Path

import httpx


def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        env[k.strip()] = v.strip().strip('"')
    return env


def main() -> None:
    env = load_env(Path(".env"))
    token = env.get("HUBSPOT_ACCESS_TOKEN", "")
    output: dict[str, object] = {"token_present": bool(token)}
    if not token:
        print(json.dumps(output, indent=2))
        return

    headers = {"Authorization": f"Bearer {token}"}
    with httpx.Client(timeout=20) as client:
        r_contacts = client.get("https://api.hubapi.com/crm/v3/objects/contacts?limit=1", headers=headers)
        output["contacts_status"] = r_contacts.status_code
        output["contacts_snippet"] = r_contacts.text[:240]

        r_token = client.get(f"https://api.hubapi.com/oauth/v1/access-tokens/{token}")
        output["token_info_status"] = r_token.status_code
        output["token_info"] = r_token.json() if r_token.status_code == 200 else {"body": r_token.text[:240]}

        r_me = client.get("https://api.hubapi.com/integrations/v1/me", headers=headers)
        output["me_status"] = r_me.status_code
        output["me_info"] = r_me.json() if r_me.status_code == 200 else {"body": r_me.text[:240]}

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
