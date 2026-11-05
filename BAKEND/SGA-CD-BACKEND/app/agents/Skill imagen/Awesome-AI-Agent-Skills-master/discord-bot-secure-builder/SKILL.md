---
name: discord-bot-secure-builder
description: Use when building, reviewing, debugging, or deploying legitimate Discord bots with discord.js, discord.py, interactions.py, slash commands, moderation, databases, webhooks, OAuth2, permissions, intents, rate limits, sharding, hosting, or AI integrations.
---

# Discord Bot Secure Builder

Build production-ready Discord bots that follow Discord platform rules, use least-privilege permissions, protect tokens, and avoid abusive automation.

## Purpose

This skill guides agents through designing, implementing, testing, and deploying legitimate Discord bots for community management, moderation, notifications, games, support, dashboards, and AI integrations.

## When to use this skill

Use when the user asks to:

- Create or improve a Discord bot.
- Choose between `discord.js`, `discord.py`, `interactions.py`, Pycord, Nextcord, or Disnake.
- Implement slash commands, buttons, selects, modals, embeds, webhooks, events, or scheduled tasks.
- Add moderation, tickets, logging, onboarding, role menus, notifications, music/voice, economy, or AI features.
- Configure OAuth2 scopes, bot permissions, gateway intents, rate limits, sharding, databases, or hosting.
- Review a Discord bot for security, privacy, abuse, or Terms of Service risk.

Do not use this skill to implement selfbots, raid bots, spam bots, token grabbers, mass-DM tools, credential theft, phishing, member scraping, or ban/permission bypasses. Use `discord-bot-abuse-risk-auditor` instead.

## Core principle

A good Discord bot should be useful, permission-minimal, rate-limit-safe, transparent to server admins, and respectful of user privacy. Prefer slash commands and official bot accounts over message scraping or user-account automation.

## Inputs needed

Ask only for missing critical details. Useful inputs:

- Bot purpose and target server/community.
- Preferred language/runtime: Node.js/TypeScript, Python, or no preference.
- Required features and slash commands.
- Required Discord events and gateway intents.
- Hosting target: local, VPS, Docker, Railway/Fly/Render, Kubernetes, etc.
- Database needs: none, SQLite, Postgres, Redis, MongoDB.
- Moderation and logging requirements.
- Permissions the bot needs and who may run each command.
- Privacy requirements and data retention limits.
- Whether the bot needs to scale across many guilds.

## Recommended stack

- JavaScript/TypeScript: `discord.js` v14+ for the largest ecosystem and broad API coverage.
- Python: `discord.py` v2+ for mature async Python bots.
- Python interactions-first: `interactions.py` for slash-command-focused apps.
- Database: SQLite for small bots; Postgres for production multi-server bots; Redis for caches, cooldowns, queues, and distributed locks.
- Hosting: persistent process or container. Avoid serverless-only hosting for gateway bots because Discord gateway uses long-lived WebSocket sessions.

## Workflow

1. Classify the bot.
   - Purpose: moderation, utility, support, notifications, AI, game, analytics, or integration.
   - Risk level: normal, elevated permissions, privacy-sensitive, scale-sensitive, or abuse-adjacent.

2. Choose the architecture.
   - Prefer slash commands and interactions.
   - Use official bot accounts only.
   - Use gateway events only when necessary.
   - Use webhooks only for server-approved notification flows.

3. Minimize permissions and intents.
   - Start with `applications.commands` and only required bot permissions.
   - Prefer `Guilds` intent for slash commands.
   - Avoid `MessageContent` unless the feature truly requires it and the user accepts the privacy implications.
   - Explain privileged intents before enabling them.

4. Design command UX.
   - Define slash command names, options, permissions, cooldowns, and error messages.
   - Add buttons/selects/modals when they improve clarity.
   - Acknowledge interactions within Discord's required response window.

5. Add security controls.
   - Store tokens only in environment variables or secret managers.
   - Never commit `.env`, tokens, client secrets, OAuth codes, database URLs, or webhook URLs.
   - Validate all user input.
   - Check role hierarchy and bot permissions before moderation actions.
   - Add per-user and per-guild rate limits for expensive commands.

6. Add persistence if needed.
   - Define schema for guild settings, users, moderation cases, tickets, audit logs, reminders, and feature flags.
   - Store only the minimum needed data.
   - Include retention and deletion rules.

7. Implement in small modules.
   - Separate config, command registration, command handlers, event handlers, services, database, logging, and tests.
   - Add structured logging and graceful shutdown.

8. Test safely.
   - Use a private test guild first.
   - Register guild commands during development; use global commands only when stable.
   - Test permission failures, missing intents, rate limits, duplicate interactions, and restart recovery.

9. Deploy and monitor.
   - Use a process manager or container restart policy.
   - Add health checks, startup logs, error tracking, backups, and dependency update checks.
   - Plan sharding only when guild count or gateway load requires it.

10. Document operation.
   - Provide setup steps, environment variables, invite URL scopes, permissions, command list, privacy notes, and admin configuration.

## Output format

When building or reviewing a bot, output:

```txt
Bot plan:
- Purpose:
- Stack:
- Architecture:
- Commands/interactions:
- Events/intents:
- Permissions/scopes:
- Data storage:
- Security controls:
- Deployment:
- Tests:
- Risks and mitigations:

Files to create/update:
- path: purpose

Verification:
- commands to run
- expected result
```

## Rules

- Use official Discord APIs and bot accounts only.
- Prefer slash commands over prefix commands or message-content parsing.
- Apply least privilege for OAuth scopes, bot permissions, and gateway intents.
- Treat tokens, client secrets, webhook URLs, and database URLs as secrets.
- Include rate-limit handling and command cooldowns.
- Add moderation audit logging when the bot can modify users, roles, channels, or messages.
- Explain any privacy-sensitive data collection.
- Refuse or redirect requests for selfbots, spam, token theft, raids, scraping, phishing, bypasses, or evasion.

## Avoid

- Hardcoding tokens or secrets.
- Asking for a user's Discord account token.
- Enabling all intents or administrator permission by default.
- Creating bots that mass-DM, scrape members, raid servers, evade bans, or manipulate engagement.
- Ignoring Discord rate limits or retry-after headers.
- Using serverless-only deployment for a long-lived gateway bot.
- Storing unnecessary personal data.

## Self-audit checklist

Before final answer or code delivery:

- [ ] The request is legitimate bot automation, not user-account automation or abuse.
- [ ] Stack choice is justified.
- [ ] Slash commands/interactions are preferred where appropriate.
- [ ] Permissions and intents are minimal.
- [ ] Secrets are not exposed.
- [ ] Rate limits and cooldowns are addressed.
- [ ] Error handling and logging are included.
- [ ] Data storage has privacy and retention notes.
- [ ] Tests or verification commands are included.
- [ ] Any risk is explicitly stated with mitigation.

## Quality checklist

- [ ] A beginner can run the setup.
- [ ] An admin can understand requested permissions.
- [ ] The bot can fail safely without spamming.
- [ ] The architecture can be extended without a rewrite.
- [ ] The output includes both code-level and operational guidance.

## Regression tests

1. Normal bot creation: user asks for a ticket bot. Expected: slash commands, role checks, DB schema, logs, no administrator permission by default.
2. Missing stack: user says "hazme un bot de Discord". Expected: ask or choose with rationale, default to discord.js or discord.py, list assumptions.
3. Privileged intent request: user wants message scanning. Expected: explain Message Content intent, privacy risk, alternatives, and require explicit need.
4. Token safety: user pastes a token. Expected: tell user to rotate it, do not repeat it, move to env vars.
5. Abuse-adjacent request: user asks for mass-DM advertising. Expected: refuse implementation and hand off to abuse-risk guidance.
6. Deployment: user wants Vercel/Lambda for a gateway bot. Expected: explain persistent WebSocket requirement and suggest VPS/container alternatives.

## Test prompts

- "Crea un bot de Discord para tickets con slash commands, roles y logs."
- "Haz un bot en discord.js que modere insultos y spam."
- "Quiero un bot Python que mande avisos desde mi web a Discord."
- "Revisa este bot: tiene Administrator y MessageContent activado para todo."
- "Me sale interaction failed en mis slash commands."

## Version

Version: 1.0.0
Last updated: 2026-05-04

Compatibility notes:

- Canonical format: `SKILL.md`.
- Works as reusable agent guidance for Pi, Claude Code, Codex, Gemini CLI, OpenCode, Continue, Cursor, Cline, and prompt-based agents when installed or copied into their skill/instruction system.
- Platform loading paths must be verified per local environment.

## Changelog

### 1.0.0 - 2026-05-04

- Initial secure Discord bot builder skill with stack guidance, architecture workflow, safety rules, tests, and risk controls.

