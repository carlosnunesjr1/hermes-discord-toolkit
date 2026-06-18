#!/bin/bash
# =============================================================================
# Discord Forum Idea Incubator - Setup Script
# Configura toda a infraestrutura necessária para a incubadora funcionar
# =============================================================================

set -euo pipefail

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }
info() { echo -e "${BLUE}[INFO]${NC} $*"; }

# =============================================================================
# CONFIGURAÇÃO - AJUSTE ESTES VALORES
# =============================================================================

DISCORD_BOT_TOKEN="${DISCORD_BOT_TOKEN:-}"
DISCORD_GUILD_ID="${DISCORD_GUILD_ID:-1516397584942370836}"
HERMES_PROFILE="${HERMES_PROFILE:-default}"
HERMES_CLI="${HERMES_CLI:-hermes}"

# Canal IDs - PREENCHA COM OS IDs REAIS DO SEU SERVIDOR
# Use: hermes chat -q "Liste canais" --toolsets discord
# Ou no Discord: Developer Mode → Right-click channel → Copy ID
FORUM_RAW=""           # #ideias-brutas
FORUM_ANALYSIS=""      # #em-análise
FORUM_EXPERIMENTS=""   # #experimentos
FORUM_READY=""         # #prontas-para-produção
FORUM_ARCHIVE=""       # #arquivadas
FORUM_TEMPLATES=""     # #templates

# =============================================================================
# FUNÇÕES
# =============================================================================

check_requirements() {
    log "Verificando requisitos..."
    
    if [[ -z "$DISCORD_BOT_TOKEN" ]]; then
        error "DISCORD_BOT_TOKEN não configurado. Export: export DISCORD_BOT_TOKEN='seu_token'"
        exit 1
    fi
    
    if ! command -v "$HERMES_CLI" &> /dev/null; then
        error "Hermes CLI não encontrado. Instale: pip install hermes-agent[all]"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        error "Python 3 não encontrado"
        exit 1
    fi
    
    # Verificar dependências Python
    python3 -c "import aiohttp" 2>/dev/null || {
        warn "aiohttp não instalado. Instalando..."
        pip install aiohttp
    }
    
    log "Requisitos OK"
}

create_forum_channels() {
    log "Criando canais de fórum no Discord (via API)..."
    info "Nota: Canais de fórum devem ser criados manualmente no Discord ou via bot com permissão MANAGE_CHANNELS"
    info "Estrutura recomendada:"
    info "  📁 INCUBADORA (Category)"
    info "  ├── 💡 #ideias-brutas"
    info "  ├── 🔬 #em-análise"
    info "  ├── ⚗️ #experimentos"
    info "  ├── ✅ #prontas-para-produção"
    info "  ├── 📦 #arquivadas"
    info "  └── 🗂️ #templates"
    echo
    read -p "Pressione Enter após criar os canais e obter os IDs..."
}

collect_channel_ids() {
    log "Coletando Channel IDs..."
    
    if [[ -z "$FORUM_RAW" ]]; then
        read -p "Channel ID #ideias-brutas: " FORUM_RAW
    fi
    if [[ -z "$FORUM_ANALYSIS" ]]; then
        read -p "Channel ID #em-análise: " FORUM_ANALYSIS
    fi
    if [[ -z "$FORUM_EXPERIMENTS" ]]; then
        read -p "Channel ID #experimentos: " FORUM_EXPERIMENTS
    fi
    if [[ -z "$FORUM_READY" ]]; then
        read -p "Channel ID #prontas-para-produção: " FORUM_READY
    fi
    if [[ -z "$FORUM_ARCHIVE" ]]; then
        read -p "Channel ID #arquivadas: " FORUM_ARCHIVE
    fi
    if [[ -z "$FORUM_TEMPLATES" ]]; then
        read -p "Channel ID #templates: " FORUM_TEMPLATES
    fi
    
    # Validar
    for var in FORUM_RAW FORUM_ANALYSIS FORUM_EXPERIMENTS FORUM_READY FORUM_ARCHIVE FORUM_TEMPLATES; do
        if [[ -z "${!var}" ]]; then
            error "$var não preenchido"
            exit 1
        fi
    done
}

create_tags_in_forum() {
    log "Criando tags nos canais de fórum..."
    info "Tags necessárias por canal:"
    echo
    info "TODOS OS CANAIS:"
    info "  status: capturada, em-debate, validando, aprovada, arquivada, feita"
    info "  prioridade: P1-urgente, P2-alta, P3-normal, P4-baixa, P5-backlog"
    info "  tipo: feature, bug, tech-debt, pesquisa, processo, infra"
    info "  esforco: XS, S, M, L, XL, desconhecido"
    info "  dominio: career, pim, router, infra, hermes, geral"
    echo
    info "Crie as tags manualmente em cada canal de fórum:"
    info "  1. Clique no canal → 'Gerenciar Tags' → 'Criar Tag'"
    info "  2. Nome exato conforme acima (case-sensitive para matching)"
    info "  3. Emoji opcional para visual"
    echo
    read -p "Pressione Enter após criar todas as tags..."
}

setup_templates() {
    log "Criando templates no canal #templates..."
    
    # Os templates são threads no canal #templates
    # Criaremos via script Python
    cat > /tmp/create_templates.py << 'PYEOF'
import asyncio
import os
import sys
sys.path.insert(0, os.path.expanduser("~/.hermes/skills/devops/discord-forum-idea-incubator/scripts"))

from forum_manager import DiscordForumManager

async def main():
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    guild_id = os.getenv("DISCORD_GUILD_ID", "1516397584942370836")
    templates_channel = os.getenv("FORUM_TEMPLATES")
    
    if not bot_token or not templates_channel:
        print("Token ou channel não configurados")
        return
    
    async with DiscordForumManager(bot_token, guild_id) as mgr:
        await mgr.get_available_tags(templates_channel)
        
        templates = [
            {
                "name": "Template: Nova Feature",
                "content": """## 💡 Ideia: {{title}}

### Contexto
{{contexto}}

### Hipótese de Valor
{{hipotese}}

### Critérios de Sucesso
- [ ] Critério 1
- [ ] Critério 2

### Riscos Conhecidos
- Risco 1: Mitigação
- Risco 2: Mitigação

### Dependências
- Sistema X, API Y

### Estimativa Rápida
- Esforço: {{esforco}}
- Complexidade técnica: {{complexidade}}
- Tempo para MVP: {{mvp}}

---

### 💬 Discussão
<!---thread-messages-->

### ✅ Decisão
- Status: capturada
- Decisor: @{{author}}
- Data: {{date}}
- Próximo passo: Aguardando triagem
""",
            },
            {
                "name": "Template: Tech Debt / Refatoração",
                "content": """## 🔧 Tech Debt: {{title}}

### O que está errado
{{problema}}

### Impacto Atual
- Performance: {{perf}}
- Manutenibilidade: {{maint}}
- Bugs recorrentes: {{bugs}}

### Solução Proposta
{{solucao}}

### Escopo
- Arquivos/módulos: {{arquivos}}
- Testes necessários: {{testes}}
- Migration strategy: {{migration}}

### Esforço Estimado
{{esforco}}

---

### 💬 Discussão
<!---thread-messages-->

### ✅ Decisão
- Status: capturada
- Decisor: @{{author}}
- Data: {{date}}
- Próximo passo: Aguardando triagem
""",
            },
            {
                "name": "Template: Spike / Pesquisa Técnica",
                "content": """## ⚗️ Spike: {{title}}

### Pergunta Técnica
{{pergunta}}

### Hipótese
{{hipotese}}

### Critérios de Validação (Pass/Fail)
- [ ] Critério 1
- [ ] Critério 2

### Timebox
{{timebox}}

### Recursos
- Docs: {{docs}}
- Código existente: {{codigo}}
- Pessoas: {{pessoas}}

---

### 💬 Discussão
<!---thread-messages-->

### ✅ Decisão
- Status: capturada
- Decisor: @{{author}}
- Data: {{date}}
- Próximo passo: Aguardando triagem
""",
            },
        ]
        
        for tmpl in templates:
            try:
                # Verificar se já existe
                existing = await mgr.list_threads(templates_channel, archived=True, limit=50)
                if any(t.name == tmpl["name"] for t in existing):
                    print(f"  ⏭️  {tmpl['name']} já existe")
                    continue
                
                thread = await mgr.create_thread(
                    channel_id=templates_channel,
                    name=tmpl["name"],
                    content=tmpl["content"],
                    applied_tags=[],  # Templates não precisam de tags de status
                )
                print(f"  ✅ {tmpl['name']} criado (ID: {thread.id})")
            except Exception as e:
                print(f"  ❌ {tmpl['name']}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
PYEOF
    
    DISCORD_BOT_TOKEN="$DISCORD_BOT_TOKEN" \
    DISCORD_GUILD_ID="$DISCORD_GUILD_ID" \
    FORUM_TEMPLATES="$FORUM_TEMPLATES" \
    python3 /tmp/create_templates.py
    
    log "Templates criados"
}

configure_hermes_cron() {
    log "Configurando Cron Jobs no Hermes..."
    
    # Triagem semanal (segunda 9h)
    $HERMES_CLI cron create "0 9 * * 1" \
        --name "incubator-weekly-triage" \
        --prompt "Execute triagem semanal da incubadora: liste threads em 'em-debate' no canal $FORUM_ANALYSIS, aplique critérios de prioridade (P1=OKR+esforço≤M, P2=OKR+esforço≥L, P3=não-OKR+alto valor/baixo esforço), atualize tags, poste resumo no canal geral." \
        --skills "discord-forum-idea-incubator" \
        --deliver "origin" \
        || warn "Cron triagem já existe ou falhou"
    
    # Resumo diário (18h)
    $HERMES_CLI cron create "0 18 * * *" \
        --name "incubator-daily-summary" \
        --prompt "Gere resumo diário da incubadora: novas ideias capturadas, threads movidas entre canais, spikes concluídos, tasks Kanban criadas. Poste no canal Home." \
        --skills "discord-forum-idea-incubator" \
        --deliver "origin" \
        || warn "Cron resumo já existe ou falhou"
    
    # Reconciliação diária (meia-noite)
    $HERMES_CLI cron create "0 0 * * *" \
        --name "incubator-daily-reconciliation" \
        --prompt "Execute reconciliação diária Forum ↔ Kanban: compare threads nos canais de fórum com tasks no board incubator, reporte discrepâncias (threads aprovadas sem task, tasks órfãs, status dessincronizados)." \
        --skills "discord-forum-idea-incubator" \
        --deliver "origin" \
        || warn "Cron reconciliação já existe ou falhou"
    
    log "Cron jobs configurados"
    $HERMES_CLI cron list
}

configure_hermes_gateway() {
    log "Configurando Hermes Gateway para Discord Forum..."
    
    # Verificar config atual
    config_file="$HOME/.hermes/config.yaml"
    
    if grep -q "forum_incubator:" "$config_file"; then
        warn "Config forum_incubator já existe em config.yaml"
        return
    fi
    
    # Adicionar config (append antes da seção final)
    cat >> "$config_file" << YAMLEOF

# Discord Forum Incubator Configuration
discord:
  forum_incubator:
    enabled: true
    category_id: "INCUBADORA_CATEGORY_ID"  # Opcional: ID da categoria pai
    channels:
      raw: "$FORUM_RAW"
      analysis: "$FORUM_ANALYSIS"
      experiments: "$FORUM_EXPERIMENTS"
      ready: "$FORUM_READY"
      archive: "$FORUM_ARCHIVE"
      templates: "$FORUM_TEMPLATES"
    auto_thread_from_voice: true
    auto_thread_from_reaction: true
    reaction_triggers: ["🎯", "💡", "🚀"]
    idea_prefix: "!ideia"

kanban:
  boards:
    incubator:
      name: "incubator"
      auto_create_from_forum: true
      default_assignee: "default"
      skill_mapping:
        career: "cn-tech-ecosystem"
        pim: "cn-tech-ecosystem"
        router: "cn-tech-ecosystem"
        infra: "cn-tech-ecosystem"
        hermes: "hermes-agent"
        geral: "system-architect-audit"

cron:
  jobs:
    - name: "incubator-weekly-triage"
      schedule: "0 9 * * 1"
      prompt: "Execute triagem semanal da incubadora..."
      skills: ["discord-forum-idea-incubator"]
    - name: "incubator-daily-summary"
      schedule: "0 18 * * *"
      prompt: "Resumo diário da incubadora..."
      skills: ["discord-forum-idea-incubator"]
    - name: "incubator-daily-reconciliation"
      schedule: "0 0 * * *"
      prompt: "Reconciliação diária Forum ↔ Kanban..."
      skills: ["discord-forum-idea-incubator"]
YAMLEOF
    
    log "Configuração adicionada a ~/.hermes/config.yaml"
    warn "Reinicie o gateway: sudo systemctl restart hermes-gateway"
}

test_e2e() {
    log "Testando pipeline E2E..."
    
    # Teste 1: Criar thread via script
    cat > /tmp/test_e2e.py << 'PYEOF'
import asyncio
import os
import sys
sys.path.insert(0, os.path.expanduser("~/.hermes/skills/devops/discord-forum-idea-incubator/scripts"))

from forum_manager import DiscordForumManager
from idea_processor import IdeaProcessor, create_raw_idea_from_discord_message
from kanban_bridge import KanbanBridge

async def main():
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    guild_id = os.getenv("DISCORD_GUILD_ID", "1516397584942370836")
    raw_channel = os.getenv("FORUM_RAW")
    
    if not bot_token or not raw_channel:
        print("Config incompleta")
        return
    
    print("🔧 Teste 1: Idea Processor")
    processor = IdeaProcessor()
    raw = create_raw_idea_from_discord_message({
        "content": "Precisamos adicionar cache Redis no LLM Router para reduzir latência. Prioridade alta, tipo tech-debt, domínio router.",
        "author": {"id": "123", "username": "TestUser"},
        "channel_id": raw_channel,
        "id": "test-msg-1",
        "timestamp": "2026-06-17T10:00:00Z",
    })
    idea = processor.process_raw_idea(raw)
    print(f"  Título: {idea.title}")
    print(f"  Tipo: {idea.tipo.value}")
    print(f"  Prioridade: {idea.prioridade.value}")
    print(f"  Esforço: {idea.esforco.value}")
    print(f"  Domínio: {idea.dominio.value}")
    
    print("\n🔧 Teste 2: Forum Manager")
    async with DiscordForumManager(bot_token, guild_id) as mgr:
        await mgr.get_available_tags(raw_channel)
        tags = mgr.build_applied_tags(
            channel_id=raw_channel,
            status=idea.status,
            prioridade=idea.prioridade.value,
            tipo=idea.tipo.value,
            esforco=idea.esforco.value,
            dominio=idea.dominio.value,
        )
        print(f"  Tags resolvidas: {tags}")
        
        # Não criar thread real no teste
        print("  (Pulando criação real de thread)")
    
    print("\n🔧 Teste 3: Kanban Bridge")
    bridge = KanbanBridge()
    tasks = bridge.list_tasks(limit=5)
    print(f"  Tasks atuais no board: {len(tasks)}")
    for t in tasks:
        print(f"    {t.id[:8]} | P{t.priority} | {t.status} | {t.title[:40]}")
    
    print("\n✅ Testes básicos passaram!")

if __name__ == "__main__":
    asyncio.run(main())
PYEOF
    
    DISCORD_BOT_TOKEN="$DISCORD_BOT_TOKEN" \
    DISCORD_GUILD_ID="$DISCORD_GUILD_ID" \
    FORUM_RAW="$FORUM_RAW" \
    python3 /tmp/test_e2e.py
    
    log "Teste E2E concluído"
}

generate_env_file() {
    log "Gerando arquivo .env para a incubadora..."
    
    cat > "$HOME/.hermes/incubator.env" << ENVEOF
# Discord Forum Idea Incubator - Environment Variables
# Source this file or add to ~/.hermes/.env

DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN
DISCORD_GUILD_ID=$DISCORD_GUILD_ID

# Forum Channel IDs
FORUM_RAW=$FORUM_RAW
FORUM_ANALYSIS=$FORUM_ANALYSIS
FORUM_EXPERIMENTS=$FORUM_EXPERIMENTS
FORUM_READY=$FORUM_READY
FORUM_ARCHIVE=$FORUM_ARCHIVE
FORUM_TEMPLATES=$FORUM_TEMPLATES

# Hermes
HERMES_PROFILE=$HERMES_PROFILE
HERMES_CLI=$HERMES_CLI
ENVEOF
    
    log "Arquivo criado: ~/.hermes/incubator.env"
    info "Adicione ao ~/.hermes/.env ou use: source ~/.hermes/incubator.env"
}

print_summary() {
    echo
    echo "================================================================="
    echo "  🎉 DISCORD FORUM IDEA INCUBATOR - SETUP CONCLUÍDO"
    echo "================================================================="
    echo
    echo "Próximos passos manuais:"
    echo "  1. source ~/.hermes/incubator.env"
    echo "  2. sudo systemctl restart hermes-gateway"
    echo "  3. Teste no Discord:"
    echo "     - Grave áudio no canal #ideias-brutas"
    echo "     - Digite: !ideia teste"
    echo "     - Reaja com 🎯 em qualquer mensagem"
    echo "     - Use: /ideia \"Nova feature\" --tipo feature --prioridade P3"
    echo "  4. Verifique cron jobs: hermes cron list"
    echo "  5. Monitore logs: journalctl -u hermes-gateway -f"
    echo
    echo "Comandos úteis:"
    echo "  hermes cron run incubator-weekly-triage    # Executar triagem agora"
    echo "  hermes cron run incubator-daily-summary    # Gerar resumo agora"
    echo "  hermes kanban list                         # Ver tasks Kanban"
    echo "  hermes kanban dispatch --dry-run           # Ver o que seria dispatchado"
    echo
    echo "Arquivos criados:"
    echo "  ~/.hermes/skills/devops/discord-forum-idea-incubator/"
    echo "  ~/.hermes/incubator.env"
    echo "  ~/.hermes/config.yaml (atualizado)"
    echo
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    echo "🚀 Discord Forum Idea Incubator - Setup"
    echo "================================================================="
    echo
    
    check_requirements
    
    # Se IDs não passados como env, perguntar
    if [[ -z "$FORUM_RAW" ]]; then
        create_forum_channels
        collect_channel_ids
    fi
    
    create_tags_in_forum
    setup_templates
    configure_hermes_cron
    configure_hermes_gateway
    generate_env_file
    test_e2e
    
    print_summary
}

main "$@"