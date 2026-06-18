#!/usr/bin/env python3
"""
Setup Tags - Cria todas as tags necessárias nos canais de fórum da Incubadora.
Execute após criar os canais de fórum no Discord.
"""

import os
import asyncio
import aiohttp

# Tags necessárias por categoria
REQUIRED_TAGS = {
    "status": [
        ("capturada", "📥", False),
        ("em-debate", "💬", False),
        ("validando", "⚗️", False),
        ("aprovada", "✅", False),
        ("arquivada", "📦", False),
        ("feita", "🎉", False),
    ],
    "prioridade": [
        ("P1-urgente", "🔴", True),
        ("P2-alta", "🟠", True),
        ("P3-normal", "🟡", True),
        ("P4-baixa", "🟢", True),
        ("P5-backlog", "⚪", True),
    ],
    "tipo": [
        ("feature", "✨", False),
        ("bug", "🐛", False),
        ("tech-debt", "🔧", False),
        ("pesquisa", "🔬", False),
        ("processo", "📋", False),
        ("infra", "☁️", False),
    ],
    "esforco": [
        ("XS", "⚡", False),
        ("S", "🟢", False),
        ("M", "🟡", False),
        ("L", "🟠", False),
        ("XL", "🔴", False),
        ("desconhecido", "❓", False),
    ],
    "dominio": [
        ("career", "💼", False),
        ("pim", "📦", False),
        ("router", "🔀", False),
        ("infra", "☁️", False),
        ("hermes", "🤖", False),
        ("geral", "📌", False),
    ],
}

async def create_tags_in_channel(bot_token: str, channel_id: str, category_name: str):
    """Cria tags de uma categoria em um canal de fórum."""
    url = f"https://discord.com/api/v10/channels/{channel_id}"
    headers = {"Authorization": f"Bot {bot_token}", "Content-Type": "application/json"}
    
    # Obter tags atuais
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"  ❌ Erro ao obter canal: {resp.status}")
                return
            channel = await resp.json()
        
        existing_tags = {t["name"]: t["id"] for t in channel.get("available_tags", [])}
        tags_to_create = []
        
        for name, emoji, moderated in REQUIRED_TAGS[category_name]:
            if name not in existing_tags:
                tags_to_create.append({
                    "name": name,
                    "emoji_name": emoji,
                    "moderated": moderated,
                })
        
        if not tags_to_create:
            print(f"  ✅ {category_name}: todas as tags já existem")
            return
        
        # Discord API: update channel with new tags
        all_tags = channel.get("available_tags", []) + tags_to_create
        payload = {"available_tags": all_tags}
        
        async with session.patch(url, json=payload) as resp:
            if resp.status == 200:
                print(f"  ✅ {category_name}: {len(tags_to_create)} tags criadas")
            else:
                text = await resp.text()
                print(f"  ❌ {category_name}: erro {resp.status} - {text}")

async def main():
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    guild_id = os.getenv("DISCORD_GUILD_ID", "1516397584942370836")
    
    if not bot_token:
        print("❌ DISCORD_BOT_TOKEN não configurado")
        return
    
    # Canais de fórum da incubadora (preencher com IDs reais)
    forum_channels = {
        "ideias-brutas": "1516843053334265916",  # insigths - atualizar com ID real
        "em-analise": "",
        "experimentos": "",
        "prontas-para-producao": "",
        "arquivadas": "",
        "templates": "",
    }
    
    print("🏷️  CONFIGURANDO TAGS DA INCUBADORA")
    print("=" * 50)
    
    for name, channel_id in forum_channels.items():
        if not channel_id:
            print(f"\n⏭️  {name}: ID não configurado (pular)")
            continue
        
        print(f"\n📁 Canal: {name} ({channel_id})")
        for category in REQUIRED_TAGS:
            await create_tags_in_channel(bot_token, channel_id, category)
            await asyncio.sleep(0.5)  # Rate limit
    
    print("\n✅ Configuração de tags concluída!")
    print("\nPróximos passos:")
    print("1. Preencher IDs dos canais não configurados")
    print("2. Executar novamente para canais restantes")
    print("3. Verificar no Discord: Canal → Gerenciar Tags")

if __name__ == "__main__":
    asyncio.run(main())