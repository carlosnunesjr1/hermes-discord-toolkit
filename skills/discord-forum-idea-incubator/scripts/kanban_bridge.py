#!/usr/bin/env python3
"""
Kanban Bridge - Sincronização bidirecional entre Discord Forum Threads e Hermes Kanban.
Parte da Hermes Incubadora de Ideias.
"""

import os
import json
import asyncio
import subprocess
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class KanbanStatus(Enum):
    TRIAGE = "triage"
    TODO = "todo"
    SCHEDULED = "scheduled"
    READY = "ready"
    RUNNING = "running"
    DONE = "done"
    BLOCKED = "blocked"
    ARCHIVED = "archived"


class KanbanPriority(Enum):
    P1 = 1
    P2 = 2
    P3 = 3
    P4 = 4
    P5 = 5


@dataclass
class KanbanTask:
    """Task do Kanban Hermes."""
    id: str
    title: str
    body: str
    status: str
    priority: int
    assignee: str
    skill: Optional[str]
    parent_ids: List[str]
    created_at: str
    updated_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SyncResult:
    """Resultado de sincronização."""
    success: bool
    thread_id: str
    task_id: Optional[str] = None
    action: str = ""
    message: str = ""
    error: Optional[str] = None


class KanbanBridge:
    """Ponte entre Discord Forum e Hermes Kanban."""
    
    def __init__(
        self,
        hermes_cli: str = "hermes",
        kanban_board: str = "incubator",
        default_assignee: str = "default",
        profile: str = "default",
    ):
        self.hermes_cli = hermes_cli
        self.kanban_board = kanban_board
        self.default_assignee = default_assignee
        self.profile = profile
        self._task_cache: Dict[str, KanbanTask] = {}
    
    def _run_hermes(self, args: List[str], input_data: str = None) -> subprocess.CompletedProcess:
        """Executa comando hermes kanban."""
        cmd = [self.hermes_cli, "kanban"] + args
        env = os.environ.copy()
        env["HERMES_PROFILE"] = self.profile
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            input=input_data,
            env=env,
            timeout=60,
        )
    
    def _run_hermes_json(self, args: List[str]) -> dict:
        """Executa e parseia JSON."""
        # Kanban list doesn't support --json flag, check which command
        json_args = args.copy()
        if args and args[0] in ["create", "show", "boards", "list", "ls"]:
            json_args.append("--json")
        result = self._run_hermes(json_args)
        if result.returncode != 0:
            raise Exception(f"hermes kanban failed: {result.stderr}")
        if not result.stdout.strip():
            return {}
        return json.loads(result.stdout)
    
    # ============== KANBAN OPERATIONS ==============
    
    def create_task(
        self,
        title: str,
        body: str,
        priority: int = 3,
        assignee: str = None,
        skill: str = None,
        triage: bool = False,
        parent: str = None,
    ) -> KanbanTask:
        """Cria task no Kanban."""
        args = [
            "create", title,
            "--body", body,
            "--priority", str(priority),
        ]
        if assignee:
            args.extend(["--assignee", assignee])
        if skill:
            args.extend(["--skill", skill])
        if triage:
            args.append("--triage")
        if parent:
            args.extend(["--parent", parent])
        
        result = self._run_hermes_json(args)
        task_data = result.get("task", result)
        
        task = KanbanTask(
            id=task_data.get("id", ""),
            title=task_data.get("title", title),
            body=task_data.get("body", body),
            status=task_data.get("status", "triage"),
            priority=task_data.get("priority", priority),
            assignee=task_data.get("assignee", assignee or self.default_assignee),
            skill=task_data.get("skill", skill),
            parent_ids=task_data.get("parent_ids", [parent] if parent else []),
            created_at=task_data.get("created_at", datetime.now().isoformat()),
            updated_at=task_data.get("updated_at", datetime.now().isoformat()),
            metadata={
                "source": "discord-forum",
                "synced_at": datetime.now().isoformat(),
            },
        )
        
        self._task_cache[task.id] = task
        return task
    
    def get_task(self, task_id: str) -> Optional[KanbanTask]:
        """Obtém task por ID."""
        if task_id in self._task_cache:
            return self._task_cache[task_id]
        
        result = self._run_hermes_json(["show", task_id])
        task_data = result.get("task", result)
        
        task = KanbanTask(
            id=task_data.get("id", task_id),
            title=task_data.get("title", ""),
            body=task_data.get("body", ""),
            status=task_data.get("status", ""),
            priority=task_data.get("priority", 3),
            assignee=task_data.get("assignee", ""),
            skill=task_data.get("skill"),
            parent_ids=task_data.get("parent_ids", []),
            created_at=task_data.get("created_at", ""),
            updated_at=task_data.get("updated_at", ""),
            started_at=task_data.get("started_at"),
            completed_at=task_data.get("completed_at"),
        )
        
        self._task_cache[task_id] = task
        return task
    
    def list_tasks(
        self,
        status: str = None,
        assignee: str = None,
        limit: int = 50,
    ) -> List[KanbanTask]:
        """Lista tasks."""
        args = ["list"]
        if status:
            args.extend(["--status", status])
        if assignee:
            args.extend(["--assignee", assignee])
        # Note: hermes kanban list doesn't support --limit
        
        result = self._run_hermes_json(args)
        tasks = []
        # hermes kanban list --json returns a list directly
        if isinstance(result, list):
            task_list = result
        else:
            task_list = result.get("tasks", [])
        for task_data in task_list:
            task = KanbanTask(
                id=task_data.get("id", ""),
                title=task_data.get("title", ""),
                body=task_data.get("body", ""),
                status=task_data.get("status", ""),
                priority=task_data.get("priority", 3),
                assignee=task_data.get("assignee", ""),
                skill=task_data.get("skill"),
                parent_ids=task_data.get("parent_ids", []),
                created_at=task_data.get("created_at", ""),
                updated_at=task_data.get("updated_at", ""),
            )
            tasks.append(task)
            self._task_cache[task.id] = task
        return tasks[:limit]
    
    def update_task(
        self,
        task_id: str,
        status: str = None,
        priority: int = None,
        assignee: str = None,
        body: str = None,
    ) -> KanbanTask:
        """Atualiza task."""
        # Hermes kanban não tem update direto, usar promote/complete/archive
        # Para body/priority, precisaria recriar ou editar via arquivo
        task = self.get_task(task_id)
        if not task:
            raise Exception(f"Task {task_id} não encontrada")
        
        if status:
            if status == "done":
                self._run_hermes(["complete", task_id])
            elif status == "blocked":
                self._run_hermes(["block", task_id, "--reason", "Bloqueado via bridge"])
            elif status in ["todo", "ready", "running"]:
                self._run_hermes(["promote", task_id])
            elif status == "archived":
                self._run_hermes(["archive", task_id])
            task.status = status
        
        task.updated_at = datetime.now().isoformat()
        return task
    
    def promote_task(self, task_id: str) -> KanbanTask:
        """Promove task (avança status)."""
        self._run_hermes(["promote", task_id])
        return self.get_task(task_id)
    
    def complete_task(self, task_id: str) -> KanbanTask:
        """Marca task como concluída."""
        self._run_hermes(["complete", task_id])
        task = self.get_task(task_id)
        task.status = "done"
        task.completed_at = datetime.now().isoformat()
        return task
    
    def dispatch_tasks(self, dry_run: bool = False) -> dict:
        """Dispara tasks para workers."""
        args = ["dispatch"]
        if dry_run:
            args.append("--dry-run")
        result = self._run_hermes_json(args)
        return result
    
    # ============== SYNC OPERATIONS ==============
    
    def thread_to_kanban(
        self,
        thread_id: str,
        thread_name: str,
        thread_content: str,
        thread_tags: List[str],
        thread_url: str,
        priority: int = 3,
        assignee: str = None,
        skill: str = None,
        triage: bool = False,
    ) -> SyncResult:
        """Cria task Kanban a partir de thread do Discord."""
        try:
            # Determinar skill baseado em tags
            if not skill:
                skill = self._map_domain_to_skill(thread_tags)
            
            # Construir body rico
            body = self._build_kanban_body(
                thread_id=thread_id,
                thread_name=thread_name,
                thread_content=thread_content,
                thread_tags=thread_tags,
                thread_url=thread_url,
            )
            
            task = self.create_task(
                title=thread_name[:200],
                body=body,
                priority=priority,
                assignee=assignee or self.default_assignee,
                skill=skill,
                triage=triage,
            )
            
            return SyncResult(
                success=True,
                thread_id=thread_id,
                task_id=task.id,
                action="created",
                message=f"Task Kanban {task.id} criada com prioridade {priority}",
            )
        except Exception as e:
            return SyncResult(
                success=False,
                thread_id=thread_id,
                action="create_failed",
                error=str(e),
            )
    
    def kanban_to_thread_update(
        self,
        task_id: str,
        forum_manager,  # DiscordForumManager instance
    ) -> SyncResult:
        """Atualiza thread Discord com progresso do Kanban."""
        try:
            task = self.get_task(task_id)
            if not task:
                return SyncResult(
                    success=False,
                    thread_id="",
                    task_id=task_id,
                    action="update_failed",
                    error="Task não encontrada",
                )
            
            # Extrair thread_id do body/metadata
            thread_id = self._extract_thread_id(task.body)
            if not thread_id:
                return SyncResult(
                    success=False,
                    thread_id="",
                    task_id=task_id,
                    action="update_failed",
                    error="Thread ID não encontrado no body da task",
                )
            
            # Enviar update para thread
            status_emoji = {
                "triage": "📥",
                "todo": "📋",
                "scheduled": "📅",
                "ready": "✅",
                "running": "🔄",
                "done": "🎉",
                "blocked": "🚫",
                "archived": "📦",
            }.get(task.status, "📝")
            
            message = (
                f"{status_emoji} **Kanban Update**\n"
                f"Task: `{task_id}`\n"
                f"Status: `{task.status}`\n"
                f"Prioridade: `P{task.priority}`\n"
                f"Assignee: `{task.assignee}`\n"
            )
            
            if task.started_at:
                message += f"Iniciada: `{task.started_at[:19]}`\n"
            if task.completed_at:
                message += f"Concluída: `{task.completed_at[:19]}`\n"
            
            # Nota: forum_manager precisa ser passado para enviar mensagem
            # Aqui só retornamos o que seria enviado
            return SyncResult(
                success=True,
                thread_id=thread_id,
                task_id=task_id,
                action="thread_update_prepared",
                message=message,
            )
        except Exception as e:
            return SyncResult(
                success=False,
                thread_id="",
                task_id=task_id,
                action="update_failed",
                error=str(e),
            )
    
    def reconcile(self, forum_threads: List[dict]) -> List[SyncResult]:
        """
        Reconcilia estado: threads no forum vs tasks no Kanban.
        Retorna lista de ações necessárias.
        """
        results = []
        
        # Obter todas tasks do board incubator
        kanban_tasks = self.list_tasks()
        task_by_thread = {}
        
        for task in kanban_tasks:
            thread_id = self._extract_thread_id(task.body)
            if thread_id:
                task_by_thread[thread_id] = task
        
        # Verificar cada thread
        for thread in forum_threads:
            thread_id = thread.get("id")
            thread_tags = thread.get("applied_tags", [])
            status_tag = next((t for t in thread_tags if "aprovada" in t or "status:" in t), None)
            
            if thread_id in task_by_thread:
                # Já sincronizada - verificar se status mudou
                task = task_by_thread[thread_id]
                if "aprovada" in str(thread_tags) and task.status in ["triage", "todo"]:
                    results.append(SyncResult(
                        success=True,
                        thread_id=thread_id,
                        task_id=task.id,
                        action="promote_needed",
                        message=f"Thread aprovada mas task em {task.status}",
                    ))
            else:
                # Nova thread aprovada - precisa criar task
                if "aprovada" in str(thread_tags):
                    results.append(SyncResult(
                        success=True,
                        thread_id=thread_id,
                        action="create_needed",
                        message=f"Thread aprovada sem task Kanban correspondente",
                    ))
        
        # Verificar tasks órfãs (task existe mas thread arquivada/deletada)
        for thread_id, task in task_by_thread.items():
            thread_exists = any(t.get("id") == thread_id for t in forum_threads)
            if not thread_exists and task.status not in ["done", "archived"]:
                results.append(SyncResult(
                    success=True,
                    thread_id=thread_id,
                    task_id=task.id,
                    action="thread_missing",
                    message=f"Task {task.id} existe mas thread {thread_id} não encontrada",
                ))
        
        return results
    
    # ============== HELPERS ==============
    
    def _map_domain_to_skill(self, tags: List[str]) -> str:
        """Mapeia tag de domínio para skill Hermes."""
        domain_skills = {
            "career": "cn-tech-ecosystem",
            "pim": "cn-tech-ecosystem",
            "router": "cn-tech-ecosystem",
            "infra": "cn-tech-ecosystem",
            "hermes": "hermes-agent",
            "geral": "system-architect-audit",
        }
        
        for tag in tags:
            for domain, skill in domain_skills.items():
                if domain in tag.lower():
                    return skill
        return "cn-tech-ecosystem"
    
    def _build_kanban_body(
        self,
        thread_id: str,
        thread_name: str,
        thread_content: str,
        thread_tags: List[str],
        thread_url: str,
    ) -> str:
        """Constrói body rico para task Kanban."""
        return f"""**🔗 Origem:** Discord Forum Thread
- **Thread:** [{thread_id}]({thread_url})
- **Canal:** Forum Discord
- **Tags:** {', '.join(thread_tags) if thread_tags else 'nenhuma'}

---

**📝 Conteúdo Original:**
{thread_content}

---

**✅ Critérios de Aceite (do template):**
- [ ] Implementar conforme especificado na thread
- [ ] Testes unitários/integração passando
- [ ] Documentação atualizada
- [ ] Deploy validado em staging
- [ ] Validação com stakeholder

---

**⚠️ Riscos Identificados:**
_Extrair da thread durante triagem_

---

**🔗 Dependências:**
_Extrair da thread durante triagem_

---

**📊 Metadata Sync:**
```json
{{
  "source": "discord-forum",
  "thread_id": "{thread_id}",
  "thread_url": "{thread_url}",
  "synced_at": "{datetime.now().isoformat()}",
  "tags": {json.dumps(thread_tags)}
}}
```"""
    
    def _extract_thread_id(self, body: str) -> Optional[str]:
        """Extrai thread_id do body da task."""
        # Procura no metadata JSON no final
        try:
            # Tentar achar JSON metadata
            if '"thread_id":' in body:
                start = body.index('"thread_id":') + len('"thread_id":')
                end = body.index('"', start + 1)
                return body[start+1:end]
        except (ValueError, IndexError):
            pass
        
        # Fallback: procurar URL do Discord
        import re
        match = re.search(r'discord\.com/channels/\d+/(\d+)/(\d+)', body)
        if match:
            return match.group(2)  # thread_id
        
        return None


# ============== WEBHOOK HANDLER ==============

class KanbanWebhookHandler:
    """Handler para webhooks do Kanban → Discord."""
    
    def __init__(self, forum_manager, bridge: KanbanBridge):
        self.forum_manager = forum_manager
        self.bridge = bridge
    
    async def on_task_created(self, task_data: dict) -> None:
        """Task criada no Kanban."""
        # Opcional: criar thread de acompanhamento se não existir
        pass
    
    async def on_task_status_changed(self, task_data: dict) -> None:
        """Task mudou de status."""
        task_id = task_data.get("id")
        if not task_id:
            return
        
        result = self.bridge.kanban_to_thread_update(task_id, self.forum_manager)
        if result.success and result.message:
            # Enviar para thread
            try:
                await self.forum_manager.send_message(
                    thread_id=result.thread_id,
                    content=result.message,
                )
            except Exception as e:
                print(f"Erro ao enviar update para thread: {e}")
    
    async def on_task_completed(self, task_data: dict) -> None:
        """Task concluída."""
        await self.on_task_status_changed(task_data)
        # Marcar thread como feita
        task_id = task_data.get("id")
        thread_id = self.bridge._extract_thread_id(task_data.get("body", ""))
        if thread_id:
            try:
                # Atualizar tags para 'feita'
                tags = await self.forum_manager.get_available_tags(
                    # Precisa do channel_id - extrair da thread ou passar
                )
                # forum_manager.update_thread(thread_id, applied_tags=[...])
            except Exception as e:
                print(f"Erro ao atualizar thread para feita: {e}")


# ============== CRON JOB ==============

def run_reconciliation_cron(
    bot_token: str,
    guild_id: str,
    forum_channel_ids: List[str],
    hermes_cli: str = "hermes",
) -> List[SyncResult]:
    """Job de reconciliação para cron (pode ser chamado via hermes cron)."""
    from scripts.forum_manager import DiscordForumManager
    
    async def _run():
        async with DiscordForumManager(bot_token, guild_id) as forum_mgr:
            bridge = KanbanBridge(hermes_cli=hermes_cli)
            
            all_threads = []
            for channel_id in forum_channel_ids:
                threads = await forum_mgr.list_threads(channel_id, archived=True, limit=100)
                all_threads.extend([t for t in threads])
            
            return bridge.reconcile(all_threads)
    
    return asyncio.run(_run())


if __name__ == "__main__":
    # Teste rápido
    bridge = KanbanBridge()
    
    # Listar tasks
    print("=== Tasks Kanban ===")
    tasks = bridge.list_tasks(limit=10)
    for t in tasks:
        print(f"  {t.id[:8]} | P{t.priority} | {t.status:10} | {t.title[:50]}")
    
    # Testar criação
    print("\n=== Criando task de teste ===")
    test_thread_id = "test-thread-123"
    test_url = f"https://discord.com/channels/1516397584942370836/123456789/{test_thread_id}"
    
    result = bridge.thread_to_kanban(
        thread_id=test_thread_id,
        thread_name="Teste Incubadora: OAuth Career Hub",
        thread_content="Adicionar login OAuth Google/GitHub no Career Hub",
        thread_tags=["status:aprovada", "prioridade:P2-alta", "tipo:feature", "dominio:career"],
        thread_url=test_url,
        priority=2,
        assignee="default",
        skill="cn-tech-ecosystem",
    )
    
    print(f"Resultado: {result}")
    if result.task_id:
        print(f"Task criada: {result.task_id}")
        # Verificar
        task = bridge.get_task(result.task_id)
        print(f"Task verificada: {task.title} | {task.status} | P{task.priority}")