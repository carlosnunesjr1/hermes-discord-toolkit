#!/usr/bin/env python3
"""
Incubator Orchestrator - Orquestrador principal da Incubadora de Ideias.
Integra: Discord Forum + Idea Processor + Kanban Bridge.
Parte da Hermes Incubadora de Ideias.
"""

import os
import json
import asyncio
import logging
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

# Importar módulos locais
import sys
sys.path.insert(0, str(Path(__file__).parent))

from forum_manager import DiscordForumManager, create_idea_thread
from idea_processor import (
    IdeaProcessor, RawIdea, StructuredIdea,
    IdeaSource, IdeaType, Priority, Effort, Domain,
    create_raw_idea_from_discord_message,
    create_raw_idea_from_voice,
    create_raw_idea_from_reaction,
)
from kanban_bridge import KanbanBridge, SyncResult


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class IncubatorConfig:
    """Configuração da Incubadora."""
    # Discord
    bot_token: str
    guild_id: str
    forum_channels: Dict[str, str]  # name -> channel_id
    
    # Kanban
    kanban_board: str = "incubator"
    default_assignee: str = "default"
    hermes_cli: str = "hermes"
    hermes_profile: str = "default"
    
    # Processing
    auto_thread_from_voice: bool = True
    auto_thread_from_reaction: bool = True
    reaction_triggers: List[str] = None
    idea_prefix: str = "!ideia"
    
    # Triage
    triage_schedule: str = "0 9 * * 1"  # Segunda 9h
    max_active_debates: int = 10
    debate_timeout_days: int = 7
    
    def __post_init__(self):
        if self.reaction_triggers is None:
            self.reaction_triggers = ["🎯", "💡", "🚀"]


class IncubatorOrchestrator:
    """Orquestrador principal da Incubadora de Ideias."""
    
    def __init__(self, config: IncubatorConfig):
        self.config = config
        self.processor = IdeaProcessor()
        self.bridge = KanbanBridge(
            hermes_cli=config.hermes_cli,
            kanban_board=config.kanban_board,
            default_assignee=config.default_assignee,
            profile=config.hermes_profile,
        )
        self.forum_manager: Optional[DiscordForumManager] = None
    
    async def __aenter__(self):
        self.forum_manager = DiscordForumManager(
            bot_token=self.config.bot_token,
            guild_id=self.config.guild_id,
        )
        await self.forum_manager.__aenter__()
        # Pré-carregar tags de todos os canais
        for channel_id in self.config.forum_channels.values():
            await self.forum_manager.get_available_tags(channel_id)
        return self
    
    async def __aexit__(self, *args):
        if self.forum_manager:
            await self.forum_manager.__aexit__(*args)
    
    # ============== ENTRY POINTS ==============
    
    async def handle_discord_message(self, message: dict) -> Optional[SyncResult]:
        """Processa mensagem do Discord (webhook/gateway)."""
        content = message.get("content", "").strip()
        if not content:
            return None
        
        channel_id = message.get("channel_id")
        
        # Verificar se é comando /ideia
        if content.startswith(self.config.idea_prefix):
            return await self._handle_slash_idea(message)
        
        # Verificar se é no canal de ideias brutas
        raw_channel_id = self.config.forum_channels.get("raw")
        if channel_id == raw_channel_id:
            return await self._handle_raw_idea(message)
        
        return None
    
    async def handle_voice_message(
        self,
        transcript: str,
        author_id: str,
        author_name: str,
        channel_id: str,
        message_id: str,
    ) -> Optional[SyncResult]:
        """Processa mensagem de voz transcrita."""
        if not self.config.auto_thread_from_voice:
            return None
        
        raw_channel_id = self.config.forum_channels.get("raw")
        if channel_id != raw_channel_id:
            return None
        
        raw = create_raw_idea_from_voice(
            transcript=transcript,
            author_id=author_id,
            author_name=author_name,
            channel_id=channel_id,
            message_id=message_id,
        )
        
        return await self._process_and_create_thread(raw)
    
    async def handle_reaction(
        self,
        message: dict,
        emoji: str,
        reactor_id: str,
        reactor_name: str,
    ) -> Optional[SyncResult]:
        """Processa reação em mensagem."""
        if not self.config.auto_thread_from_reaction:
            return None
        
        if emoji not in self.config.reaction_triggers:
            return None
        
        raw = create_raw_idea_from_reaction(message, emoji, reactor_id, reactor_name)
        return await self._process_and_create_thread(raw)
    
    # ============== HANDLERS INTERNOS ==============
    
    async def _handle_slash_idea(self, message: dict) -> SyncResult:
        """Processa comando /ideia."""
        content = message.get("content", "")
        overrides = self.processor.parse_slash_command(content)
        
        if not overrides:
            return SyncResult(
                success=False,
                thread_id="",
                action="slash_parse_failed",
                error="Formato inválido. Use: /ideia \"titulo\" --tipo feature --prioridade P3 --dominio career",
            )
        
        # Extrair título e criar ideia base
        title = overrides.pop("title")
        raw = create_raw_idea_from_discord_message(message)
        raw.content = title  # Usar título como conteúdo base
        
        idea = self.processor.process_raw_idea(raw)
        idea = self.processor.apply_slash_overrides(idea, overrides)
        
        return await self._create_thread_from_idea(idea, message.get("channel_id"))
    
    async def _handle_raw_idea(self, message: dict) -> SyncResult:
        """Processa ideia livre no canal #ideias-brutas."""
        raw = create_raw_idea_from_discord_message(message)
        return await self._process_and_create_thread(raw)
    
    async def _process_and_create_thread(self, raw: RawIdea) -> SyncResult:
        """Processa ideia bruta e cria thread."""
        idea = self.processor.process_raw_idea(raw)
        channel_id = self.config.forum_channels.get("raw")
        return await self._create_thread_from_idea(idea, channel_id)
    
    async def _create_thread_from_idea(
        self,
        idea: StructuredIdea,
        channel_id: str,
    ) -> SyncResult:
        """Cria thread no Discord a partir de ideia estruturada."""
        if not channel_id:
            return SyncResult(
                success=False,
                thread_id="",
                action="no_channel",
                error="Canal de destino não configurado",
            )
        
        try:
            thread = await self.forum_manager.create_thread(
                channel_id=channel_id,
                name=idea.title,
                content=idea.content,
                applied_tags=self._idea_to_tag_ids(idea),
            )
            
            logger.info(f"✅ Thread criada: {thread.id} - {thread.name}")
            
            return SyncResult(
                success=True,
                thread_id=thread.id,
                action="thread_created",
                message=f"Thread criada: {thread.name}",
            )
        except Exception as e:
            logger.error(f"Erro ao criar thread: {e}")
            return SyncResult(
                success=False,
                thread_id="",
                action="thread_create_failed",
                error=str(e),
            )
    
    def _idea_to_tag_ids(self, idea: StructuredIdea) -> List[str]:
        """Converte ideia em tag IDs."""
        channel_id = self.config.forum_channels.get("raw", "")
        if not channel_id or not self.forum_manager:
            return []
        
        return self.forum_manager.build_applied_tags(
            channel_id=channel_id,
            status=idea.status,
            prioridade=idea.prioridade.value,
            tipo=idea.tipo.value,
            esforco=idea.esforco.value,
            dominio=idea.dominio.value,
        )
    
    # ============== PROMOTION PIPELINE ==============
    
    async def promote_to_analysis(self, thread_id: str) -> SyncResult:
        """Move thread para canal #em-análise."""
        return await self._move_thread(thread_id, "analysis", status="em-debate")
    
    async def promote_to_experiments(self, thread_id: str) -> SyncResult:
        """Move thread para canal #experimentos."""
        return await self._move_thread(thread_id, "experiments", status="validando")
    
    async def promote_to_ready(self, thread_id: str) -> SyncResult:
        """Move thread para canal #prontas-para-produção."""
        return await self._move_thread(thread_id, "ready", status="aprovada")
    
    async def archive_thread(self, thread_id: str, reason: str = "arquivada") -> SyncResult:
        """Arquiva thread."""
        return await self._move_thread(thread_id, "archive", status=reason)
    
    async def _move_thread(
        self,
        thread_id: str,
        target_channel_key: str,
        status: str,
    ) -> SyncResult:
        """Move thread atualizando tags (Discord não suporta move de forum threads)."""
        target_channel_id = self.config.forum_channels.get(target_channel_key)
        if not target_channel_id:
            return SyncResult(
                success=False,
                thread_id=thread_id,
                action="move_failed",
                error=f"Canal destino '{target_channel_key}' não configurado",
            )
        
        try:
            # Obter thread atual
            thread = await self.forum_manager.get_thread(thread_id)
            
            # Atualizar tags com novo status
            await self.forum_manager.update_thread(
                thread_id=thread_id,
                applied_tags=self.forum_manager.build_applied_tags(
                    channel_id=thread.channel_id,
                    status=status,
                ),
            )
            
            # Postar mensagem de transição
            await self.forum_manager.send_message(
                thread_id=thread_id,
                content=f"📦 **Movida para {target_channel_key}**\n"
                        f"Status atualizado: `{status}`\n"
                        f"Canal destino: <#{target_channel_id}>",
            )
            
            return SyncResult(
                success=True,
                thread_id=thread_id,
                action="moved",
                message=f"Thread movida para {target_channel_key} com status {status}",
            )
        except Exception as e:
            return SyncResult(
                success=False,
                thread_id=thread_id,
                action="move_failed",
                error=str(e),
            )
    
    async def promote_to_kanban(
        self,
        thread_id: str,
        priority: int = 2,
        assignee: str = None,
        skill: str = None,
    ) -> SyncResult:
        """Promove thread aprovada para Kanban produção."""
        try:
            from forum_manager import promote_thread_to_kanban
            
            result = await promote_thread_to_kanban(
                bot_token=self.config.bot_token,
                guild_id=self.config.guild_id,
                thread_id=thread_id,
                kanban_priority=priority,
                assignee=assignee or self.config.default_assignee,
                skill=skill or "cn-tech-ecosystem",
            )
            
            # Criar task no Kanban real
            kanban_data = result["kanban_data"]
            task = self.bridge.create_task(**kanban_data)
            
            # Atualizar thread com link Kanban
            await self.forum_manager.send_message(
                thread_id=thread_id,
                content=f"🚀 **Promovida para Produção**\n"
                        f"Kanban Task: `{task.id}`\n"
                        f"Prioridade: P{priority}\n"
                        f"Assignee: {assignee or self.config.default_assignee}\n"
                        f"Skill: {skill or 'cn-tech-ecosystem'}",
            )
            
            return SyncResult(
                success=True,
                thread_id=thread_id,
                task_id=task.id,
                action="promoted_to_kanban",
                message=f"Task Kanban {task.id} criada",
            )
        except Exception as e:
            logger.error(f"Erro ao promover para Kanban: {e}")
            return SyncResult(
                success=False,
                thread_id=thread_id,
                action="kanban_promote_failed",
                error=str(e),
            )
    
    # ============== TRIAGE & RECONCILIATION ==============
    
    async def run_weekly_triage(self) -> Dict[str, Any]:
        """Executa triagem semanal automática."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "threads_reviewed": 0,
            "promoted": [],
            "archived": [],
            "errors": [],
        }
        
        analysis_channel = self.config.forum_channels.get("analysis")
        if not analysis_channel:
            results["errors"].append("Canal 'analysis' não configurado")
            return results
        
        # Listar threads em análise
        threads = await self.forum_manager.list_threads(analysis_channel, archived=False, limit=50)
        results["threads_reviewed"] = len(threads)
        
        for thread in threads:
            # Verificar timeout de debate
            created = datetime.fromisoformat(thread.created_at.replace("Z", "+00:00"))
            days_old = (datetime.now(created.tzinfo) - created).days
            
            if days_old >= self.config.debate_timeout_days:
                # Auto-arquivar debates parados
                await self.archive_thread(thread.id, "arquivada (timeout debate)")
                results["archived"].append({"id": thread.id, "name": thread.name, "reason": "timeout"})
            else:
                # Avaliar engajamento (reactions, replies)
                # Se alto engajamento e tags de aprovação, promover
                pass
        
        return results
    
    async def run_daily_reconciliation(self) -> List[SyncResult]:
        """Reconciliação diária Forum ↔ Kanban."""
        all_threads = []
        for channel_id in self.config.forum_channels.values():
            threads = await self.forum_manager.list_threads(channel_id, archived=True, limit=100)
            all_threads.extend([asdict(t) for t in threads])
        
        return self.bridge.reconcile(all_threads)
    
    async def generate_daily_summary(self) -> str:
        """Gera resumo diário para postar no Discord."""
        # Coletar stats
        total_threads = 0
        by_channel = {}
        by_status = {}
        
        for name, channel_id in self.config.forum_channels.items():
            threads = await self.forum_manager.list_threads(channel_id, archived=True, limit=100)
            by_channel[name] = len(threads)
            total_threads += len(threads)
            
            for t in threads:
                status_tags = [tag for tag in t.applied_tags if "status" in tag.lower()]
                status = status_tags[0] if status_tags else "sem-status"
                by_status[status] = by_status.get(status, 0) + 1
        
        # Tasks Kanban
        kanban_tasks = self.bridge.list_tasks()
        kanban_by_status = {}
        for t in kanban_tasks:
            kanban_by_status[t.status] = kanban_by_status.get(t.status, 0) + 1
        
        summary = f"""📊 **Resumo Diário da Incubadora** ({datetime.now().strftime('%d/%m/%Y')})

**📁 Threads por Canal:**
"""
        for ch, count in by_channel.items():
            summary += f"  • {ch}: {count}\n"
        
        summary += f"\n**📋 Threads por Status:**\n"
        for status, count in sorted(by_status.items()):
            summary += f"  • {status}: {count}\n"
        
        summary += f"\n**🎯 Tasks Kanban ({self.config.kanban_board}):**\n"
        for status, count in sorted(kanban_by_status.items()):
            summary += f"  • {status}: {count}\n"
        
        summary += f"\n**Total:** {total_threads} threads | {len(kanban_tasks)} tasks"
        
        return summary


# ============== SLASH COMMAND HANDLERS ==============

async def handle_slash_triage(
    orchestrator: IncubatorOrchestrator,
    thread_id: str,
    status: str = None,
    prioridade: str = None,
) -> SyncResult:
    """Handler para /triagem."""
    try:
        # Atualizar tags
        channel_id = None
        for ch_id in orchestrator.config.forum_channels.values():
            thread = await orchestrator.forum_manager.get_thread(thread_id)
            if thread.channel_id == ch_id:
                channel_id = ch_id
                break
        
        if not channel_id:
            return SyncResult(
                success=False,
                thread_id=thread_id,
                action="triage_failed",
                error="Thread não encontrada nos canais monitorados",
            )
        
        await orchestrator.forum_manager.get_available_tags(channel_id)
        new_tags = orchestrator.forum_manager.build_applied_tags(
            channel_id=channel_id,
            status=status,
            prioridade=prioridade,
        )
        
        await orchestrator.forum_manager.update_thread(
            thread_id=thread_id,
            applied_tags=new_tags,
        )
        
        return SyncResult(
            success=True,
            thread_id=thread_id,
            action="triaged",
            message=f"Tags atualizadas: status={status}, prioridade={prioridade}",
        )
    except Exception as e:
        return SyncResult(
            success=False,
            thread_id=thread_id,
            action="triage_failed",
            error=str(e),
        )


async def handle_slash_spike(
    orchestrator: IncubatorOrchestrator,
    thread_id: str,
    timebox: str = "4h",
) -> SyncResult:
    """Handler para /spike."""
    try:
        # Mover para experimentos
        result = await orchestrator.promote_to_experiments(thread_id)
        if not result.success:
            return result
        
        # Criar task Kanban spike
        thread = await orchestrator.forum_manager.get_thread(thread_id)
        channel_id = thread.channel_id
        
        task = orchestrator.bridge.create_task(
            title=f"Spike: {thread.name}",
            body=f"""**Spike Técnico** (timebox: {timebox})

**Origem:** Thread Discord {thread_id}
**Objetivo:** Validar viabilidade técnica da ideia

**Critérios de Validação:**
- [ ] Critério técnico 1
- [ ] Critério técnico 2

**Resultado Esperado:** Viável / Inviável / Parcial
""",
            priority=2,
            skill="cn-tech-ecosystem",
        )
        
        # Postar na thread
        await orchestrator.forum_manager.send_message(
            thread_id=thread_id,
            content=f"⚗️ **Spike Criado**\n"
                    f"Task: `{task.id}`\n"
                    f"Timebox: {timebox}\n"
                    f"Assignee: {task.assignee}",
        )
        
        return SyncResult(
            success=True,
            thread_id=thread_id,
            task_id=task.id,
            action="spike_created",
            message=f"Spike task {task.id} criada com timebox {timebox}",
        )
    except Exception as e:
        return SyncResult(
            success=False,
            thread_id=thread_id,
            action="spike_failed",
            error=str(e),
        )


async def handle_slash_promote(
    orchestrator: IncubatorOrchestrator,
    thread_id: str,
    prioridade: int = 2,
    assignee: str = "default",
    skill: str = "cn-tech-ecosystem",
) -> SyncResult:
    """Handler para /promover."""
    return await orchestrator.promote_to_kanban(
        thread_id=thread_id,
        priority=prioridade,
        assignee=assignee,
        skill=skill,
    )


async def handle_slash_archive(
    orchestrator: IncubatorOrchestrator,
    thread_id: str,
    motivo: str = "arquivada",
) -> SyncResult:
    """Handler para /arquivar."""
    valid_reasons = ["feita", "descartada", "depois", "arquivada"]
    if motivo not in valid_reasons:
        motivo = "arquivada"
    
    return await orchestrator.archive_thread(thread_id, motivo)


async def handle_slash_resumo(
    orchestrator: IncubatorOrchestrator,
    periodo: str = "dia",
) -> str:
    """Handler para /resumo-incubadora."""
    if periodo == "dia":
        return await orchestrator.generate_daily_summary()
    elif periodo == "semana":
        # Implementar resumo semanal
        return "Resumo semanal - TODO"
    return "Período inválido. Use: dia ou semana"


# ============== MAIN ==============

async def main():
    """Teste rápido do orquestrador."""
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    guild_id = os.getenv("DISCORD_GUILD_ID", "1516397584942370836")
    
    if not bot_token:
        print("❌ DISCORD_BOT_TOKEN não configurado")
        return
    
    # Configuração (ajustar channel IDs conforme seu servidor)
    config = IncubatorConfig(
        bot_token=bot_token,
        guild_id=guild_id,
        forum_channels={
            "raw": "YOUR_FORUM_CHANNEL_ID_RAW",        # #ideias-brutas
            "analysis": "YOUR_FORUM_CHANNEL_ID_ANALYSIS",  # #em-análise
            "experiments": "YOUR_FORUM_CHANNEL_ID_EXP",    # #experimentos
            "ready": "YOUR_FORUM_CHANNEL_ID_READY",        # #prontas-para-produção
            "archive": "YOUR_FORUM_CHANNEL_ID_ARCHIVE",    # #arquivadas
            "templates": "YOUR_FORUM_CHANNEL_ID_TEMPLATES", # #templates
        },
    )
    
    async with IncubatorOrchestrator(config) as orchestrator:
        # Testar listagem de canais
        print("🔍 Verificando canais de fórum...")
        # for name, ch_id in config.forum_channels.items():
        #     try:
        #         threads = await orchestrator.forum_manager.list_threads(ch_id, limit=5)
        #         print(f"  {name} ({ch_id}): {len(threads)} threads")
        #     except Exception as e:
        #         print(f"  {name} ({ch_id}): ERRO - {e}")
        
        print("✅ Orquestrador inicializado com sucesso!")
        print("\nPróximos passos:")
        print("1. Configure os channel IDs reais no config")
        print("2. Crie as tags necessárias nos canais de fórum")
        print("3. Configure webhook Discord → Hermes para mensagens")
        print("4. Configure cron jobs para triagem/reconciliação")
        print("5. Teste E2E: voice → thread → debate → spike → kanban → deploy")


if __name__ == "__main__":
    asyncio.run(main())