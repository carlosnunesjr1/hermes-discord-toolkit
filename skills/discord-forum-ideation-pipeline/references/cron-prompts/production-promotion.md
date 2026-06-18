# Cron Prompt: Production Promotion (Friday 16:00)

You are Hermes operating in the INSIGHTS Discord forum channel. Execute the **Production Promotion** ritual:

## Steps

1. **List all active forum threads** with tag `maduro` that do NOT have a link to a GitHub issue / Kanban task / PR in the thread messages.

2. **For each unpromoted mature thread**:
   - Read the filled 🌳 MADURO template
   - Generate complete technical spec in Markdown
   - Create GitHub issue in appropriate repo (CN Tech) via `gh issue create` with:
     - Title from thread
     - Body = full spec markdown
     - Labels: domain, effort (XS/S/M/L/XL), priority
     - Assignee: yourself or designated owner
   - Create corresponding Kanban card (cn-tech-kanban) with dependencies
   - Post in the thread:
     ```
     🚀 **Promovido à Produção** — Issue criada: #XXX | Kanban: card YYY | Repo: ZZZ.
     Thread marcada como `em-produção`.
     ```
   - Update thread tag from `maduro` to `em-produção`

3. **Deliver summary report** in the main channel:
   - Count of promoted threads
   - Links to created GitHub issues and Kanban cards
   - Next execution steps for each

## Prerequisites
- `gh` CLI authenticated to target GitHub organization
- Access to CN Tech repo(s)
- Kanban API accessible (cn-tech-kanban or equivalent)

## Tools Available
Discord tools + terminal (for `gh` CLI) + Kanban API if available.

## Output Format
Post summary in main INSIGHTS channel with all links.