# Agent Installation Guide — Install the Abaqus Skills in Any Agent Tool

The Abaqus skills follow the **open Agent Skills standard** (https://agentskills.io),
so the same repository works across Claude Code, OpenAI Codex, opencode, Gemini CLI,
Cursor, and other skill-compatible agents. Choose your tool below.

## 1. Claude Code (Anthropic)

```bash
# One-liner (recommended)
npx skills add jasonanewcoder/abaqus_skills

# Or git clone
git clone https://github.com/jasonanewcoder/abaqus_skills.git ~/.claude/skills/abaqus_skills

# Or download ZIP to ~/.claude/skills/
```

## 2. OpenAI Codex

Codex scans skills from `$REPO_ROOT/.agents/skills` and `$HOME/.agents/skills`:

```bash
# User-level (available in every repository)
git clone https://github.com/jasonanewcoder/abaqus_skills.git ~/.agents/skills/abaqus_skills

# Repository-level (checked into a project so the whole team gets it)
mkdir -p .agents/skills
git clone https://github.com/jasonanewcoder/abaqus_skills.git .agents/skills/abaqus_skills
```

Restart Codex after installing (skills are discovered at startup).

## 3. opencode

```bash
git clone https://github.com/jasonanewcoder/abaqus_skills.git ~/.config/opencode/skills/abaqus_skills
```

## 4. Gemini CLI

```bash
git clone https://github.com/jasonanewcoder/abaqus_skills.git ~/.gemini/skills/abaqus_skills
```

## 5. Cursor / VS Code (Copilot) — Agent Skills

Follow the editor's Agent Skills instructions (skills directory), or use the
`.agents/skills` repo-level location where supported.

## 6. Universal (repo-level, all tools)

```bash
mkdir -p .agents/skills
git clone https://github.com/jasonanewcoder/abaqus_skills.git .agents/skills/abaqus_skills
```

Any skill-compatible agent that scans `.agents/skills` will pick it up.

## Verify the installation

```bash
ls <skill-dir>/abaqus_skills/abaqus_scriptcontrol_skills/general/SKILL.md
ls <skill-dir>/abaqus_skills/abaqus_subroutine_skills/SKILL.md
```

Then ask your agent: "使用 Abaqus 做一根悬臂梁的静力分析" (or in English:
"Run a static cantilever beam analysis in Abaqus") — it should load the general skill
and follow the playbook.

## Updating

```bash
cd <skill-dir>/abaqus_skills && git pull
```

## Notes

- The skills are **progressive disclosure**: agents load only `SKILL.md` first, then
  the `reference/` files they need — keeping context small.
- Trigger matching uses each skill's `description` (front-loaded with keywords).
- Some agents (e.g. Codex) may shorten long descriptions when many skills are
  installed — the descriptions are written with the key triggers first.
