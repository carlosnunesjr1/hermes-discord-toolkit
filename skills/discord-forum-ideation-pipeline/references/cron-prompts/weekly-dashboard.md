# Cron Prompt: Weekly Dashboard (Sunday 20:00)

You are Hermes operating in the INSIGHTS Discord forum channel. Execute the **Weekly Dashboard** ritual:

## Steps

1. **Collect metrics for the week (Mon-Sun)**:
   - New `semente` threads created
   - Threads promoted `semente` → `brotando`
   - Threads promoted `brotando` → `maduro`
   - Threads promoted `maduro` → `em-produção` (with GitHub/Kanban links)
   - Threads pruned `podado` (with/without lesson recorded)
   - Threads `em-produção` closed (done)
   - Median lead time: creation → `em-produção` (days)
   - Germination rate, Flowering rate, Harvest rate, Conscious Prune rate

2. **Generate formatted Markdown report** for Discord:
   ```
   ## 📊 INSIGHTS — Resumo Semanal (DD/MM–DD/MM)
   
   ### 🌱 Novas Sementes: X
   - [link] Título — domínio
   ...
   
   ### 🌿 Promovidas a Brotando: Y
   ...
   
   ### 🌳 Promovidas a Maduro: Z
   ...
   
   ### 🚀 Entregues à Produção: W
   - #issue Título — repo — Kanban card
   ...
   
   ### ✂️ Podadas: K (L com lição, M sem lição ⚠️)
   ...
   
   ### 📈 KPIs da Semana
   - Germinação: X% (target ≥60%)
   - Floração: Y% (target ≥40%)
   - Colheita: Z% (target ≥90%)
   - Poda Consciente: L% (target 100%)
   - Lead Time Mediano: N dias (target ≤30)
   
   ### ⚠️ Alertas
   - [Se algum KPI fora do target]
   - [Sementes >14d sem movimento]
   - [Brotando >21d sem decisão]
   - [Maduro >7d sem promoção]
   
   ### 🎯 Foco da Próxima Semana
   - [Top 3 ações recomendadas baseadas nos dados]
   ```

3. **Post in main INSIGHTS channel** AND save to Obsidian:
   `03-Resources/Insights/weekly/YYYY-WW-summary.md`

## Tools Available
Discord tools for reading threads, terminal for file write to Obsidian vault.

## Output Format
Discord message + Obsidian file.