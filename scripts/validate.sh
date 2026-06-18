#!/bin/bash
# validate.sh — Validate templates and configuration
# Run in CI and before commit

set -euo pipefail

TEMPLATE_DIR="$(dirname "$0")/../templates"
SCRIPT_DIR="$(dirname "$0")"
RENDERED_DIR="$(dirname "$0")/../rendered"

echo "🔍 Validating templates..."

# Check for unresolved placeholders in rendered output (should have none)
echo "Checking rendered output for unresolved placeholders..."
if [[ -d "$RENDERED_DIR" ]] && grep -r "{{[A-Z_]\+}}" "$RENDERED_DIR" 2>/dev/null; then
    echo "❌ Found unresolved placeholders in rendered output:"
    grep -r "{{[A-Z_]\+}}" "$RENDERED_DIR"
    exit 1
fi
echo "  ✅ No unresolved placeholders in rendered output (or not rendered yet)"

# Check .template files HAVE placeholders (they should)
for template in "$TEMPLATE_DIR"/**/*.template; do
    if [[ -f "$template" ]] && ! grep -q "{{" "$template"; then
        echo "❌ Template missing placeholders: $template"
        exit 1
    fi
done
echo "  ✅ All .template files have placeholders"

# Check .example files have placeholders (they should)
if ! grep -q "{{" "$TEMPLATE_DIR/env/.env.example"; then
    echo "❌ .env.example missing placeholders"
    exit 1
fi
echo "  ✅ .env.example has placeholders"

# Validate shell scripts with shellcheck
echo "Checking shell scripts..."
for script in "$SCRIPT_DIR"/*.sh; do
    if command -v shellcheck >/dev/null 2>&1; then
        shellcheck "$script" || exit 1
    else
        echo "  ⚠️ shellcheck not installed, skipping $script"
    fi
done
echo "  ✅ Shell scripts valid"

# Validate systemd unit syntax (basic check)
echo "Checking systemd units..."
for unit in "$TEMPLATE_DIR/systemd/"*.service; do
    # Basic syntax check: required sections exist
    if ! grep -q "\[Unit\]" "$unit" || ! grep -q "\[Service\]" "$unit" || ! grep -q "\[Install\]" "$unit"; then
        echo "❌ Missing required section in $unit"
        exit 1
    fi
    if ! grep -q "ExecStart" "$unit"; then
        echo "❌ Missing ExecStart in $unit"
        exit 1
    fi
done
echo "  ✅ Systemd units have required sections"

# Check required files exist
required=(
    "README.md"
    "LICENSE"
    ".gitignore"
    "templates/env/.env.example"
    "templates/systemd/hermes-gateway@.service"
    "templates/systemd/hermes-workspace@.service"
    "templates/caddy/Caddyfile.template"
    "scripts/setup.sh"
    "scripts/render-templates.sh"
    "scripts/deploy.sh"
)

for f in "${required[@]}"; do
    if [[ ! -f "$(dirname "$0")/../$f" ]]; then
        echo "❌ Missing required file: $f"
        exit 1
    fi
done
echo "  ✅ All required files present"

echo ""
echo "✅ All validations passed"