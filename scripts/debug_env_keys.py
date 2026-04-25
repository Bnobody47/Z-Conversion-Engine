from pathlib import Path


def main() -> None:
    p = Path(".env")
    print("cwd_env_exists", p.exists(), "path", p.resolve())
    env = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        env[k.strip()] = v.strip().strip('"')
    print("keys", sorted(env.keys()))
    token = env.get("HUBSPOT_ACCESS_TOKEN", "")
    print("token_len", len(token))
    print("token_prefix", token[:8] if token else "")
    raw_lines = p.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(raw_lines, start=1):
        if "HUBSPOT_ACCESS_TOKEN" in line:
            print("raw_line_index", idx, "raw_line_len", len(line))
            if "=" in line:
                print("raw_value_len", len(line.split("=", 1)[1]))


if __name__ == "__main__":
    main()
