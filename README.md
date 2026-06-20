# Agent Operator Skills

Sanitized, reusable skills for AI coding and operator workflows.

This repository is intentionally curated. It includes skills that are useful outside a private company or personal setup, and excludes account-specific, product-specific, and third-party/vendor skills.

This is not an official OpenAI, Anthropic, Vercel, GitHub, or platform-owned repository.

## Included Skills

| Skill | Purpose |
| --- | --- |
| `codex-improvement-loop` | Coordinate large multi-step coding initiatives with scoped workers, reviewers, loop state, and verification gates. |
| `honest-output-auditor` | Audit high-stakes outputs before calling them done. |
| `changelog-generator` | Turn git history into user-facing changelogs and release notes. |
| `cli-creator` | Build small, composable CLIs from APIs, scripts, docs, or admin workflows. |
| `define-goal` | Convert fuzzy intentions into concrete, measurable agent goals. |
| `seo-audit` | Run and interpret technical SEO audits for websites and local previews. |
| `security-best-practices` | Apply framework-specific secure-coding guidance for Python, JavaScript/TypeScript, Go, React, Next.js, Express, Django, Flask, FastAPI, Vue, and jQuery projects. |
| `security-threat-model` | Produce repo-grounded AppSec threat models with evidence anchors and abuse paths. |
| `security-ownership-map` | Analyze git history to identify security ownership risk, bus factor, and sensitive-code stewardship gaps. |

## Why One Repo

One curated repo is easier to audit, install, version, and explain than many tiny repos. A skill can be split into its own repository later if it becomes a standalone project with tests, examples, or a user community.

## Installation

Copy a skill folder into your agent's skills directory.

For Codex-style local skills:

```bash
cp -R skills/codex-improvement-loop ~/.codex/skills/
```

For tools that use the open skills layout, copy the same folder into that tool's expected skill directory.

## Privacy And Provenance

The public skills in this repo were sanitized before publication:

- no personal names
- no personal email addresses
- no local home-directory paths
- no private product names
- no customer or prospect data
- no secrets, tokens, cookies, or API keys
- no private repository paths
- no personal admin workflow skills

See `SANITIZATION_AUDIT.md` for what was included, excluded, and checked.
See `PROVENANCE.md` for the publication and authorship notes.

## License

Apache-2.0. See `LICENSE`.
