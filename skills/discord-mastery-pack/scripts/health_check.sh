#!/bin/bash
# scripts/health_check.sh - VPS Health Check para Cron
# Usado pelo cron "VPS Health Monitor" (--no-agent mode)

# Thresholds
CPU_THRESHOLD=80
MEM_THRESHOLD=85
DISK_THRESHOLD=90

# Coletar métricas
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print 100 - $8}' | cut -d. -f1)
MEM_USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
UPTIME=$(uptime -p)
LOAD=$(uptime | awk -F'load average:' '{print $2}')

ALERTS=()

# Verificar CPU
if [[ $CPU_USAGE -gt $CPU_THRESHOLD ]]; then
    ALERTS+=("🔴 **CPU CRÍTICO**: ${CPU_USAGE}% (limite: ${CPU_THRESHOLD}%)")
fi

# Verificar Memória
if [[ $MEM_USAGE -gt $MEM_THRESHOLD ]]; then
    ALERTS+=("🔴 **RAM CRÍTICA**: ${MEM_USAGE}% (limite: ${MEM_THRESHOLD}%)")
fi

# Verificar Disco
if [[ $DISK_USAGE -gt $DISK_THRESHOLD ]]; then
    ALERTS+=("🔴 **DISCO CRÍTICO**: ${DISK_USAGE}% (limite: ${DISK_THRESHOLD}%)")
fi

# Se há alertas, output JSON para Discord
if [[ ${#ALERTS[@]} -gt 0 ]]; then
    cat << EOF
{
  "content": "⚠️ **ALERTA VPS - $(hostname)**",
  "embeds": [{
    "title": "Health Check - $(date '+%d/%m/%Y %H:%M')",
    "color": 15158332,
    "fields": [
      {"name": "CPU", "value": "${CPU_USAGE}%", "inline": true},
      {"name": "RAM", "value": "${MEM_USAGE}%", "inline": true},
      {"name": "Disco", "value": "${DISK_USAGE}%", "inline": true},
      {"name": "Uptime", "value": "${UPTIME}", "inline": true},
      {"name": "Load Avg", "value": "${LOAD}", "inline": true},
      {"name": "Alertas", "value": "$(printf '%s\n' "${ALERTS[@]}")", "inline": false}
    ]
  }]
}
EOF
else
    # Silencioso - sem output = sem mensagem no Discord
    exit 0
fi