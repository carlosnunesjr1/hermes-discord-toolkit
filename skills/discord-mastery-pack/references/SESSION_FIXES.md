# Session Fixes & Learnings
## Discord Mastery Pack - Session 2026-06-16

---

## Caddy Config Pitfall: Nested Site Blocks

**Problem**: Accidentally created nested `menusummo.com.br:80` blocks inside the main site definition, causing:
```
Error: adapting config using caddyfile: /etc/caddy/Caddyfile:69: unrecognized directive: menusummo.com.br:80,
```

**Root Cause**: The awk replacement inserted the entire corrected block INCLUDING the outer `menusummo.com.br:80, www.menusummo.com.br:80 {` inside the existing one, creating double nesting.

**Fix**: Restore from backup (`/etc/caddy/Caddyfile.bak`), then use awk that replaces the ENTIRE section from opening brace to matching closing brace.

```bash
# Correct approach - replace entire section with brace counting
sudo awk '
BEGIN { in_section = 0; brace_count = 0; replaced = 0 }
/^menusummo\.com\.br:80, www\.menusummo\.com\.br:80 \{/ && !in_section {
    in_section = 1
    brace_count = 1
    while ((getline line < "/tmp/main_section.txt") > 0) print line
    close("/tmp/main_section.txt")
    next
}
in_section {
    brace_count += gsub(/{/, "{")
    brace_count -= gsub(/}/, "}")
    if (brace_count == 0) {
        in_section = 0
        next
    }
    next
}
{ print }
' /etc/caddy/Caddyfile > /tmp/caddy_new && sudo mv /tmp/caddy_new /etc/caddy/Caddyfile
```

**Prevention**: Always backup before Caddy edits (`sudo cp /etc/caddy/Caddyfile /etc/caddy/Caddyfile.bak`). Use `caddy fmt --overwrite` to validate before reload.

---

## Basic Auth Rotation: admin/admin123 → bcrypt scrypt

**Process**:

1. Generate new secret:
```bash
openssl rand -base64 32
# Output: xBj/yT2pSdiP8QdkHTL7LfDknzgFu6XgjwBElFVXpbg=
```

2. Hash with bcrypt (12 rounds):
```bash
python3 -c "
import bcrypt
password = 'xBj/yT2pSdiP8QdkHTL7LfDknzgFu6XgjwBElFVXpbg='
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
print(f'admin:{hashed.decode()}')"
# Output: admin:$2b$12$9vMB7vOqDMp6UTLcuNx.cuOlN5VKlDluVC8krZ5Mu8li0Wo81LQP6
```

3. Update Caddyfile (single occurrence in `@sec_api` block):
```bash
sudo sed -i 's|\$2b\$12\$OLD_HASH|\$2b\$12\$NEW_HASH|' /etc/caddy/Caddyfile
```

4. Validate and reload:
```bash
sudo caddy fmt /etc/caddy/Caddyfile --overwrite && sudo systemctl reload caddy
```

**Verification**: Test with curl using basic auth:
```bash
curl -u admin:NEW_SECRET https://menusummo.com.br/secrets/
```

---

## Service Binding Verification (FASE 1.1)

**Command**:
```bash
ss -tlnp | grep -E ':(2019|9121|9130|8799|9119|3002|9120|9125|8642|8644|9140)' | grep -v 127.0.0.1
```

**Expected**: Empty output (all internal services bound to 127.0.0.1 only)

**Result**: ✅ All services correctly bound to 127.0.0.1:
- 8642 (Hermes API Server)
- 8644 (Webhook Server)
- 9119 (Dashboard)
- 9120 (Control)
- 9121 (PIM)
- 9130 (Central)
- 9140 (Secrets API)
- 2019 (Career Hub)

---

## GitHub Webhook HMAC Signature Generation

**Critical**: Use the exact secret from `hermes webhook list` (Secret column).

```python
import hmac, hashlib, json

secret = 'xiVxJ9Mys5HMvfOKGYwTWmYl25kY8ZHM1nGukz6Bj5M'  # From hermes webhook list
payload = {'action': 'opened', 'pull_request': {...}}
body = json.dumps(payload, separators=(',', ':')).encode()
sig = 'sha256=' + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
```

**Test**:
```bash
curl -X POST http://localhost:8644/webhooks/github-pr-review \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  -H "X-Hub-Signature-256: sha256=GENERATED_SIG" \
  -d '{"action":"opened",...}'
# Expected: {"status": "accepted", "route": "github-pr-review", ...}
```

---

## Launchpad Integration at Root Domain

**Problem**: Launchpad needed to be accessible at `https://menusummo.com.br/` (root) not a subdomain.

**Solution**: Add `handle` block at end of main site config (catches all unmatched paths):

```caddy
menusummo.com.br:80, www.menusummo.com.br:80 {
    # ... existing handles ...
    
    # Launchpad at root - serves the Discord Mastery Pack UI
    handle {
        root * /var/www/launchpad
        file_server
    }
}
```

**Note**: Place AFTER all specific `@gateway_paths`, `@workspace_paths`, etc. so they take precedence. The fallback `handle` serves launchpad for `/` and any unmatched paths.

---

## Profile Setup for Multi-Agent

**Process** (interactive, requires API keys):
```bash
coder setup      # Inherits or sets API keys
architect setup  # Inherits or sets API keys
critic setup     # Inherits or sets API keys
```

Each creates `~/.hermes/profiles/<name>/` with own config and SOUL.md persona copied from skill references.

---

## MCP Deployment Sequence

```bash
# Each requires interactive credential input
hermes mcp add notion     # NOTION_API_KEY, optional DB IDs
hermes mcp add github     # GITHUB_TOKEN (classic, scopes: repo, admin:repo_hook, read:org, user)
hermes mcp add linear     # LINEAR_API_KEY
hermes mcp add obsidian   # OBSIDIAN_API_KEY (plugin Local REST API)
systemctl --user restart hermes-gateway
```

**Obsidian prerequisite**: Install "Local REST API" plugin in Obsidian (port 27123, API key enabled).

---

## DNS & Webhook Finalization (Manual)

| Action | Command/Location |
|--------|------------------|
| Cloudflare DNS | dash.cloudflare.com → menusummo.com.br → DNS → Add: A, webhook, 163.176.219.122, Proxy ON |
| GitHub Webhook | repo Settings → Webhooks → Add: `https://webhook.menusummo.com.br/webhooks/github-pr-review`, Secret from `hermes webhook list` |
| Profile Setup | `coder setup`, `architect setup`, `critic setup` (interactive) |
| MCP Deploy | `hermes mcp add notion|github|linear|obsidian` then restart gateway |