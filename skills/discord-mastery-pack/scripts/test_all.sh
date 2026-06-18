#!/bin/bash
# scripts/test_all.sh - Suite Completa de Testes
# Uso: ./test_all.sh

set -euo pipefail

PASS=0
FAIL=0

test_pass() { echo -e "\033[0;32m[PASS]\033[0m $1"; ((PASS++)); }
test_fail() { echo -e "\033[0;31m[FAIL]\033[0m $1"; ((FAIL++)); }
test_info() { echo -e "\033[0;34m[INFO]\033[0m $1"; }

# API Key for testing
API_KEY="hermes-api-key-dev-2026"

echo "═══════════════════════════════════════════════════════════════"
echo "    🧪 DISCORD MASTERY PACK - TEST SUITE"
echo "═══════════════════════════════════════════════════════════════"
echo

# 1. Hermes Installation
test_info "Testing Hermes installation..."
if command -v hermes &> /dev/null; then
    VERSION=$(hermes --version 2>&1 | head -1)
    test_pass "Hermes installed: $VERSION"
else
    test_fail "Hermes not found in PATH"
fi

# 2. Gateway Service
test_info "Testing systemd service..."
if systemctl --user is-active hermes-gateway &> /dev/null; then
    test_pass "Gateway service: ACTIVE"
else
    test_fail "Gateway service: NOT RUNNING"
fi

# 3. API Server Health
test_info "Testing API Server (port 8642)..."
if curl -sf -H "Authorization: Bearer $API_KEY" http://localhost:8642/v1/health | grep -q '"status":"ok"'; then
    test_pass "API Server: HEALTHY"
else
    test_fail "API Server: UNHEALTHY or unreachable"
fi

# 4. Models Endpoint
test_info "Testing /v1/models..."
if curl -sf -H "Authorization: Bearer $API_KEY" http://localhost:8642/v1/models | grep -q "hermes-agent"; then
    test_pass "Models endpoint: OK"
else
    test_fail "Models endpoint: FAILED"
fi

# 5. Chat Completions
test_info "Testing /v1/chat/completions..."
RESPONSE=$(curl -sf -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"model":"hermes-agent","messages":[{"role":"user","content":"test"}],"max_tokens":10}' \
    http://localhost:8642/v1/chat/completions)
if echo "$RESPONSE" | grep -q "choices"; then
    test_pass "Chat completions: WORKING"
else
    test_fail "Chat completions: FAILED"
fi

# 6. Webhook Server
test_info "Testing Webhook Server (port 8644)..."
if curl -sf http://localhost:8644/health | grep -q "webhook"; then
    test_pass "Webhook Server: HEALTHY"
else
    test_fail "Webhook Server: UNHEALTHY"
fi

# 7. Channel Directory
test_info "Testing Channel Directory..."
if [[ -f ~/.hermes/channel_directory.json ]]; then
    DISCORD_CHANNELS=$(jq -r '.platforms.discord | length' ~/.hermes/channel_directory.json 2>/dev/null || echo "0")
    if [[ "$DISCORD_CHANNELS" -gt 0 ]]; then
        test_pass "Channel Directory: $DISCORD_CHANNELS Discord channels"
    else
        test_fail "Channel Directory: No Discord channels found"
    fi
else
    test_fail "Channel Directory: File not found"
fi

# 8. Webhook Subscriptions
test_info "Testing Webhook Subscriptions..."
if [[ -f ~/.hermes/webhook_subscriptions.json ]]; then
    WH_COUNT=$(jq 'length' ~/.hermes/webhook_subscriptions.json 2>/dev/null || echo "0")
    test_pass "Webhook Subscriptions: $WH_COUNT configured"
else
    test_fail "Webhook Subscriptions: None configured"
fi

# 9. Cron Jobs
test_info "Testing Cron Jobs..."
CRON_COUNT=$(hermes cron list 2>/dev/null | grep -c "Name:" || echo "0")
if [[ "$CRON_COUNT" -ge 4 ]]; then
    test_pass "Cron Jobs: $CRON_COUNT active"
else
    test_fail "Cron Jobs: Only $CRON_COUNT active (expected 4+)"
fi

# 10. Profiles
test_info "Testing Multi-Agent Profiles..."
for p in coder architect critic; do
    if [[ -d ~/.hermes/profiles/$p ]]; then
        test_pass "Profile '$p': EXISTS"
    else
        test_fail "Profile '$p': MISSING"
    fi
done

# 11. SOUL.md Files
test_info "Testing SOUL.md files..."
for p in coder architect critic; do
    if [[ -f ~/.hermes/profiles/$p/SOUL.md ]]; then
        test_pass "SOUL.md '$p': EXISTS"
    else
        test_fail "SOUL.md '$p': MISSING"
    fixture
done

# 12. Voice Dependencies
test_info "Testing Voice Dependencies..."
for dep in ffmpeg libopus0 portaudio19-dev espeak-ng; do
    if dpkg -l | grep -q "^ii  $dep "; then
        test_pass "Voice dep '$dep': INSTALLED"
    else
        test_fail "Voice dep '$dep': MISSING"
    fi
done

# 13. TTS/STT Test (quick)
test_info "Testing TTS (Edge)..."
if /usr/local/lib/hermes-agent/venv/bin/python -c "import edge_tts; print('OK')" 2>/dev/null; then
    test_pass "Edge TTS: AVAILABLE"
else
    test_fail "Edge TTS: NOT AVAILABLE"
fi

test_info "Testing STT (faster-whisper)..."
if /usr/local/lib/hermes-agent/venv/bin/python -c "import faster_whisper; print('OK')" 2>/dev/null; then
    test_pass "faster-whisper: AVAILABLE"
else
    test_fail "faster-whisper: NOT AVAILABLE"
fi

# 14. Discord Connection (via channel directory timestamp)
test_info "Testing Discord Connection Freshness..."
DIR_TIME=$(jq -r '.updated_at' ~/.hermes/channel_directory.json 2>/dev/null || echo "")
if [[ -n "$DIR_TIME" ]]; then
    # Check if updated in last 10 minutes
    DIR_EPOCH=$(date -d "$DIR_TIME" +%s 2>/dev/null || echo 0)
    NOW_EPOCH=$(date +%s)
    DIFF=$((NOW_EPOCH - DIR_EPOCH))
    if [[ $DIFF -lt 600 ]]; then
        test_pass "Discord Channel Directory: FRESH (${DIFF}s ago)"
    else
        test_fail "Discord Channel Directory: STALE (${DIFF}s ago)"
    fi
else
    test_fail "Channel Directory: No timestamp"
fi

# Summary
echo
echo "═══════════════════════════════════════════════════════════════"
echo "    📊 TEST SUMMARY: $PASS passed, $FAIL failed"
echo "═══════════════════════════════════════════════════════════════"

if [[ $FAIL -eq 0 ]]; then
    echo -e "\033[0;32m🎉 ALL TESTS PASSED!\033[0m"
    exit 0
else
    echo -e "\033[0;31m❌ SOME TESTS FAILED\033[0m"
    exit 1
fi