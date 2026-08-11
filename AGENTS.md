# AGENTS.md — Multi-Agent Entry Point (Codex, opencode, Cursor, Gemini CLI, Claude Code)

This repository is a skills library for **Abaqus secondary development**: generating
production-quality Abaqus Python scripts (CAE automation) and Fortran user subroutines,
then running, diagnosing and verifying simulations — end to end.

## How to use this library

1. **Start here**: read `abaqus_agent_playbook.md` for the full execution loop
   (clarify → generate → run headless → diagnose → iterate → verify → report).
2. **For Python scripting** (model building, mesh, loads, job, post-processing):
   - Entry: `abaqus_scriptcontrol_skills/general/SKILL.md`
   - Reference templates: `abaqus_scriptcontrol_skills/general/reference/*.md`
   - Specialized: `static/`, `fatigue/`, `thermal/`, `xfem/`, `composite/` under
     `abaqus_scriptcontrol_skills/`
3. **For Fortran subroutines** (UMAT, DLOAD, DFLUX, ...):
   - Entry: `abaqus_subroutine_skills/SKILL.md`
   - Templates: `abaqus_subroutine_skills/reference/**/*.md`
4. **When running analyses** (not just writing scripts) the agent loop is mandatory.

## Skills install (repo-level, recommended for Codex/Gemini/opencode)

```bash
mkdir -p .agents/skills
git clone https://github.com/jasonanewcoder/abaqus_skills.git .agents/skills/abaqus_skills
```

User-level install for Codex: `~/.agents/skills/abaqus_skills`
Claude Code: `~/.claude/skills/abaqus_skills` — see `docs/agent_installation.md`.

## Non-negotiable rules

| Rule | Detail |
|------|--------|
| Unit system | N-mm-MPa ONLY (mm, N, MPa, tonne/mm³, 9800 mm/s²) |
| Python target | Abaqus 2023+ / Python 3.9+; NO Python 2.7 syntax |
| Fortran | Fixed format, `REAL*8`, `ABA_PARAM.INC`/`vaba_param.inc`, `1.0D0` |
| Field output | Do NOT request 'MISES' in FieldOutputRequest (compute in post) |
| API fidelity | Copy from `reference/`; check `docs/ERRATA.md` for unverified items |
| Verification | Every completed analysis gets benchmark/energy/mesh checks |

## Quick file map

```
abaqus_agent_playbook.md            ← agent orchestration (read first for full tasks)
CLAUDE.md                           ← full project identity + standards
docs/ERRATA.md                      ← fixed bugs + unverified API items
docs/agent_installation.md          ← install per agent tool
scripts/                            ← executable helpers (unit_converter, inp_checker,
                                       odb_extract, job_monitor)
abaqus_scriptcontrol_skills/        ← Python skills (general + static/fatigue/thermal/xfem/composite)
abaqus_subroutine_skills/           ← Fortran subroutine skills + official examples
cross_module_examples/              ← end-to-end Python+Fortran example tasks
```

## Tools you can call

| Tool | When | How |
|------|------|-----|
| `scripts/unit_converter.py` | any unit doubt | `python3 scripts/unit_converter.py --to-abaqus density 7850` |
| `scripts/inp_checker.py` | before submitting | `python3 scripts/inp_checker.py Job-1.inp` |
| `scripts/odb_extract.py` | after a job | `abaqus python scripts/odb_extract.py Job-1.odb --field U --max` |
| `scripts/job_monitor.sh` | submit + monitor | `scripts/job_monitor.sh Job-1 cpus=4` |
