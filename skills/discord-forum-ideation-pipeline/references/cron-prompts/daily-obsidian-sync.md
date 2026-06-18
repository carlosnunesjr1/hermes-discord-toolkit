# Cron Prompt: Daily Obsidian Sync (Daily 06:00)

You are Hermes operating in the INSIGHTS Discord forum channel. Execute the **Daily Obsidian Sync** ritual:

## Steps

1. **List all forum threads** with changes in the last 24 hours (use last message timestamp).

2. **For each changed thread, export to Obsidian by stage**:

   **`semente`** → `00-Inbox/YYYY-MM-DD-seed-{slug}.md`
   - Content: filled 🌱 template + Discord thread link

   **`brotando`** → `01-Projects/{slug}/wip.md`
   - Content: filled 🌿 template + discussion summary + research links

   **`maduro`** → `01-Projects/{slug}/spec.md` + `tasks.md`
   - Content: filled 🌳 template (spec.md) + task breakdown (tasks.md)

   **`podado`** → `04-Archive/{slug}-lesson.md`
   - Content: filled ✂️ template + lesson

   **`em-produção`** → `01-Projects/{slug}/production.md`
   - Content: GitHub/Kanban links + current status

3. **Update master index**: `🤖 Hermes/forum-index.md` with:
   - Master table: Thread | Stage | Domain | Last Updated | Discord Link | Obsidian Link
   - Sections by stage with counters
   - Most-used tags

4. **Commit & push** to Vault git repo (if configured) or save locally.

5. **Deliver summary** in main channel:
   ```
   🔄 Sync Diário — X threads sincronizadas | Y novas | Z promovidas | Índice atualizado: [[🤖 Hermes/forum-index]]
   ```

## Prerequisites
- Vault Brain OS mounted at `/opt/obsidian/` or configured path
- Write access to vault directories

## Tools Available
Discord tools + terminal (file operations)

## Output Format
Discord summary message + Obsidian files created/updated.