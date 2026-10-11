# Ponytail Skill

**Ponytail** - "Lazy senior dev mode for any coding task (write, refactor, fix, review): YAGNI, stdlib first, no unrequested abstractions. Not for non-coding requests."

## Overview

Ponytail is a skill/plugin for AI coding agents that enforces a "lazy senior developer" mindset. It reduces over-engineering by:
- **~54% less code** (up to 94% reduction)
- **~20% cheaper** (fewer tokens)
- **~27% faster**
- **100% safe** (benchmarked on real repos)

## Core Philosophy

> "He says nothing. He writes one line. It works."

- **YAGNI** - You Aren't Gonna Need It
- **Stdlib first** - Use what the platform/language already provides
- **Native over dependencies** - Prefer built-in features over npm/pip packages
- **No unrequested abstractions** - Don't add factories, interfaces, or layers unless asked

## Commands

| Command | Description |
|---------|-------------|
| `/ponytail [lite \| full \| ultra \| off]` | Set intensity level or turn off. No argument toggles on/off or shows current level. |
| `/ponytail-review` | Review current diff for over-engineering, returns a delete-list. Target: `uncommitted`, `staged`, `branch`, or PR link. |
| `/ponytail-audit` | Audit entire repo for over-engineering (not just diff). |
| `/ponytail-debt` | Harvest `ponytail:` shortcut comments into a tracked ledger. |
| `/ponytail-gain` | Show measured impact scoreboard (less code, less cost, more speed). |
| `/ponytail-help` | Quick reference for all commands. |

## Intensity Levels

- **lite** - Build what's asked, name the lazier alternative in one line
- **full** (default) - YAGNI → stdlib → native → one-liner → minimum
- **ultra** - Deletion before addition, challenges the requirement before building
- **off** - Disabled

## Installation

Available for 20+ agents including:
- Claude Code (via GitHub or npm `@dietrichgebert/ponytail`)
- OpenCode
- OpenClaw/ClawHub
- VS Code extensions
- And more...

## Benchmarks

Tested on real FastAPI + React repo (tiangolo/full-stack-fastapi-template):
- 12 feature tasks
- Haiku 4.5 model
- n=4 runs per task
- Measures: LOC reduction, correctness, safety

## Examples

See [examples/](https://github.com/DietrichGebert/ponytail/tree/main/examples) for before/after comparisons:
- Email Validation: 75 → 3 LOC
- Debounce: 116 → 10 LOC
- CSV Sum: 20 → 3 LOC
- React Countdown: 267 → 9 LOC
- Rate Limiting: 128 → 10 LOC

## License

MIT License - Copyright (c) 2026 DietrichGebert

## Repository

- GitHub: https://github.com/DietrichGebert/ponytail
- Website: https://ponytail.dev
- npm: `@dietrichgebert/ponytail`

## File Reference
- Skill file: `/home/jeni/.agents/skills/ponytail/SKILL.md`