# Contributing

1. Fork and clone the repo
2. Edit `generate-image/SKILL.md` — this is where all the skill logic lives
3. Test by installing locally: `./install.sh --link`
4. Open a PR with a clear description of what changed and why

## Adding a new provider

Add a new API reference section to `generate-image/SKILL.md` following the pattern of the existing OpenAI and Gemini sections. The agent handles everything from there.

## Guidelines

- Keep SKILL.md concise — the agent is smart, it doesn't need verbose instructions
- Test with both Claude Code and Copilot CLI if possible
- Don't add wrapper scripts unless absolutely necessary — let the agent do the work
