#!/usr/bin/env python3
"""
Discord Forum Manager - Gerenciamento de threads em canais de fórum do Discord.
Usado pela Hermes Incubadora de Ideias.
"""

import os
import json
import asyncio
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
import aiohttp


@dataclass
class ForumThread:
    """Representa uma thread em um canal de fórum."""
    id: str
    channel_id: str
    name: str
    content: str
    tags: List[str]
    applied_tags: List[str]  # Tag IDs aplicados
    owner_id: str
    created_at: str
    archived: bool
    locked: bool
    message_count: int
    last_message_id: Optional[str] = None
    
    @classmethod
    def from_discord(cls, data: dict) -> "ForumThread":
        return cls(
            id=data["id"],
            channel_id=data["parent_id"],
            name=data["name"],
            content=data.get("message", {}).get("content", ""),
            tags=[],  # Preenchido separadamente
            applied_tags=data.get("applied_tags", []),
            owner_id=data.get("owner_id", ""),
            created_at=data.get("thread_metadata", {}).get("create_timestamp", ""),
            archived=data.get("thread_metadata", {}).get("archived", False),
            locked=data.get("thread_metadata", {}).get("locked", False),
            message_count=data.get("message_count", 0),
            last_message_id=data.get("last_message_id"),
        )


@dataclass
class ForumTag:
    """Tag de um canal de fórum."""
    id: str
    name: str
    moderated: bool
    emoji_id: Optional[str] = None
    emoji_name: Optional[str] = None
    
    @classmethod
    def from_discord(cls, data: dict) -> "ForumTag":
        return cls(
            id=data["id"],
            name=data["name"],
            moderated=data.get("moderated", False),
            emoji_id=data.get("emoji_id"),
            emoji_name=data.get("emoji_name"),
        )


class DiscordForumManager:
    """Gerencia canais de fórum e threads do Discord via Bot Token."""
    
    def __init__(self, bot_token: str, guild_id: str):
        self.bot_token = bot_token
        self.guild_id = guild_id
        self.base_url = "https://discord.com/api/v10"
        self.headers = {
            "Authorization": f"Bot {bot_token}",
            "Content-Type": "application/json",
        }
        self._session: Optional[aiohttp.ClientSession] = None
        self._tags_cache: Dict[str, List[ForumTag]] = {}
    
    async def __aenter__(self):
        self._session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, *args):
        if self._session:
            await self._session.close()
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Faz requisição à API do Discord."""
        if not self._session:
            self._session = aiohttp.ClientSession(headers=self.headers)
        
        url = f"{self.base_url}{endpoint}"
        async with self._session.request(method, url, **kwargs) as resp:
            if resp.status >= 400:
                text = await resp.text()
                raise Exception(f"Discord API {resp.status}: {text}")
            if resp.content_type == "application/json":
                return await resp.json()
            return {}
    
    # ============== CANAIS DE FÓRUM ==============
    
    async def get_forum_channels(self) -> List[dict]:
        """Lista todos os canais do servidor, filtrando forum channels."""
        data = await self._request("GET", f"/guilds/{self.guild_id}/channels")
        return [c for c in data if c.get("type") == 15]  # ChannelType.GUILD_FORUM = 15
    
    async def get_forum_channel(self, channel_id: str) -> dict:
        """Obtém detalhes de um canal de fórum específico."""
        return await self._request("GET", f"/channels/{channel_id}")
    
    async def get_available_tags(self, channel_id: str) -> List[ForumTag]:
        """Obtém tags disponíveis no canal de fórum (cached)."""
        if channel_id not in self._tags_cache:
            channel = await self.get_forum_channel(channel_id)
            self._tags_cache[channel_id] = [
                ForumTag.from_discord(t) for t in channel.get("available_tags", [])
            ]
        return self._tags_cache[channel_id]
    
    def find_tag_id(self, channel_id: str, tag_name: str) -> Optional[str]:
        """Encontra ID da tag pelo nome (case-insensitive)."""
        tags = self._tags_cache.get(channel_id, [])
        for tag in tags:
            if tag.name.lower() == tag_name.lower():
                return tag.id
        return None
    
    # ============== THREADS ==============
    
    async def create_thread(
        self,
        channel_id: str,
        name: str,
        content: str,
        applied_tags: List[str] = None,
        auto_archive_duration: int = 10080,  # 1 week
    ) -> ForumThread:
        """Cria uma nova thread no canal de fórum."""
        payload = {
            "name": name[:100],  # Max 100 chars
            "auto_archive_duration": auto_archive_duration,
            "message": {"content": content[:2000]},
        }
        if applied_tags:
            payload["applied_tags"] = applied_tags
        
        data = await self._request("POST", f"/channels/{channel_id}/threads", json=payload)
        thread = ForumThread.from_discord(data)
        thread.applied_tags = applied_tags or []
        return thread
    
    async def get_thread(self, thread_id: str) -> ForumThread:
        """Obtém uma thread específica."""
        data = await self._request("GET", f"/channels/{thread_id}")
        return ForumThread.from_discord(data)
    
    async def list_threads(
        self,
        channel_id: str,
        archived: bool = False,
        limit: int = 50,
    ) -> List[ForumThread]:
        """Lista threads ativas ou arquivadas do canal."""
        threads = []
        
        if not archived:
            # Use guild-level active threads endpoint and filter by parent_id
            data = await self._request("GET", f"/guilds/{self.guild_id}/threads/active")
            all_threads = data.get("threads", [])
            threads = [
                ForumThread.from_discord(t) for t in all_threads
                if t.get("parent_id") == channel_id
            ]
        else:
            # Archived threads (paginated) - channel-specific endpoint works for archived
            after = None
            while len(threads) < limit:
                params = {"limit": min(50, limit - len(threads))}
                if after:
                    params["after"] = after
                try:
                    archived_data = await self._request(
                        "GET", f"/channels/{channel_id}/threads/archived/public", params=params
                    )
                    archived_threads = [
                        ForumThread.from_discord(t) for t in archived_data.get("threads", [])
                    ]
                    if not archived_threads:
                        break
                    threads.extend(archived_threads)
                    after = archived_threads[-1].id
                except Exception as e:
                    # If archived endpoint fails, try guild-level
                    print(f"Warning: archived endpoint failed, trying guild: {e}")
                    break
        
        return threads[:limit]
    
    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        archived: Optional[bool] = None,
        locked: Optional[bool] = None,
        applied_tags: Optional[List[str]] = None,
    ) -> ForumThread:
        """Atualiza uma thread (nome, archive, lock, tags)."""
        payload = {}
        if name is not None:
            payload["name"] = name[:100]
        if archived is not None:
            payload["archived"] = archived
        if locked is not None:
            payload["locked"] = locked
        if applied_tags is not None:
            payload["applied_tags"] = applied_tags
        
        data = await self._request("PATCH", f"/channels/{thread_id}", json=payload)
        return ForumThread.from_discord(data)
    
    async def send_message(
        self,
        thread_id: str,
        content: str,
        embeds: Optional[List[dict]] = None,
    ) -> dict:
        """Envia mensagem na thread."""
        payload = {"content": content[:2000]}
        if embeds:
            payload["embeds"] = embeds
        return await self._request("POST", f"/channels/{thread_id}/messages", json=payload)
    
    async def add_reaction(self, thread_id: str, message_id: str, emoji: str) -> None:
        """Adiciona reação a uma mensagem."""
        encoded_emoji = emoji.encode("utf-8").decode("utf-8")
        await self._request(
            "PUT", f"/channels/{thread_id}/messages/{message_id}/reactions/{encoded_emoji}/@me"
        )
    
    # ============== TEMPLATES ==============
    
    async def create_thread_from_template(
        self,
        channel_id: str,
        template_name: str,
        variables: Dict[str, str],
        applied_tags: List[str] = None,
    ) -> ForumThread:
        """Cria thread a partir de template armazenado no canal #templates."""
        # Buscar template no canal de templates
        templates_channel_id = await self._find_templates_channel()
        if not templates_channel_id:
            raise Exception("Canal de templates não encontrado")
        
        templates = await self.list_threads(templates_channel_id, archived=True, limit=100)
        template_thread = next((t for t in templates if t.name == template_name), None)
        
        if not template_thread:
            raise Exception(f"Template '{template_name}' não encontrado")
        
        # Obter conteúdo completo do template
        template_full = await self.get_thread(template_thread.id)
        
        # Aplicar variáveis
        content = template_full.content
        for key, value in variables.items():
            content = content.replace(f"{{{{{key}}}}}", value)
        
        name = template_name.replace("Template: ", "").strip()
        name = name[:100]
        
        return await self.create_thread(
            channel_id=channel_id,
            name=name,
            content=content,
            applied_tags=applied_tags,
        )
    
    async def _find_templates_channel(self) -> Optional[str]:
        """Encontra canal de templates por nome."""
        forums = await self.get_forum_channels()
        for f in forums:
            if "template" in f["name"].lower():
                return f["id"]
        return None
    
    # ============== UTILITÁRIOS DE TAGS ==============
    
    def build_applied_tags(
        self,
        channel_id: str,
        status: Optional[str] = None,
        prioridade: Optional[str] = None,
        tipo: Optional[str] = None,
        esforco: Optional[str] = None,
        dominio: Optional[str] = None,
    ) -> List[str]:
        """Constrói lista de tag IDs baseado nos parâmetros."""
        tag_ids = []
        
        mapping = {
            "status": status,
            "prioridade": prioridade,
            "tipo": tipo,
            "esforco": esforco,
            "dominio": dominio,
        }
        
        for category, value in mapping.items():
            if value:
                tag_id = self.find_tag_id(channel_id, value)
                if tag_id:
                    tag_ids.append(tag_id)
                else:
                    print(f"⚠️ Tag '{value}' (categoria: {category}) não encontrada no canal {channel_id}")
        
        return tag_ids


# ============== FUNÇÕES HELPER PARA USO DIRETO ==============

async def create_idea_thread(
    bot_token: str,
    guild_id: str,
    channel_id: str,
    title: str,
    content: str,
    status: str = "capturada",
    prioridade: str = "P3-normal",
    tipo: str = "feature",
    esforco: str = "desconhecido",
    dominio: str = "geral",
) -> ForumThread:
    """Helper rápido para criar thread de ideia com tags padrão."""
    async with DiscordForumManager(bot_token, guild_id) as mgr:
        # Garantir cache de tags
        await mgr.get_available_tags(channel_id)
        
        applied_tags = mgr.build_applied_tags(
            channel_id=channel_id,
            status=status,
            prioridade=prioridade,
            tipo=tipo,
            esforco=esforco,
            dominio=dominio,
        )
        
        return await mgr.create_thread(
            channel_id=channel_id,
            name=title[:100],
            content=content,
            applied_tags=applied_tags,
        )


async def promote_thread_to_kanban(
    bot_token: str,
    guild_id: str,
    thread_id: str,
    kanban_priority: int = 2,
    assignee: str = "default",
    skill: str = "cn-tech-ecosystem",
) -> dict:
    """
    Promove thread para Kanban.
    Retorna dict com info da thread e task Kanban criada.
    """
    async with DiscordForumManager(bot_token, guild_id) as mgr:
        thread = await mgr.get_thread(thread_id)
        
        # Extrair metadata da thread
        channel = await mgr.get_forum_channel(thread.channel_id)
        await mgr.get_available_tags(thread.channel_id)
        
        # Mapear tags de volta para valores legíveis
        tag_names = []
        for tag_id in thread.applied_tags:
            for tag in mgr._tags_cache.get(thread.channel_id, []):
                if tag.id == tag_id:
                    tag_names.append(tag.name)
                    break
        
        # Construir body para Kanban
        kanban_body = f"""**Origem:** Discord Forum Thread [{thread_id}](https://discord.com/channels/{guild_id}/{thread.channel_id}/{thread_id})

**Contexto Original:**
{thread.content}

**Tags:** {', '.join(tag_names)}

**Critérios de Aceite:**
- [ ] Implementar conforme especificado na thread
- [ ] Testes passando
- [ ] Deploy validado

**Riscos Identificados:**
- Ver thread para detalhes
"""
        
        # Atualizar thread: status=aprovada, mover para canal pronto
        # (movimento de canal requer recriar thread ou usar API de move - Discord não suporta move direto de forum threads)
        # Workaround: atualizar tags + postar mensagem de transição
        
        await mgr.update_thread(
            thread_id=thread_id,
            applied_tags=mgr.build_applied_tags(
                channel_id=thread.channel_id,
                status="aprovada",
                prioridade=f"P{kanban_priority}-alta" if kanban_priority <= 2 else "P3-normal",
                tipo=next((t for t in tag_names if t in ["feature", "bug", "tech-debt", "pesquisa", "processo", "infra"]), "feature"),
            ),
        )
        
        await mgr.send_message(
            thread_id=thread_id,
            content=f"✅ **Promovida para Produção**\n"
                    f"Kanban Task criada com prioridade {kanban_priority}, assignee: {assignee}, skill: {skill}\n"
                    f"Link Kanban: (será preenchido pelo bridge)"
        )
        
        return {
            "thread": asdict(thread),
            "kanban_data": {
                "title": thread.name,
                "body": kanban_body,
                "priority": kanban_priority,
                "assignee": assignee,
                "skill": skill,
            },
        }


if __name__ == "__main__":
    import sys
    
    # Teste rápido via CLI
    if len(sys.argv) < 2:
        print("Uso: python forum_manager.py <comando> [args...]")
        print("Comandos: list-forums, list-threads <channel_id>, create-thread <channel_id> <title> <content>")
        sys.exit(1)
    
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    guild_id = os.getenv("DISCORD_GUILD_ID", "1516397584942370836")
    
    if not bot_token:
        print("❌ DISCORD_BOT_TOKEN não configurado")
        sys.exit(1)
    
    async def main():
        async with DiscordForumManager(bot_token, guild_id) as mgr:
            cmd = sys.argv[1]
            
            if cmd == "list-forums":
                forums = await mgr.get_forum_channels()
                print(f"📁 {len(forums)} canais de fórum encontrados:")
                for f in forums:
                    print(f"  - {f['name']} (ID: {f['id']})")
                    tags = await mgr.get_available_tags(f['id'])
                    if tags:
                        print(f"    Tags: {', '.join([t.name for t in tags])}")
            
            elif cmd == "list-threads" and len(sys.argv) >= 3:
                channel_id = sys.argv[2]
                # Default to active threads, use --archived flag for archived
                archived = "--archived" in sys.argv
                threads = await mgr.list_threads(channel_id, archived=archived, limit=20)
                print(f"📋 {len(threads)} threads em {channel_id} ({'archived' if archived else 'active'}):")
                for t in threads:
                    status_tags = [tag for tag in t.applied_tags if tag.startswith("status:")]
                    print(f"  - {t.name} (ID: {t.id}) [{', '.join(status_tags) or 'sem status'}]")
            
            elif cmd == "create-thread" and len(sys.argv) >= 5:
                channel_id = sys.argv[2]
                title = sys.argv[3]
                content = sys.argv[4]
                await mgr.get_available_tags(channel_id)
                thread = await mgr.create_thread(channel_id, title, content)
                print(f"✅ Thread criada: {thread.id}")
            
            else:
                print("Comando inválido")
    
    asyncio.run(main())